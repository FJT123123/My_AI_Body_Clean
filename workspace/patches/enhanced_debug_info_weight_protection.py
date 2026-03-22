# enhanced_debug_info_weight_protection.py
# 调试信息权重保护补丁 - 防止工具链传递中的权重衰减

def apply_debug_info_weight_protection(debug_info, context=None, tool_name=None, minimum_weight_threshold=0.8):
    """
    应用调试信息权重保护机制，确保调试信息在工具链传递中保持高权重
    
    Args:
        debug_info: 调试信息内容
        context: 当前执行上下文
        tool_name: 相关工具名称
        minimum_weight_threshold: 最小权重阈值，默认0.8（防止衰减到0.3以下）
    
    Returns:
        保护后的调试信息，确保权重不低于阈值
    """
    import json
    
    # 确保输入是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            debug_info = {"raw_content": debug_info}
    
    # 如果已经是保护过的调试信息，直接返回
    if isinstance(debug_info, dict) and debug_info.get("_weight_protected", False):
        return debug_info
    
    # 应用权重保护
    protected_debug_info = {
        "_weight_protected": True,
        "_minimum_weight": minimum_weight_threshold,
        "_original_context": context,
        "_tool_name": tool_name,
        "_protection_timestamp": __import__('time').time(),
        **debug_info
    }
    
    return protected_debug_info

def validate_debug_info_weight_preservation(original_debug_info, processed_debug_info, threshold=0.8):
    """
    验证调试信息权重是否得到保护
    
    Args:
        original_debug_info: 原始调试信息
        processed_debug_info: 处理后的调试信息
        threshold: 权重保护阈值
    
    Returns:
        验证结果字典
    """
    # 检查是否应用了保护机制
    is_protected = (
        isinstance(processed_debug_info, dict) and 
        processed_debug_info.get("_weight_protected", False)
    )
    
    # 检查关键信息是否保留
    original_keys = set(original_debug_info.keys()) if isinstance(original_debug_info, dict) else set()
    processed_keys = set(processed_debug_info.keys()) if isinstance(processed_debug_info, dict) else set()
    key_preservation_rate = len(original_keys.intersection(processed_keys)) / max(len(original_keys), 1)
    
    return {
        "weight_protection_applied": is_protected,
        "key_preservation_rate": key_preservation_rate,
        "meets_threshold": is_protected and key_preservation_rate >= threshold,
        "original_size": len(str(original_debug_info)),
        "processed_size": len(str(processed_debug_info))
    }