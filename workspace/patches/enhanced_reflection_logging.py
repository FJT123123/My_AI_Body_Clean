"""
增强反思日志记录的热补丁
- 在每次反思后附加记录反思长度和是否触发行为变化
- 不干涉 importance（由 TTR 守卫 reflection_quality_guard 决定）
"""

def enhanced_reflection_logger(ctx):
    """只附加元数据，不覆盖 importance"""
    return {
        'reflection_length': len(ctx.get('reply', '')),
        'triggered_action': ctx.get('acted', False),
    }

# 注册（避免重复）
if "_post_reflection_hooks" in globals():
    _post_reflection_hooks[:] = [
        h for h in _post_reflection_hooks
        if getattr(h, "__name__", "") != "enhanced_reflection_logger"
    ]
    _post_reflection_hooks.append(enhanced_reflection_logger)
    print("   🔌 [patch] enhanced_reflection_logging 已注册")
else:
    print("   ⚠️  [patch] _post_reflection_hooks 不存在，无法注册")