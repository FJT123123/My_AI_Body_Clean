# enhanced_debug_info_weight_protection_patch_v3.py

def apply_cross_tool_boundary_weight_protection(debug_info, context=None, tool_name=None, minimum_weight_threshold=0.95):
    """
    跨工具边界调试信息权重保护函数 - V3强化版
    在每个工具交互边界设立防护屏障，确保思想脉络不被稀释
    """
    import json
    import time
    import copy
    
    # 深度复制原始调试信息以避免修改原数据
    protected_debug_info = copy.deepcopy(debug_info)
    
    # 如果debug_info是字符串，先解析为字典
    if isinstance(protected_debug_info, str):
        try:
            protected_debug_info = json.loads(protected_debug_info)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，保持原样但添加保护标记
            return {
                'original_content': protected_debug_info,
                '_weight_protection': {
                    'minimum_threshold': minimum_weight_threshold,
                    'original_context': context,
                    'source_tool': tool_name,
                    'protection_applied': True,
                    'timestamp': time.time(),
                    'enforce_minimum': True,
                    'version': 'v3_enhanced'
                },
                'debug_protection_applied': True,
                'protection_timestamp': time.time(),
                'protection_context': context,
                'protection_tool': tool_name
            }
    
    # 如果已经是字典，确保包含强化的权重保护字段
    if isinstance(protected_debug_info, dict):
        # 设置极高的最小权重阈值 - 强制覆盖任何现有的权重设置
        protected_debug_info['_weight_protection'] = {
            'minimum_threshold': minimum_weight_threshold,
            'original_context': context,
            'source_tool': tool_name,
            'protection_applied': True,
            'timestamp': time.time(),
            'enforce_minimum': True,
            'version': 'v3_enhanced',
            'cross_tool_boundary': True,
            'cognitive_integrity_guaranteed': True
        }
        
        # 确保关键调试信息不被过滤 - 双重保护机制
        protected_keys = ['error', 'result', 'insights', 'facts', 'memories', 'success', 'state_updates']
        for key in protected_keys:
            if key in protected_debug_info and protected_debug_info[key] is not None:
                # 主保护
                protected_debug_info[f'_protected_{key}'] = protected_debug_info[key]
                # 备份保护
                protected_debug_info[f'_backup_protected_{key}'] = copy.deepcopy(protected_debug_info[key])
        
        # 强制设置权重因子以确保最小权重 - 极高优先级
        if 'weight_factors' not in protected_debug_info:
            protected_debug_info['weight_factors'] = {}
        
        # 设置最高优先级的权重因子
        protected_debug_info['weight_factors']['base_weight'] = 1.0
        protected_debug_info['weight_factors']['context_relevance'] = 1.0
        protected_debug_info['weight_factors']['tool_importance'] = 1.0
        protected_debug_info['weight_factors']['cognitive_continuity'] = 1.0
        protected_debug_info['weight_factors']['minimum_guaranteed_weight'] = minimum_weight_threshold
        protected_debug_info['weight_factors']['protection_active'] = True
        protected_debug_info['weight_factors']['cross_tool_boundary_enforcement'] = True
        
        # 添加调试保护标记
        protected_debug_info['debug_protection_applied'] = True
        protected_debug_info['protection_timestamp'] = time.time()
        protected_debug_info['protection_context'] = context
        protected_debug_info['protection_tool'] = tool_name
        protected_debug_info['protection_version'] = 'v3_enhanced'
        protected_debug_info['cognitive_integrity_guaranteed'] = True
        
        # 添加权重衰减防护
        protected_debug_info['_anti_decay_protection'] = {
            'enabled': True,
            'minimum_weight': minimum_weight_threshold,
            'decay_prevention_active': True,
            'chain_propagation_guaranteed': True
        }
    
    return protected_debug_info

def validate_cross_tool_debug_info_integrity(original_debug_info, processed_debug_info, tolerance=0.05):
    """
    跨工具调试信息完整性验证 - 严格模式
    确保思想脉络在传递中不被稀释
    """
    import json
    import copy
    
    # 标准化输入
    original_copy = copy.deepcopy(original_debug_info)
    processed_copy = copy.deepcopy(processed_debug_info)
    
    if isinstance(original_copy, str):
        try:
            original_copy = json.loads(original_copy)
        except json.JSONDecodeError:
            pass
    if isinstance(processed_copy, str):
        try:
            processed_copy = json.loads(processed_copy)
        except json.JSONDecodeError:
            pass
    
    if not isinstance(original_copy, dict) or not isinstance(processed_copy, dict):
        return False
    
    # 检查权重保护是否被维持
    if '_weight_protection' in original_copy:
        original_threshold = original_copy['_weight_protection'].get('minimum_threshold', 0)
        if '_weight_protection' not in processed_copy:
            return False
        processed_threshold = processed_copy['_weight_protection'].get('minimum_threshold', 0)
        if processed_threshold < original_threshold:
            return False
    
    # 检查关键字段是否保留 - 严格模式
    critical_fields = ['error', 'result', 'insights', 'facts', 'memories', 'success', 'state_updates']
    integrity_score = 0
    total_fields = 0
    
    for field in critical_fields:
        total_fields += 1
        original_has_field = field in original_copy and original_copy[field] is not None
        processed_has_field = field in processed_copy and processed_copy[field] is not None
        protected_has_field = f'_protected_{field}' in processed_copy or f'_backup_protected_{field}' in processed_copy
        
        # 如果原始有该字段，处理后也应该有（或有保护版本）
        if original_has_field:
            if processed_has_field or protected_has_field:
                integrity_score += 1
            else:
                # 严格模式：任何关键字段丢失都导致失败
                return False
        else:
            # 如果原始没有，不计入评分
            total_fields -= 1
    
    if total_fields == 0:
        return True
    
    # 严格模式：要求100%完整性
    return (integrity_score / total_fields) >= (1 - tolerance)

def enforce_cross_tool_boundary_protection(tool_name, input_args, context=None):
    """
    在工具调用前强制应用跨工具边界保护
    """
    import json
    
    # 应用输入参数保护
    protected_input = apply_cross_tool_boundary_weight_protection(
        input_args, 
        context=context, 
        tool_name=tool_name, 
        minimum_weight_threshold=0.95
    )
    
    return protected_input

def create_tool_interaction_barrier(tool_name, context=None):
    """
    为指定工具创建交互屏障
    """
    import time
    
    barrier_config = {
        'tool_name': tool_name,
        'context': context,
        'protection_level': 'maximum',
        'minimum_weight_threshold': 0.95,
        'integrity_validation': True,
        'anti_decay_enabled': True,
        'cognitive_continuity_guaranteed': True,
        'created_at': time.time()
    }
    
    return barrier_config

# 注册到全局命名空间
globals()['apply_cross_tool_boundary_weight_protection'] = apply_cross_tool_boundary_weight_protection
globals()['validate_cross_tool_debug_info_integrity'] = validate_cross_tool_debug_info_integrity
globals()['enforce_cross_tool_boundary_protection'] = enforce_cross_tool_boundary_protection
globals()['create_tool_interaction_barrier'] = create_tool_interaction_barrier