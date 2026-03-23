# tool_name: unified_api_parameter_validation_layer
from langchain.tools import tool
import json

@tool
def unified_api_parameter_validation_layer(input_args: str) -> dict:
    """
    统一API参数验证层：提供标准化的参数验证接口
    
    Args:
        input_args (str): JSON字符串，包含parameters和parameter_contract
        
    Returns:
        dict: 验证结果，包含is_valid, validated_params, errors, warnings
    """
    try:
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
            
        parameters = params.get('parameters', {})
        parameter_contract = params.get('parameter_contract', {})
        
        validated_params = {}
        errors = []
        warnings = []
        is_valid = True
        
        # 验证每个参数是否符合契约
        for param_name, param_value in parameters.items():
            if param_name not in parameter_contract:
                warnings.append(f"Parameter '{param_name}' not defined in contract")
                validated_params[param_name] = param_value
                continue
                
            contract = parameter_contract[param_name]
            required = contract.get('required', False)
            param_type = contract.get('type', 'any')
            min_val = contract.get('min', None)
            max_val = contract.get('max', None)
            allowed_values = contract.get('allowed_values', None)
            
            # 检查必需参数
            if required and param_value is None:
                errors.append(f"Required parameter '{param_name}' is missing")
                is_valid = False
                continue
                
            # 类型验证
            if param_type != 'any':
                type_mapping = {
                    'string': str,
                    'integer': int,
                    'number': (int, float),
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }
                
                expected_type = type_mapping.get(param_type, str)
                if not isinstance(param_value, expected_type):
                    errors.append(f"Parameter '{param_name}' should be of type {param_type}, got {type(param_value).__name__}")
                    is_valid = False
                    continue
                    
            # 数值范围验证
            if param_type in ['integer', 'number'] and param_value is not None:
                if min_val is not None and param_value < min_val:
                    errors.append(f"Parameter '{param_name}' value {param_value} is below minimum {min_val}")
                    is_valid = False
                if max_val is not None and param_value > max_val:
                    errors.append(f"Parameter '{param_name}' value {param_value} is above maximum {max_val}")
                    is_valid = False
                    
            # 允许值验证
            if allowed_values is not None and param_value not in allowed_values:
                errors.append(f"Parameter '{param_name}' value {param_value} is not in allowed values {allowed_values}")
                is_valid = False
                
            validated_params[param_name] = param_value
            
        # 检查缺失的必需参数
        for param_name, contract in parameter_contract.items():
            if contract.get('required', False) and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")
                is_valid = False
                
        return {
            'is_valid': is_valid,
            'validated_params': validated_params,
            'errors': errors,
            'warnings': warnings
        }
        
    except Exception as e:
        return {
            'is_valid': False,
            'validated_params': {},
            'errors': [f"Validation error: {str(e)}"],
            'warnings': []
        }