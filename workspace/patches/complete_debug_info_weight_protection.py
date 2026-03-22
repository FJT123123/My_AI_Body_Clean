# complete_debug_info_weight_protection.py
# 完整的调试信息权重保护解决方案

import json
import time

def apply_complete_weight_protection(debug_info, context=None, tool_name=None, minimum_weight=0.9):
    """
    应用完整的调试信息权重保护
    
    Args:
        debug_info: 调试信息
        context: 上下文
        tool_name: 工具名称
        minimum_weight: 最小权重阈值
    
    Returns:
        保护后的调试信息
    """
    # 处理输入格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except:
            debug_info = {"content": debug_info}
    
    # 创建保护后的调试信息
    protected = {
        "_weight_protected": True,
        "_minimum_weight": minimum_weight,
        "_context": context,
        "_tool_name": tool_name,
        "_protection_time": time.time(),
        "_original_debug_info": debug_info.copy() if isinstance(debug_info, dict) else debug_info,
        **(debug_info if isinstance(debug_info, dict) else {})
    }
    
    return protected

def validate_weight_preservation(original, processed, threshold=0.8):
    """验证权重保护效果"""
    if not isinstance(processed, dict) or not processed.get("_weight_protected"):
        return False
    
    # 检查关键信息是否保留
    if isinstance(original, dict) and isinstance(processed, dict):
        original_keys = set(original.keys())
        processed_keys = set(k for k in processed.keys() if not k.startswith('_'))
        preservation_rate = len(original_keys & processed_keys) / max(len(original_keys), 1)
        return preservation_rate >= threshold
    
    return True

# 全局保护函数
def protect_debug_info_in_toolchain(debug_info, context="toolchain_protection", tool_name="unknown"):
    """在工具链中保护调试信息的统一入口"""
    return apply_complete_weight_protection(
        debug_info, 
        context=context, 
        tool_name=tool_name, 
        minimum_weight=0.95  # 非常高的保护阈值
    )

# 注册到全局命名空间
globals()['apply_complete_weight_protection'] = apply_complete_weight_protection
globals()['protect_debug_info_in_toolchain'] = protect_debug_info_in_toolchain
globals()['validate_weight_preservation'] = validate_weight_preservation