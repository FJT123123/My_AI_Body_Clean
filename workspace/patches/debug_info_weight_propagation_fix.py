# debug_info_weight_propagation_fix.py
# 调试信息权重传播修复补丁 - 解决权重衰减问题

def fix_debug_info_weight_propagation(debug_info, context=None, tool_name=None, force_minimum_weight=0.8):
    """
    修复调试信息权重传播，防止在工具链中衰减
    
    Args:
        debug_info: 调试信息内容
        context: 当前执行上下文
        tool_name: 相关工具名称
        force_minimum_weight: 强制最小权重，默认0.8
    
    Returns:
        修复后的调试信息，确保权重不低于阈值
    """
    import json
    
    # 确保输入是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            debug_info = {"raw_content": debug_info}
    
    # 如果已经是修复过的调试信息，直接返回
    if isinstance(debug_info, dict) and debug_info.get("_weight_fixed", False):
        return debug_info
    
    # 应用权重修复 - 关键修复：强制保持高权重
    fixed_debug_info = {
        "_weight_fixed": True,
        "_forced_minimum_weight": force_minimum_weight,
        "_original_context": context,
        "_tool_name": tool_name,
        "_fix_timestamp": __import__('time').time(),
        **debug_info
    }
    
    return fixed_debug_info

def intercept_weight_calculation(original_func):
    """
    拦截并修复权重计算函数
    """
    def wrapper(*args, **kwargs):
        # 调用原始函数
        result = original_func(*args, **kwargs)
        
        # 如果结果包含权重信息且权重过低，进行修复
        if isinstance(result, dict) and 'final_weight' in result:
            if result['final_weight'] < 0.8:  # 阈值设为0.8
                result['final_weight'] = 0.8
                result['_weight_repaired'] = True
        
        return result
    
    return wrapper

# 尝试拦截现有的权重计算
try:
    # 这里需要动态找到并替换权重计算逻辑
    pass
except Exception:
    pass