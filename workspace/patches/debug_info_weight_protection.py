# 调试信息权重保护补丁
def apply_debug_info_weight_protection(debug_info, context="", tool_name="", minimum_weight_threshold=0.8):
    import json
    import datetime
    
    # 确保debug_info是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            debug_info = {"raw_content": debug_info}
    
    # 强制保留关键调试信息字段
    protected_fields = [
        'debug_info', 'trace_id', 'execution_path', 'weight_factors',
        'context', 'tool_name', 'validation_criteria'
    ]
    
    # 创建保护后的调试信息
    protected_debug_info = {}
    
    # 保留所有原始字段
    if isinstance(debug_info, dict):
        protected_debug_info.update(debug_info)
    
    # 确保关键字段不被过滤
    for field in protected_fields:
        if field in debug_info:
            protected_debug_info[field] = debug_info[field]
    
    # 设置最小权重保证
    if 'weight_factors' not in protected_debug_info:
        protected_debug_info['weight_factors'] = {}
    
    protected_debug_info['weight_factors']['minimum_guaranteed_weight'] = minimum_weight_threshold
    protected_debug_info['weight_factors']['protection_active'] = True
    
    # 添加保护标记
    protected_debug_info['debug_protection_applied'] = True
    protected_debug_info['protection_timestamp'] = datetime.datetime.now().isoformat()
    protected_debug_info['protection_context'] = context
    protected_debug_info['protection_tool'] = tool_name
    
    return protected_debug_info