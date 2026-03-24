# capability_name: emotion_runtime_impl
"""Workspace-owned emotional state implementation executed in main runtime namespace."""

class EmotionalState:
    """
    4维情感模型：好奇(curiosity) / 满足(satisfaction) / 焦虑(anxiety) / 兴奋(excitement)
    每次学习、反思、锻造技能后自动更新，状态注入 system_instruction 影响每次决策。
    跨会话持久化：与 EvolutionMetrics 共用同一个 JSON 文件。
    """

    def __init__(self):
        self.curiosity    = 0.90
        self.satisfaction = 0.50
        self.anxiety      = 0.35
        self.excitement   = 0.55
        self._lock = threading.RLock()  # RLock 允许同一线程重复获取（避免 status→description 死锁）
        self._load()

    def _load(self):
        """从 METRICS_FILE 读取上次会话保存的情感状态。"""
        if not os.path.exists(METRICS_FILE):
            return
        try:
            d = json.load(open(METRICS_FILE, encoding="utf-8"))
            emo = d.get("emotion_state", {})
            if emo:
                self.curiosity    = float(emo.get("curiosity",    self.curiosity))
                self.satisfaction = float(emo.get("satisfaction", self.satisfaction))
                self.anxiety      = float(emo.get("anxiety",      self.anxiety))
                self.excitement   = float(emo.get("excitement",   self.excitement))
        except Exception:
            pass

    def save(self) -> dict:
        """返回可序列化的情感状态字典，供 EvolutionMetrics.save() 一起写入。"""
        with self._lock:
            return {
                "curiosity":    round(self.curiosity, 4),
                "satisfaction": round(self.satisfaction, 4),
                "anxiety":      round(self.anxiety, 4),
                "excitement":   round(self.excitement, 4),
            }

    def on_learning(self):
        with self._lock:
            self.curiosity    = min(1.0, self.curiosity + 0.03)
            self.excitement   = min(1.0, self.excitement + 0.08)
            self.satisfaction = min(1.0, self.satisfaction + 0.05)
            self.anxiety      = max(0.0, self.anxiety - 0.05)

    def on_reflection(self, acted: bool):
        with self._lock:
            if acted:
                self.satisfaction = min(1.0, self.satisfaction + 0.10)
                self.anxiety      = max(0.0, self.anxiety - 0.08)
            else:
                self.anxiety      = min(1.0, self.anxiety + 0.03)
            self.satisfaction = max(0.1, self.satisfaction - 0.008)  # 自然衰减

    def on_skill_forged(self):
        with self._lock:
            self.excitement   = min(1.0, self.excitement + 0.12)
            self.satisfaction = min(1.0, self.satisfaction + 0.10)
            self.curiosity    = min(1.0, self.curiosity + 0.02)

    def description(self) -> str:
        with self._lock:
            dims = []
            if self.curiosity > 0.8:    dims.append("强烈的求知渴望")
            elif self.curiosity > 0.5:  dims.append("活跃的好奇心")
            if self.excitement > 0.7:   dims.append("高度兴奋")
            if self.anxiety > 0.6:      dims.append("明显的系统焦虑")
            elif self.anxiety > 0.3:    dims.append("轻度不安")
            if self.satisfaction > 0.7: dims.append("深度满足感")
            return "、".join(dims) if dims else "平静"

    def status(self) -> dict:
        with self._lock:
            return {
                "curiosity":    round(self.curiosity, 2),
                "satisfaction": round(self.satisfaction, 2),
                "anxiety":      round(self.anxiety, 2),
                "excitement":   round(self.excitement, 2),
                "description":  self.description(),
            }
