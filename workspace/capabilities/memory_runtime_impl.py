# capability_name: memory_runtime_impl
"""Workspace-owned memory core implementation executed in main runtime namespace."""

class MemoryCore:
    """
    SQLite 持久记忆，与 openclaw_main.py 共用同一个 DB，数据互通。
    每次调用都创建独立连接（check_same_thread=False），解决跨线程问题。
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._lock   = threading.Lock()
        self._init_db()

    _EMBEDDING_DIM = 384
    _VECTOR_EVENT_TYPES = frozenset({
        "learning",
        "autonomous_thought",
        "long_term_memory",
        "user_mission_started",
        "user_mission_finished",
        "self_identity_updated",
        "skill_insight",
        "conversation_digestion",
        "external_audit",
    })

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id         TEXT PRIMARY KEY,
                        event_type TEXT,
                        content    TEXT,
                        importance REAL DEFAULT 0.5,
                        timestamp  TEXT,
                        tags       TEXT
                    )
                """)
                # 知识图谱三元组表（对标 Neo4j 的 Subject→Relation→Object 结构）
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_triples (
                        id        TEXT PRIMARY KEY,
                        subject   TEXT,
                        relation  TEXT,
                        object    TEXT,
                        source    TEXT,
                        timestamp TEXT
                    )
                """)
                # 技能执行结果全量表（解决子进程数据消失问题）
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS skill_results (
                        id               TEXT PRIMARY KEY,
                        skill_name       TEXT NOT NULL,
                        input_args       TEXT,
                        result_json      TEXT,
                        result_summary   TEXT,
                        timestamp        TEXT,
                        execution_time_ms REAL
                    )
                """)
                # 兼容旧库：运行时迁移，若缺少 execution_time_ms 列则补加
                try:
                    conn.execute("ALTER TABLE skill_results ADD COLUMN execution_time_ms REAL")
                    conn.commit()
                except Exception:
                    pass  # 列已存在，忽略
                # skill_results 查询索引（skill_name + timestamp 复合，加速 query_skill_results）
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_skill_results_name_ts "
                    "ON skill_results(skill_name, timestamp DESC)"
                )
                # memories 表 importance+timestamp 复合索引（加速按重要性排序的 recall）
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memories_imp_ts "
                    "ON memories(importance DESC, timestamp DESC)"
                )
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_embeddings (
                        memory_id      TEXT PRIMARY KEY,
                        source_type    TEXT,
                        content_text   TEXT,
                        embedding_json TEXT,
                        timestamp      TEXT,
                        embedding_source TEXT,
                        importance     REAL DEFAULT 0.5
                    )
                """)
                try:
                    conn.execute("ALTER TABLE memory_embeddings ADD COLUMN embedding_source TEXT")
                    conn.commit()
                except Exception:
                    pass
                try:
                    conn.execute("ALTER TABLE memory_embeddings ADD COLUMN importance REAL DEFAULT 0.5")
                    conn.commit()
                except Exception:
                    pass
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memory_embeddings_ts "
                    "ON memory_embeddings(timestamp DESC)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_memory_embeddings_imp_ts "
                    "ON memory_embeddings(importance DESC, timestamp DESC)"
                )
                # 已结案议题注册表：防止同一幻像问题被心跳循环反复触发
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settled_topics (
                        id         TEXT PRIMARY KEY,
                        topic_key  TEXT NOT NULL,
                        conclusion TEXT,
                        settled_at TEXT,
                        ttl_days   INTEGER DEFAULT 7
                    )
                """)
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_settled_topics_key "
                    "ON settled_topics(topic_key)"
                )
                conn.commit()
            finally:
                conn.close()

    def _serialize_content_text(self, event_type: str, content) -> str:
        if isinstance(content, str):
            text = content
        elif isinstance(content, dict):
            preferred_fields = [
                "topic", "reason", "summary", "reflection", "knowledge",
                "fact", "mission", "user_input", "ai_reply", "preview",
                "field", "event_content", "description",
            ]
            parts = []
            for field in preferred_fields:
                value = content.get(field)
                if value:
                    parts.append(f"{field}: {value}")
            if not parts:
                parts.append(json.dumps(content, ensure_ascii=False, sort_keys=True))
            text = "\n".join(str(part) for part in parts)
        else:
            text = str(content)
        text = re.sub(r"\s+", " ", text).strip()
        return f"[{event_type}] {text[:1200]}" if text else ""

    def _memory_snippet(self, content) -> str:
        if isinstance(content, dict):
            for key in ("summary", "reflection", "knowledge", "fact", "digestion", "topic", "reason", "preview"):
                value = content.get(key)
                if value:
                    return str(value)[:120]
            return json.dumps(content, ensure_ascii=False)[:120]
        return str(content)[:120]

    def _tokenize_for_embedding(self, text: str) -> list:
        lowered = text.lower().strip()
        if not lowered:
            return []
        latin_tokens = re.findall(r"[\w\-\.]+", lowered)
        compact = re.sub(r"\s+", "", lowered)
        cjk_chars = [ch for ch in compact if "\u4e00" <= ch <= "\u9fff"]
        cjk_bigrams = ["".join(cjk_chars[i:i + 2]) for i in range(max(0, len(cjk_chars) - 1))]
        return latin_tokens + cjk_chars + cjk_bigrams

    def _embed_text_hash_fallback(self, text: str) -> list:
        tokens = self._tokenize_for_embedding(text)
        if not tokens:
            return []

        vec = [0.0] * self._EMBEDDING_DIM
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._EMBEDDING_DIM
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + (digest[5] / 255.0) * 0.25
            vec[index] += sign * weight

        norm = math.sqrt(sum(value * value for value in vec))
        if norm <= 1e-9:
            return []
        return [round(value / norm, 6) for value in vec]

    def _embed_text(self, text: str) -> tuple[str, list]:
        model = _get_sentence_transformer_model()
        if model is not None:
            try:
                vector = model.encode([text], normalize_embeddings=True, show_progress_bar=False)[0]
                values = vector.tolist() if hasattr(vector, "tolist") else list(vector)
                return f"st::{_embedding_model_name}", [round(float(value), 6) for value in values]
            except Exception:
                pass

        return "hash::v2", self._embed_text_hash_fallback(text)

    def _cosine_similarity(self, left: list, right: list) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        return float(sum(a * b for a, b in zip(left, right)))

    def _should_store_embedding(self, event_type: str, content) -> bool:
        if event_type not in self._VECTOR_EVENT_TYPES:
            return False
        text = self._serialize_content_text(event_type, content)
        return len(text) >= 12

    def _store_embedding(self, conn, memory_id: str, event_type: str, content, timestamp: str):
        if not self._should_store_embedding(event_type, content):
            return
        text = self._serialize_content_text(event_type, content)
        embedding_source, embedding = self._embed_text(text)
        if not embedding:
            return
        conn.execute(
            "INSERT OR REPLACE INTO memory_embeddings (memory_id, source_type, content_text, embedding_json, timestamp, embedding_source) VALUES (?,?,?,?,?,?)",
            (memory_id, event_type, text, json.dumps(embedding), timestamp, embedding_source)
        )

    def store(self, event_type: str, content, importance: float = 0.5, tags: Optional[list] = None):
        importance = max(0.0, min(1.0, float(importance)))  # 防止溢出
        with self._lock:
            conn = self._get_conn()
            try:
                record_id = f"{event_type}_{uuid.uuid4().hex[:8]}"
                timestamp = datetime.now().isoformat()
                conn.execute(
                    "INSERT OR IGNORE INTO memories (id,event_type,content,importance,timestamp,tags) VALUES (?,?,?,?,?,?)",
                    (
                        record_id,
                        event_type,
                        json.dumps(content, ensure_ascii=False) if not isinstance(content, str) else content,
                        importance,
                        timestamp,
                        json.dumps(tags or ["system", event_type]),
                    )
                )
                try:
                    self._store_embedding(conn, record_id, event_type, content, timestamp)
                except Exception:
                    pass
                # AGI Rebirth: 同步到 Neo4j
                try:
                    neo4j_bridge.store(event_type, content, importance, timestamp)
                except Exception:
                    pass
                conn.commit()
            finally:
                conn.close()

    def store_triple(self, subject: str, relation: str, obj: str, source: str = ""):
        """存入知识三元组，格式与 Neo4j GraphMemory 对齐：Subject→Relation→Object"""
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO knowledge_triples VALUES (?,?,?,?,?,?)",
                    (
                        f"triple_{uuid.uuid4().hex[:8]}",
                        subject.strip()[:120],
                        relation.strip()[:80],
                        obj.strip()[:200],
                        source[:100],
                        datetime.now().isoformat(),
                    )
                )
                conn.commit()
                # AGI Rebirth: 同步到 Neo4j 知识图谱
                try:
                    neo4j_bridge.store_triple(subject, relation, obj, source)
                except Exception:
                    pass
            finally:
                conn.close()

    def recall_triples(self, keyword: str, limit: int = 8) -> list:
        """按关键词检索三元组（优先查本地 SQLite，如果开启了 Neo4j 则合并结果）"""
        kw = f"%{keyword.lower()}%"
        local_results = []
        with self._lock:
            conn = self._get_conn()
            try:
                rows = conn.execute(
                    "SELECT subject, relation, object, source, timestamp FROM knowledge_triples "
                    "WHERE lower(subject) LIKE ? OR lower(relation) LIKE ? OR lower(object) LIKE ? "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (kw, kw, kw, limit)
                ).fetchall()
                local_results = [{"subject": r[0], "relation": r[1], "object": r[2],
                                  "source": r[3], "timestamp": r[4]} for r in rows]
            finally:
                conn.close()
        
        # AGI Rebirth: 尝试从 Neo4j 补充深度图背景
        graph_results = neo4j_bridge.recall_graph(keyword, limit=limit)
        if graph_results:
            # 合并去重（简单逻辑）
            seen = { (r["subject"], r["relation"], r["object"]) for r in local_results }
            for gr in graph_results:
                key = (gr["source"], gr["relation"], gr["target"])
                if key not in seen:
                    local_results.append({
                        "subject": gr["source"],
                        "relation": gr["relation"],
                        "object": gr["target"],
                        "source": gr.get("origin", "neo4j"),
                        "timestamp": "graph_db"
                    })
        return local_results[:limit]

    # 不设置黑名单：AI 自行判断内容价值
    _RECALL_BLACKLIST: frozenset = frozenset()

    def recall(self, event_type: Optional[str] = None, limit: int = 10, days_back: int = 7) -> list:
        """按 importance DESC 排序返回记忆，过滤掉纯系统内务噪音。
        指定 event_type 时不过滤（精确查询场景）。
        """
        cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
        with self._lock:
            conn = self._get_conn()
            try:
                if event_type:
                    rows = conn.execute(
                        "SELECT id, event_type, content, importance, timestamp FROM memories "
                        "WHERE event_type=? AND timestamp>? "
                        "ORDER BY importance DESC, timestamp DESC LIMIT ?",
                        (event_type, cutoff, limit)
                    ).fetchall()
                else:
                    blist = list(self._RECALL_BLACKLIST)
                    if blist:
                        placeholders = ",".join("?" * len(blist))
                        rows = conn.execute(
                            f"SELECT id, event_type, content, importance, timestamp FROM memories "
                            f"WHERE timestamp>? AND event_type NOT IN ({placeholders}) "
                            f"ORDER BY importance DESC, timestamp DESC LIMIT ?",
                            [cutoff] + blist + [limit]
                        ).fetchall()
                    else:
                        rows = conn.execute(
                            "SELECT id, event_type, content, importance, timestamp FROM memories "
                            "WHERE timestamp>? ORDER BY importance DESC, timestamp DESC LIMIT ?",
                            (cutoff, limit)
                        ).fetchall()
            finally:
                conn.close()
        results = []
        for row in rows:
            try:
                content = json.loads(row[2])
            except Exception:
                content = row[2]
            results.append({
                "id":         row[0],
                "event_type": row[1],
                "content":    content,
                "importance": row[3],
                "timestamp":  row[4],
            })
        return results

    def recall_by_vector(self, query: str, limit: int = 8, days_back: int = 60) -> list:
        text = self._serialize_content_text("query", query)
        query_backend, query_embedding = self._embed_text(text)
        if not query_embedding:
            return []

        cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
        with self._lock:
            conn = self._get_conn()
            try:
                rows = conn.execute(
                    "SELECT m.id, m.event_type, m.content, m.importance, m.timestamp, e.content_text, e.embedding_json, e.embedding_source "
                    "FROM memories m JOIN memory_embeddings e ON e.memory_id = m.id "
                    "WHERE m.timestamp > ? AND coalesce(e.embedding_source, '') = ? "
                    "ORDER BY m.timestamp DESC LIMIT 400",
                    (cutoff, query_backend)
                ).fetchall()
            finally:
                conn.close()

        scored = []
        for row in rows:
            try:
                candidate_embedding = json.loads(row[6])
            except Exception:
                continue
            similarity = self._cosine_similarity(query_embedding, candidate_embedding)
            if similarity <= 0.12:
                continue
            try:
                content = json.loads(row[2])
            except Exception:
                content = row[2]
            fused_score = round(similarity * 0.85 + float(row[3]) * 0.15, 4)
            scored.append({
                "id": row[0],
                "event_type": row[1],
                "content": content,
                "importance": row[3],
                "timestamp": row[4],
                "vector_text": row[5],
                "embedding_source": row[7],
                "score": fused_score,
            })

        scored.sort(key=lambda item: (item["score"], item["timestamp"]), reverse=True)
        return scored[:max(1, limit)]

    def recall_hybrid(self, query: str, limit: int = 10, days_back: int = 120) -> list:
        q = (query or "").strip().lower()
        vector_hits = self.recall_by_vector(query, limit=max(limit, 6), days_back=days_back)
        all_records = self.recall(limit=80, days_back=days_back)

        merged = {}
        for item in vector_hits:
            merged[item["id"]] = {
                **item,
                "sources": ["vector"],
            }

        for record in all_records:
            haystack = json.dumps(record["content"], ensure_ascii=False).lower()
            if q and q not in haystack:
                continue
            snippet = self._memory_snippet(record["content"])
            if record["id"] in merged:
                merged[record["id"]]["sources"].append("keyword")
                merged[record["id"]]["score"] = round(merged[record["id"]]["score"] + 0.18, 4)
                continue
            merged[record["id"]] = {
                **record,
                "vector_text": snippet,
                "score": round(float(record["importance"]) * 0.55 + 0.25, 4),
                "sources": ["keyword"],
            }

        ranked = list(merged.values())
        ranked.sort(key=lambda item: (item.get("score", 0.0), item.get("importance", 0.0), item.get("timestamp", "")), reverse=True)
        return ranked[:max(1, limit)]

    def backfill_embeddings(self, limit: int = 120, days_back: int = 365) -> int:
        cutoff = (datetime.now() - timedelta(days=days_back)).isoformat()
        current_backend = _current_embedding_backend_name()
        with self._lock:
            conn = self._get_conn()
            try:
                rows = conn.execute(
                    "SELECT m.id, m.event_type, m.content, m.timestamp "
                    "FROM memories m LEFT JOIN memory_embeddings e ON e.memory_id = m.id "
                    "WHERE m.timestamp > ? AND (e.memory_id IS NULL OR coalesce(e.embedding_source, '') != ?) "
                    "ORDER BY m.importance DESC, m.timestamp DESC LIMIT ?",
                    (cutoff, current_backend, max(1, int(limit)))
                ).fetchall()
                inserted = 0
                for row in rows:
                    try:
                        content = json.loads(row[2])
                    except Exception:
                        content = row[2]
                    try:
                        self._store_embedding(conn, row[0], row[1], content, row[3])
                        inserted += 1
                    except Exception:
                        continue
                conn.commit()
                return inserted
            finally:
                conn.close()

    # ── 已结案议题注册表 ─────────────────────────────────────────────────────

    _SETTLED_DENY_SIGNALS: frozenset = frozenset({
        "不存在", "假设错误", "之前的假设是错误的", "并不存在",
        "未发现异常", "未发现问题", "已验证无问题", "无需修复",
        "实际上不存在", "调查结果：假设不成立", "结论：无",
        "no issue found", "assumption was wrong", "does not exist",
    })

    _SETTLED_STOP_WORDS: frozenset = frozenset({
        "的", "了", "是", "在", "有", "和", "与", "我", "它", "这", "那",
        "一个", "为", "对", "从", "被", "会", "已", "也", "或", "都",
        "问题", "发现", "系统", "当前", "需要", "进行",
    })

    def _extract_topic_keywords(self, text: str) -> List[str]:
        """从议题文本中提取2-4个核心名词关键词，用于已结案匹配。"""
        words = re.findall(r'[\u4e00-\u9fff]{2,8}|[a-zA-Z]{4,20}', text)
        filtered = [w for w in words if w not in self._SETTLED_STOP_WORDS]
        from collections import Counter
        freq = Counter(filtered)
        return [w for w, _ in freq.most_common(4)]

    def mark_topic_settled(self, topic_text: str, conclusion: str, ttl_days: int = 7) -> None:
        """
        标记某类议题已结案（已验证不存在、假设错误等），
        ttl_days 天内该议题关键词命中时会在种子选取阶段被跳过。
        """
        keywords = self._extract_topic_keywords(topic_text)
        if not keywords:
            return
        with self._lock:
            conn = self._get_conn()
            try:
                for kw in keywords:
                    conn.execute(
                        "INSERT OR REPLACE INTO settled_topics "
                        "(id, topic_key, conclusion, settled_at, ttl_days) VALUES (?,?,?,?,?)",
                        (
                            f"settled_{hashlib.md5(kw.encode()).hexdigest()[:8]}",
                            kw.lower(),
                            conclusion[:200],
                            datetime.now().isoformat(),
                            ttl_days,
                        )
                    )
                conn.commit()
            finally:
                conn.close()

    def is_topic_settled(self, seed_text: str) -> Tuple[bool, str]:
        """
        检查议题是否命中已结案注册表（在 TTL 内）。
        返回 (True, conclusion) 表示应跳过；(False, '') 表示未命中。
        """
        keywords = self._extract_topic_keywords(seed_text)
        if not keywords:
            return False, ""
        with self._lock:
            conn = self._get_conn()
            try:
                for kw in keywords:
                    row = conn.execute(
                        "SELECT conclusion, settled_at, ttl_days FROM settled_topics "
                        "WHERE topic_key=? ORDER BY settled_at DESC LIMIT 1",
                        (kw.lower(),)
                    ).fetchone()
                    if row:
                        conclusion, settled_at, ttl_days = row
                        try:
                            settled_dt = datetime.fromisoformat(settled_at)
                            if datetime.now() < settled_dt + timedelta(days=int(ttl_days or 7)):
                                return True, conclusion
                        except Exception:
                            pass
            finally:
                conn.close()
        return False, ""
