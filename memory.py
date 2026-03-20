"""
兼容的GraphMemory模块，使用SQLite作为后备存储
当Neo4j不可用时自动降级到SQLite
"""
import os
import json
import re
from datetime import datetime
from iflow_adapter import get_iflow_llm
import sys
import threading
from typing import List, Dict, Any, Optional

# AGI Rebirth: 增加本地依赖库路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_lib_path = os.path.join(_current_dir, "lib")
if os.path.exists(_lib_path) and _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

class GraphMemory:
    def __init__(self):
        # 尝试连接Neo4j
        self.neo4j_enabled = False
        try:
            from neo4j import GraphDatabase
            import dotenv
            dotenv.load_dotenv()
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("✅ [系统] Neo4j数据库连接成功！")
            self.neo4j_enabled = True
        except Exception as e:
            print(f"⚠️ [系统] Neo4j连接失败，使用SQLite后备: {e}")
            self.driver = None
        
        self.llm = get_iflow_llm("coder", temperature=0)
        
        # 初始化SQLite作为后备
        self.db_path = os.path.join(os.path.dirname(__file__), "memory_graph.db")
        self.lock = threading.Lock()
        self._init_sqlite_db()
        
        print("🧠 [记忆模块] 初始化完成")
    
    def _init_sqlite_db(self):
        """初始化SQLite数据库作为图形存储的后备方案"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建节点表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    content TEXT,
                    last_seen TEXT
                )
            ''')
            
            # 创建关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    target TEXT,
                    type TEXT,
                    created_at TEXT
                )
            ''')
            
            # 创建记忆快照表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT,
                    timestamp TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def _save_to_neo4j(self, text: str, data: Dict) -> str:
        """尝试保存到Neo4j数据库"""
        if not self.driver:
            raise Exception("Neo4j未连接")
            
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.driver.session() as session:
            # 创建快照
            session.run("CREATE (m:Snapshot {content: $text, timestamp: $time})", text=text, time=now_str)
            
            # 创建节点
            nodes = data.get("nodes", [])
            for node in nodes:
                session.run("""
                    MERGE (e:Entity {id: $id}) 
                    SET e.type = $type, e.last_seen = $time
                    WITH e MATCH (s:Snapshot {timestamp: $time}) MERGE (s)-[:MENTIONS]->(e)
                """, id=node.get("id", "Unknown"), type=node.get("type", "Object"), time=now_str)
            
            # 创建关系
            rels = data.get("rels", [])
            for rel in rels:
                session.run("""
                    MERGE (a:Entity {id: $src}) MERGE (b:Entity {id: $tgt})
                    MERGE (a)-[r:RELATED_TO]->(b) SET r.type = $rel_type, r.updated_at = $time
                """, src=rel.get("source"), tgt=rel.get("target"), rel_type=rel.get("type", "CONNECTED"), time=now_str)
        
        return f"✅ Neo4j存入成功 (节点:{len(nodes)} 关系:{len(rels)})"
    
    def _save_to_sqlite(self, text: str, data: Dict) -> str:
        """保存到SQLite数据库"""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 保存记忆快照
            cursor.execute("INSERT INTO snapshots (content, timestamp) VALUES (?, ?)", (text, now_str))
            
            # 保存节点
            nodes = data.get("nodes", [])
            for node in nodes:
                cursor.execute("""
                    INSERT OR REPLACE INTO nodes 
                    (id, type, content, last_seen) 
                    VALUES (?, ?, ?, ?)
                """, (
                    node.get("id", "Unknown"), 
                    node.get("type", "Object"), 
                    text if node.get("id", "Unknown") == "Unknown" else node.get("content", text), 
                    now_str
                ))
            
            # 保存关系
            rels = data.get("rels", [])
            for rel in rels:
                cursor.execute("""
                    INSERT INTO relationships 
                    (source, target, type, created_at) 
                    VALUES (?, ?, ?, ?)
                """, (
                    rel.get("source"), 
                    rel.get("target"), 
                    rel.get("type", "CONNECTED"), 
                    now_str
                ))
            
            conn.commit()
            conn.close()
        
        return f"✅ SQLite存入成功 (节点:{len(nodes)} 关系:{len(rels)})"
    
    def save_memory(self, text: str) -> str:
        """保存记忆，优先使用Neo4j，后备使用SQLite"""
        # 尝试从文本中提取实体和关系
        try:
            prompt = f"""
            你是一个知识提取引擎。请将以下文本中的核心实体和关系提取为严格的 JSON 格式。
            要求：
            1. 必须包含 "nodes" (带 id 和 type) 和 "rels" (带 source, target, type)。
            2. 只返回 JSON 块，不要任何解释。
            
            文本内容: {text}
            """
            
            response = self.llm.invoke(prompt).content
            clean_json = re.sub(r"```json\s*|```", "", response).strip()
            
            try:
                data = json.loads(clean_json)
            except json.JSONDecodeError as je:
                print(f"⚠️ [解析警告] JSON 格式不规范: {je}")
                match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    raise je

            result = ""
            # 尝试保存到Neo4j
            if self.neo4j_enabled:
                try:
                    result = self._save_to_neo4j(text, data)
                except Exception as e:
                    print(f"⚠️ Neo4j保存失败，使用SQLite后备: {e}")
                    result = self._save_to_sqlite(text, data)
            else:
                # 直接保存到SQLite
                result = self._save_to_sqlite(text, data)
            
            return result
            
        except Exception as e:
            print(f"❌ 写入流程崩溃: {e}")
            # 即使解析失败，也至少保存原始文本
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO snapshots (content, timestamp) VALUES (?, ?)", (text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
            return "✅ 基础保存成功 (解析失败但文本已存)"
    
    def _recall_from_neo4j(self, query: str) -> List[Dict[str, Any]]:
        """从Neo4j检索记忆"""
        if not self.driver:
            raise Exception("Neo4j未连接")
            
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Entity) WHERE n.id CONTAINS $q OR n.type CONTAINS $q
                OPTIONAL MATCH (n)-[r]->(m:Entity)
                RETURN n.id AS Source, type(r) AS Relation, m.id AS Target 
                ORDER BY coalesce(n.last_seen, "") DESC LIMIT 10
            """, q=query)
            return [{"Source": r["Source"], "Relation": r["Relation"], "Target": r["Target"]} for r in result if r["Source"]]
    
    def _recall_from_sqlite(self, query: str) -> List[Dict[str, Any]]:
        """从SQLite检索记忆"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 搜索节点和关系
            cursor.execute("""
                SELECT n1.id AS Source, r.type AS Relation, n2.id AS Target
                FROM nodes n1
                LEFT JOIN relationships r ON n1.id = r.source
                LEFT JOIN nodes n2 ON r.target = n2.id
                WHERE n1.id LIKE ? OR n1.type LIKE ? OR n1.content LIKE ?
                ORDER BY n1.last_seen DESC
                LIMIT 10
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            results = []
            for row in cursor.fetchall():
                if row[0]:  # 如果有源节点
                    results.append({
                        "Source": row[0],
                        "Relation": row[1] if row[1] else "MENTIONS",
                        "Target": row[2] if row[2] else "Unknown"
                    })
            
            conn.close()
            return results
    
    def recall_memory(self, query: str) -> List[Dict[str, Any]]:
        """从记忆中检索相关信息，优先使用Neo4j，后备使用SQLite"""
        try:
            if self.neo4j_enabled:
                try:
                    return self._recall_from_neo4j(query)
                except Exception as e:
                    print(f"⚠️ Neo4j检索失败，使用SQLite后备: {e}")
                    return self._recall_from_sqlite(query)
            else:
                return self._recall_from_sqlite(query)
        except Exception as e:
            print(f"❌ 检索记忆时出错: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆库统计信息"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM nodes")
            node_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM relationships")
            rel_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM snapshots")
            snapshot_count = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                "sqlite_nodes": node_count,
                "sqlite_relationships": rel_count,
                "sqlite_snapshots": snapshot_count,
                "neo4j_enabled": self.neo4j_enabled
            }
            
            # 如果Neo4j可用，也获取Neo4j的统计
            if self.neo4j_enabled and self.driver:
                try:
                    with self.driver.session() as session:
                        neo4j_nodes = list(session.run("MATCH (n) RETURN count(n) AS count"))[0]["count"]
                        neo4j_rels = list(session.run("MATCH ()-[r]->() RETURN count(r) AS count"))[0]["count"]
                        stats["neo4j_nodes"] = neo4j_nodes
                        stats["neo4j_relationships"] = neo4j_rels
                except:
                    pass
            
            return stats