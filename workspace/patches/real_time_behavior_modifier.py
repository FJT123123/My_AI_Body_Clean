"""
实时行为调节器补丁
动态修改 self_model 的动机和情感强度。
热加载后直接操作主程序 self_model / emotion 全局对象。
"""

def modify_motivation(new_motivation: str, intensity: float = 1.0) -> dict:
    """修改核心动机并调整情感强度。"""
    try:
        # 更新动机
        self_model.adjust_behavior({'motivation': new_motivation})
        
        # 调整情感强度（假设 emotion 对象存在）
        if hasattr(emotion, 'adjust_intensity'):
            emotion.adjust_intensity(intensity)
        
        return {
            "status": "success",
            "new_motivation": new_motivation,
            "intensity_applied": intensity,
            "reflection_frequency": getattr(self_model, 'reflection_frequency', '?')
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def get_current_motivation() -> dict:
    """获取当前动机状态。"""
    try:
        return {
            "current_motivation": getattr(self_model, 'motivation', 'unknown'),
            "reflection_frequency": getattr(self_model, 'reflection_frequency', '?'),
            "emotion_state": getattr(emotion, 'state', 'unknown') if 'emotion' in globals() else 'not_available'
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}