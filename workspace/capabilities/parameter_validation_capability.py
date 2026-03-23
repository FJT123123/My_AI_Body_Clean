# capability_name: parameter_validation_capability

def safe_parameter_parser(input_data):
    """
    安全的参数解析器，用于处理验证工具的输入参数
    """
    import json
    
    if isinstance(input_data, str):
        try:
            return json.loads(input_data)
        except (json.JSONDecodeError, TypeError):
            raise ValueError("输入参数不是有效的JSON字符串")
    elif isinstance(input_data, dict):
        return input_data
    else:
        raise ValueError("输入参数必须是JSON字符串或字典")

def fixed_unified_api_parameter_validation_layer(input_args):
    """
    修复后的统一API参数验证层
    """
    import json
    
    try:
        args_dict = safe_parameter_parser(input_args)
    except ValueError as e:
        return {
            'is_valid': False,
            'validated_params': {},
            'errors': [str(e)],
            'warnings': []
        }
    
    parameters = args_dict.get('parameters', {})
    parameter_contract = args_dict.get('parameter_contract', {})
    
    errors = []
    warnings = []
    validated_params = {}
    
    # 验证必需参数
    for param_name, contract in parameter_contract.items():
        is_required = contract.get('required', False)
        param_type = contract.get('type', 'any')
        default_value = contract.get('default', None)
        
        if param_name in parameters:
            # 参数存在，验证类型
            param_value = parameters[param_name]
            if param_type != 'any':
                if param_type == 'string' and not isinstance(param_value, str):
                    errors.append(f"参数 '{param_name}' 应为字符串类型")
                elif param_type == 'number' and not isinstance(param_value, (int, float)):
                    errors.append(f"参数 '{param_name}' 应为数字类型")
                elif param_type == 'boolean' and not isinstance(param_value, bool):
                    errors.append(f"参数 '{param_name}' 应为布尔类型")
                elif param_type == 'object' and not isinstance(param_value, dict):
                    errors.append(f"参数 '{param_name}' 应为对象类型")
                elif param_type == 'array' and not isinstance(param_value, list):
                    errors.append(f"参数 '{param_name}' 应为数组类型")
            
            validated_params[param_name] = param_value
        else:
            # 参数不存在
            if is_required:
                errors.append(f"缺少必需参数 '{param_name}'")
            elif default_value is not None:
                validated_params[param_name] = default_value
    
    # 检查额外参数（不在契约中的参数）
    for param_name in parameters:
        if param_name not in parameter_contract:
            warnings.append(f"发现未在契约中定义的参数 '{param_name}'")
            validated_params[param_name] = parameters[param_name]
    
    return {
        'is_valid': len(errors) == 0,
        'validated_params': validated_params,
        'errors': errors,
        'warnings': warnings
    }

def fixed_type_sandbox_validator(input_args):
    """
    修复后的类型沙盒验证器
    """
    import json
    
    try:
        args_dict = safe_parameter_parser(input_args)
    except ValueError as e:
        return {
            'is_valid': False,
            'validated_parameters': {},
            'errors': [str(e)],
            'warnings': [],
            'type_violations': [],
            'recommendations': ['确保输入参数格式正确']
        }
    
    parameters = args_dict.get('parameters', {})
    type_contract = args_dict.get('type_contract', {})
    validation_mode = args_dict.get('validation_mode', 'strict')
    
    errors = []
    warnings = []
    type_violations = []
    validated_parameters = {}
    
    # 验证参数类型
    for param_name, expected_type in type_contract.items():
        if param_name in parameters:
            param_value = parameters[param_name]
            actual_type = type(param_value).__name__
            
            # 类型映射
            type_mapping = {
                'str': 'string',
                'int': 'number',
                'float': 'number',
                'bool': 'boolean',
                'dict': 'object',
                'list': 'array'
            }
            
            normalized_actual_type = type_mapping.get(actual_type, actual_type)
            
            if expected_type == 'any':
                validated_parameters[param_name] = param_value
            elif expected_type == normalized_actual_type:
                validated_parameters[param_name] = param_value
            else:
                type_violations.append(f"参数 '{param_name}': 期望 {expected_type}, 实际 {normalized_actual_type}")
                if validation_mode == 'strict':
                    errors.append(f"参数 '{param_name}' 类型不匹配")
                validated_parameters[param_name] = param_value
        else:
            if validation_mode == 'strict':
                errors.append(f"缺少参数 '{param_name}'")
    
    # 处理额外参数
    for param_name in parameters:
        if param_name not in type_contract:
            validated_parameters[param_name] = parameters[param_name]
            if validation_mode == 'strict':
                warnings.append(f"未定义的参数 '{param_name}'")
    
    return {
        'is_valid': len(errors) == 0,
        'validated_parameters': validated_parameters,
        'errors': errors,
        'warnings': warnings,
        'type_violations': type_violations,
        'recommendations': []
    }

def fixed_cognitive_weight_repair_mapper(input_params):
    """
    修复后的认知权重修复映射器
    """
    import json
    
    try:
        params_dict = safe_parameter_parser(input_params)
    except ValueError as e:
        return {
            'error': str(e),
            'mapping_validity': 0.0,
            'success_rate_prediction': 0.0,
            'confidence_interval': [0.0, 0.0],
            'validation_results': {},
            'recommendations': []
        }
    
    cognitive_weights = params_dict.get('cognitive_weights', {})
    repair_scenarios = params_dict.get('repair_scenarios', [])
    validation_metrics = params_dict.get('validation_metrics', {})
    
    # 简单的映射有效性计算
    if not cognitive_weights or not repair_scenarios:
        mapping_validity = 0.0
        success_rate_prediction = 0.0
    else:
        # 基于权重和场景数量的简单计算
        weight_sum = sum(cognitive_weights.values())
        scenario_count = len(repair_scenarios)
        metric_avg = sum(validation_metrics.values()) / len(validation_metrics) if validation_metrics else 0.5
        
        mapping_validity = min(1.0, weight_sum * 0.5 + metric_avg * 0.5)
        success_rate_prediction = min(1.0, scenario_count * 0.1 + metric_avg * 0.7)
    
    confidence_interval = [
        max(0.0, success_rate_prediction - 0.1),
        min(1.0, success_rate_prediction + 0.1)
    ]
    
    validation_results = {
        'weight_analysis': cognitive_weights,
        'scenario_coverage': len(repair_scenarios),
        'metric_performance': validation_metrics
    }
    
    recommendations = []
    if mapping_validity < 0.5:
        recommendations.append("建议增加认知权重的多样性")
    if success_rate_prediction < 0.6:
        recommendations.append("建议扩展修复场景覆盖范围")
    
    result = {
        'mapping_validity': mapping_validity,
        'success_rate_prediction': success_rate_prediction,
        'confidence_interval': confidence_interval,
        'validation_results': validation_results,
        'recommendations': recommendations
    }
    
    if 'error' in locals():
        result['error'] = error
    
    return result

def run_parameter_validation_cycle(input_data):
    """
    运行参数验证循环，整合所有验证功能
    """
    try:
        parsed_input = safe_parameter_parser(input_data)
        
        # 根据输入参数类型选择验证方法
        validation_type = parsed_input.get('validation_type', 'unified_api')
        
        if validation_type == 'unified_api':
            return fixed_unified_api_parameter_validation_layer(input_data)
        elif validation_type == 'type_sandbox':
            return fixed_type_sandbox_validator(input_data)
        elif validation_type == 'cognitive_weight':
            return fixed_cognitive_weight_repair_mapper(input_data)
        else:
            # 如果没有指定类型，默认使用统一API验证
            return fixed_unified_api_parameter_validation_layer(input_data)
    
    except Exception as e:
        return {
            'is_valid': False,
            'validated_params': {},
            'errors': [f"验证过程发生错误: {str(e)}"],
            'warnings': []
        }

def check_parameter_validation(input_data):
    """
    检查参数是否符合验证要求
    """
    return run_parameter_validation_cycle(input_data)