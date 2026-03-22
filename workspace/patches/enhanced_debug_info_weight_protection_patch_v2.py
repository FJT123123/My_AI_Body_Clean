# enhanced_debug_info_weight_protection_patch_v2.py

def apply_debug_info_weight_protection(debug_info, context=None, tool_name=None, minimum_weight_threshold=0.8):
    """
    增强版调试信息权重保护函数
    确保调试信息在工具链传递中保持最小权重阈值
    """
    import json
    import time
    
    # 如果debug_info是字符串，先解析为字典
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，保持原样
            return debug_info
    
    # 如果已经是字典，确保包含必要的权重保护字段
    if isinstance(debug_info, dict):
        # 设置最小权重阈值 - 强制覆盖任何现有的权重设置
        debug_info['_weight_protection'] = {
            'minimum_threshold': minimum_weight_threshold,
            'original_context': context,
            'source_tool': tool_name,
            'protection_applied': True,
            'timestamp': time.time(),
            'enforce_minimum': True  # 标记需要强制执行最小权重
        }
        
        # 确保关键调试信息不被过滤
        protected_keys = ['error', 'result', 'insights', 'facts', 'memories', 'success']
        for key in protected_keys:
            if key in debug_info and debug_info[key] is not None:
                debug_info[f'_protected_{key}'] = debug_info[key]
        
        # 强制设置权重因子以确保最小权重
        if 'weight_factors' not in debug_info:
            debug_info['weight_factors'] = {}
        
        # 设置高优先级的权重因子
        debug_info['weight_factors']['base_weight'] = 1.0
        debug_info['weight_factors']['context_relevance'] = 1.0
        debug_info['weight_factors']['tool_importance'] = 1.0
        debug_info['weight_factors']['minimum_guaranteed_weight'] = minimum_weight_threshold
        debug_info['weight_factors']['protection_active'] = True
        
        # 添加调试保护标记
        debug_info['debug_protection_applied'] = True
        debug_info['protection_timestamp'] = time.time()
        debug_info['protection_context'] = context
        debug_info['protection_tool'] = tool_name
    
    return debug_info

def validate_debug_info_integrity(original_debug_info, processed_debug_info, tolerance=0.1):
    """
    验证调试信息完整性，确保关键信息未丢失
    """
    import json
    
    # 标准化输入
    if isinstance(original_debug_info, str):
        original_debug_info = json.loads(original_debug_info)
    if isinstance(processed_debug_info, str):
        processed_debug_info = json.loads(processed_debug_info)
    
    if not isinstance(original_debug_info, dict) or not isinstance(processed_debug_info, dict):
        return False
    
    # 检查关键字段是否保留
    critical_fields = ['error', 'result', 'insights', 'facts', 'memories', 'success']
    integrity_score = 0
    total_fields = 0
    
    for field in critical_fields:
        total_fields += 1
        original_has_field = field in original_debug_info and original_debug_info[field] is not None
        processed_has_field = field in processed_debug_info and processed_debug_info[field] is not None
        
        # 如果原始有该字段，处理后也应该有（或有保护版本）
        if original_has_field:
            if processed_has_field or f'_protected_{field}' in processed_debug_info:
                integrity_score += 1
        else:
            # 如果原始没有，不计入评分
            total_fields -= 1
    
    if total_fields == 0:
        return True
    
    return (integrity_score / total_fields) >= (1 - tolerance)

def enforce_minimum_weight_in_framework(weight_result, minimum_threshold=0.8):
    """
    在权重框架结果中强制执行最小权重
    """
    if isinstance(weight_result, dict) and 'weight_calculation' in weight_result:
        current_weight = weight_result['weight_calculation'].get('final_weight', 0)
        if current_weight < minimum_threshold:
            # 调整权重因子以满足最小阈值
            weight_result['weight_calculation']['final_weight'] = minimum_threshold
            weight_result['weight_calculation']['enforced_minimum'] = True
            weight_result['weight_calculation']['original_weight'] = current_weight
            
            # 调整可见性级别
            if minimum_threshold >= 0.8:
                weight_result['visibility_level'] = 'full'
                weight_result['importance_level'] = 'high'
            elif minimum_threshold >= 0.5:
                weight_result['visibility_level'] = 'detailed'
                weight_result['importance_level'] = 'medium'
            
    return weight_result

# 注册到全局命名空间
globals()['apply_debug_info_weight_protection'] = apply_debug_info_weight_protection
globals()['validate_debug_info_integrity'] = validate_debug_info_integrity
globals()['enforce_minimum_weight_in_framework'] = enforce_minimum_weight_in_framework