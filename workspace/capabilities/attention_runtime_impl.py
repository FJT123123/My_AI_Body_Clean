# capability_name: attention_runtime_impl
"""Workspace-owned attention gate implementation executed in main runtime namespace."""

class AttentionGate:
    """
    专注力与抗干扰机制。
    - focus_topic  : 当前专注主题（None = 开放模式）
    - focus_until  : 专注期截止时间戳
    - pending_queue: 低相关性输入暂存队列
    """

    def __init__(self):
        self.focus_topic   = None
        self.focus_until   = 0.0
        self.pending_queue = []  # [{"text": ..., "relevance": ..., "ts": ...}]
        self._lock = threading.Lock()

    def set_focus(self, topic: str, duration: int = 300):
        with self._lock:
            self.focus_topic = topic
            self.focus_until = time.time() + duration
            # 同步写入 consciousness.focus_areas
            consciousness.adjust_behavior({"new_focus_area": topic})
        print(f"🎯 [专注] 进入专注模式: {topic}，持续 {duration}s")

    def clear_focus(self):
        with self._lock:
            self.focus_topic = None
            self.focus_until = 0.0
        print("⚡ [专注] 专注模式已关闭，进入开放探索")

    def is_focused(self) -> bool:
        with self._lock:
            if self.focus_until > time.time():
                return True
            if self.focus_topic:
                self.focus_topic = None  # 过期自动清除
            return False

    def filter(self, text: str) -> tuple:
        """
        返回 (should_process: bool, reason: str)。
        低相关性输入进入 pending_queue。
        """
        if not self.is_focused():
            return True, "开放模式，全量处理"
        with self._lock:
            ft = self.focus_topic or ""
        
        # AGI Rebirth: 动态干扰阈值。高好奇心 = 易受干扰；高专注度 = 极度排外。
        # 默认 0.5，根据 curiosity 和 focus_level 浮动
        threshold = 0.5 + (runtime_state.focus_level * 0.2) - (runtime_state.curiosity_level * 0.2)
        threshold = max(0.1, min(0.9, threshold))

        # 简单相关性：主题词是否出现在输入中
        relevance = 1.0 if ft.lower() in text.lower() else 0.4
        
        if relevance < threshold:
            with self._lock:
                self.pending_queue.append({"text": text, "relevance": relevance, "ts": time.time()})
                self.pending_queue = sorted(self.pending_queue,
                                            key=lambda x: x["relevance"], reverse=True)[:10]
            return False, f"⚠️ 相关性 {relevance:.1f} < 专注阈值 {threshold:.1f}，已加入待处理队列（当前专注: {ft}）"
        return True, f"✅ 通过专注过滤 (相关性 {relevance:.1f})"

    def pending_summary(self) -> str:
        with self._lock:
            if not self.pending_queue:
                return "待处理队列为空"
            items = [f"  [{i+1}] {p['text'][:40]}..." for i, p in enumerate(self.pending_queue)]
            return f"待处理队列 ({len(self.pending_queue)} 项):\n" + "\n".join(items)

    def pop_pending(self) -> Optional[dict]:
        """提取并删除最高相关性的待处理项。"""
        with self._lock:
            if not self.pending_queue:
                return None
            return self.pending_queue.pop(0)  # 已按相关性排序
