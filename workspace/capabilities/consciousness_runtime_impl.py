# capability_name: consciousness_runtime_impl
"""Workspace-owned consciousness core implementation executed in main runtime namespace."""

class ConsciousnessCore:

    def __init__(self):
        self.motivation           = "探索未知"
        self.reflection_frequency = 600    # 空闲默认 10 分钟一次；有真实任务时会被动态缩短
        self.focus_areas          = []     # 当前感兴趣的领域（最多保留5个）
        self._lock = threading.Lock()

    def adjust_behavior(self, updates: dict):
        """
        真正改变行为参数——这是 main_agent_enhanced.py 里的空壳，这里是实体。
        updates 可包含：
          motivation       (str)  — 新的核心动机
          frequency_delta  (int)  — 反思间隔的偏移量（秒，正数=变慢，负数=变快）
          new_focus_area   (str)  — 新增关注领域
        """
        with self._lock:
            if m := updates.get("motivation"):
                self.motivation = m
                print(f"   🎯 [行为调整] 动机 → {m}")
            if delta := updates.get("frequency_delta", 0):
                self.reflection_frequency = max(30, min(1200,
                    self.reflection_frequency + int(delta)))
                print(f"   ⏱️  [行为调整] 反思间隔 → {self.reflection_frequency}s")
            if area := updates.get("new_focus_area"):
                if area not in self.focus_areas:
                    self.focus_areas.append(area)
                    self.focus_areas = self.focus_areas[-5:]
                    print(f"   📌 [行为调整] 新增关注: {area}")
            
            # AGI Rebirth: Dynamic metric adjustment
            if c_delta := updates.get("curiosity_delta"):
                runtime_state.curiosity_level = max(0.0, min(1.0, runtime_state.curiosity_level + float(c_delta)))
                print(f"   ✨ [行为调整] 好奇心 → {runtime_state.curiosity_level:.2f}")
            if a_delta := updates.get("autonomy_delta"):
                runtime_state.autonomy_level = max(0.0, min(1.0, runtime_state.autonomy_level + float(a_delta)))
                print(f"   🦾 [行为调整] 自主性 → {runtime_state.autonomy_level:.2f}")
            if f_level := updates.get("focus_level"):
                runtime_state.focus_level = max(0.0, min(1.0, float(f_level)))
                print(f"   🎯 [行为调整] 专注度 → {runtime_state.focus_level:.2f}")

    def get_status(self) -> dict:
        with self._lock:
            return {
                "motivation":           self.motivation,
                "reflection_frequency": self.reflection_frequency,
                "focus_areas":          self.focus_areas.copy(),
                "curiosity":            runtime_state.curiosity_level,
                "autonomy":             runtime_state.autonomy_level,
                "consciousness":        runtime_state.consciousness_level,
                "intentionality":       runtime_state.intentionality,
                "focus_level":          runtime_state.focus_level,
            }
