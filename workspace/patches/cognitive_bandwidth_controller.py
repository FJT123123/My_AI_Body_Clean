"""
认知带宽控制器补丁
动态调节 self_model 的反思频率和情感权重。
热加载后直接操作主程序 self_model / emotion 全局对象。
"""

# 带宽比例 → 映射到 reflection_frequency 实际秒数范围 [10, 120]
_BANDWIDTH_RF_MAP = {
    'fast':    10,   # 高强度反思
    'normal':  30,
    'slow':    90,
    'minimal': 120,
}

class CognitiveBandwidthController:
    def __init__(self):
        # 三个维度的权重（总和 1.0）
        self.bandwidth_allocation = {
            'reflection': 0.3,
            'learning':   0.4,
            'execution':  0.3,
        }

    def adjust_allocation(self, component: str, new_ratio: float) -> dict:
        """调整特定组件的带宽，并将 reflection 权重同步到 self_model.reflection_frequency。"""
        if component not in self.bandwidth_allocation:
            raise ValueError(f"Unknown component: {component}")
        new_ratio = max(0.05, min(0.9, float(new_ratio)))
        old_ratio = self.bandwidth_allocation[component]
        delta = new_ratio - old_ratio
        other = [k for k in self.bandwidth_allocation if k != component]
        total_other = sum(self.bandwidth_allocation[k] for k in other)
        if total_other > 0:
            for comp in other:
                self.bandwidth_allocation[comp] -= (self.bandwidth_allocation[comp] / total_other) * delta
        self.bandwidth_allocation[component] = new_ratio
        self._sync_to_self_model()
        return self.get_status()

    def _sync_to_self_model(self):
        """将 reflection 权重换算为 reflection_frequency 并写入 self_model。"""
        rf = self.bandwidth_allocation.get('reflection', 0.3)
        # rf 越高 → 反思越频繁 → 秒数越小；线性映射 [0.05,0.9] → [120,10]
        new_freq = int(120 - (rf - 0.05) / 0.85 * 110)
        new_freq = max(10, min(120, new_freq))
        try:
            self_model.adjust_behavior({'reflection_frequency_delta': new_freq - self_model.reflection_frequency})
        except Exception:
            pass  # 主程序对象不可用时静默跳过

    def get_status(self) -> dict:
        return {
            'bandwidth_allocation': self.bandwidth_allocation.copy(),
            'total': round(sum(self.bandwidth_allocation.values()), 4),
            'reflection_frequency_sec': getattr(self_model, 'reflection_frequency', '?'),
        }

# 补丁加载时创建/替换全局实例
cognitive_controller = CognitiveBandwidthController()
cognitive_controller._sync_to_self_model()  # 立即同步一次当前默认值

def get_cognitive_status() -> dict:
    """获取认知带宽状态（可被 Agent 工具调用）"""
    return cognitive_controller.get_status()

def adjust_cognitive_bandwidth(component: str, ratio: float) -> dict:
    """调整认知带宽分配并同步到 self_model（可被 Agent 工具调用）"""
    return cognitive_controller.adjust_allocation(component, ratio)