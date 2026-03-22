def apply_enhanced_debug_info_protection(input_args):
    """
    增强版调试信息保护机制 - 直接修改现有函数的行为
    """
    import json
    
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args)
        except:
            params = {"debug_info": input_args}
    else:
        params = input_args
    
    debug_info = params.get("debug_info", {})
    context = params.get("context", "")
    tool_name = params.get("tool_name", "unknown_tool")
    minimum_weight_threshold = params.get("minimum_weight_threshold", 0.5)  # 提高默认阈值
    force_preserve_keys = params.get("force_preserve_keys", ["error", "trace_id", "timestamp", "status", "weight", "context", "result", "insights", "facts", "memories"])
    
    # 确保debug_info是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except:
            debug_info = {"raw_debug_info": debug_info}
    
    # 提取当前权重
    current_weight = 1.0
    if isinstance(debug_info, dict):
        # 检查各种可能的权重字段
        for weight_key in ["final_weight", "weight", "weight_calculation"]:
            if weight_key in debug_info:
                if isinstance(debug_info[weight_key], (int, float)):
                    current_weight = float(debug_info[weight_key])
                    break
                elif isinstance(debug_info[weight_key], dict) and "final_weight" in debug_info[weight_key]:
                    current_weight = float(debug_info[weight_key]["final_weight"])
                    break
    
    # 强制保留关键信息
    protected_debug_info = {}
    if isinstance(debug_info, dict):
        # 首先复制所有原始信息
        protected_debug_info = debug_info.copy()
        
        # 确保关键字段被保留
        for key in force_preserve_keys:
            if key in debug_info:
                protected_debug_info[key] = debug_info[key]
    
    # 应用增强保护 - 即使权重高于阈值也要确保完整性
    final_weight = max(current_weight, minimum_weight_threshold)
    
    # 添加保护标记
    if isinstance(protected_debug_info, dict):
        protected_debug_info["cognitive_immunity_applied"] = True
        protected_debug_info["original_weight"] = current_weight
        protected_debug_info["final_weight"] = final_weight
        protected_debug_info["enhanced_protection"] = True
    
    return {
        'success': True,
        'original_debug_info': debug_info,
        'processed_debug_info': protected_debug_info,
        'final_weight': final_weight,
        'context': context,
        'tool_name': tool_name,
        'cognitive_immunity_applied': True
    }