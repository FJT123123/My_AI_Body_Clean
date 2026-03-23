# tool_name: type_sandbox_validator

from langchain.tools import tool
import json
import re
from typing import Any, Dict, List, Union

@tool
def type_sandbox_validator(input_args: str) -> dict:
    """
    类型沙盒验证器 - 验证参数类型和结构的安全性
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - parameters: 要验证的参数字典
            - type_contract: 类型契约定义
            - validation_mode: 验证模式 ("strict", "lenient", "repair")
    
    Returns:
        dict: 包含验证结果的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            args = json.loads(input_args)
        else:
            args = input_args
            
        parameters = args.get('parameters', {})
        type_contract = args.get('type_contract', {})
        validation_mode = args.get('validation_mode', 'strict')
        
        results = {
            'is_valid': True,
            'validated_parameters': {},
            'errors': [],
            'warnings': [],
            'type_violations': [],
            'recommendations': []
        }
        
        # 基本类型映射
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        # 验证每个参数
        for param_name, param_value in parameters.items():
            if param_name not in type_contract:
                if validation_mode == 'strict':
                    results['errors'].append(f'参数 {param_name} 不在类型契约中')
                    results['is_valid'] = False
                continue
                
            expected_type = type_contract[param_name].get('type', 'any')
            required = type_contract[param_name].get('required', False)
            
            # 检查必需参数
            if required and param_value is None:
                results['errors'].append(f'必需参数 {param_name} 不能为空')
                results['is_valid'] = False
                continue
                
            if expected_type == 'any':
                results['validated_parameters'][param_name] = param_value
                continue
                
            # 检查类型
            if expected_type in type_mapping:
                expected_python_type = type_mapping[expected_type]
                if not isinstance(param_value, expected_python_type):
                    # 尝试类型转换（仅在repair模式下）
                    if validation_mode == 'repair':
                        try:
                            if expected_type == 'string':
                                converted_value = str(param_value)
                                results['validated_parameters'][param_name] = converted_value
                                results['warnings'].append(f'参数 {param_name} 已从 {type(param_value).__name__} 转换为 string')
                                continue
                            elif expected_type == 'integer':
                                converted_value = int(float(param_value))
                                results['validated_parameters'][param_name] = converted_value
                                results['warnings'].append(f'参数 {param_name} 已从 {type(param_value).__name__} 转换为 integer')
                                continue
                            elif expected_type == 'number':
                                converted_value = float(param_value)
                                results['validated_parameters'][param_name] = converted_value
                                results['warnings'].append(f'参数 {param_name} 已从 {type(param_value).__name__} 转换为 number')
                                continue
                            elif expected_type == 'boolean':
                                converted_value = bool(param_value)
                                results['validated_parameters'][param_name] = converted_value
                                results['warnings'].append(f'参数 {param_name} 已从 {type(param_value).__name__} 转换为 boolean')
                                continue
                        except (ValueError, TypeError):
                            pass
                    
                    results['type_violations'].append({
                        'parameter': param_name,
                        'expected': expected_type,
                        'actual': type(param_value).__name__,
                        'value': param_value
                    })
                    results['errors'].append(f'参数 {param_name} 类型错误: 期望 {expected_type}, 实际 {type(param_value).__name__}')
                    results['is_valid'] = False
                else:
                    results['validated_parameters'][param_name] = param_value
            else:
                # 自定义类型或复杂类型
                if validation_mode != 'lenient':
                    results['warnings'].append(f'参数 {param_name} 使用了未知类型 {expected_type}')
        
        # 生成建议
        if not results['is_valid']:
            if validation_mode == 'repair':
                results['recommendations'].append('使用 repair 模式自动修复了部分类型错误')
            else:
                results['recommendations'].append('考虑使用 repair 模式自动修复类型错误')
                
        return results
        
    except Exception as e:
        return {
            'is_valid': False,
            'error': str(e),
            'validated_parameters': {},
            'errors': [f'验证过程中发生错误: {str(e)}'],
            'warnings': [],
            'type_violations': [],
            'recommendations': ['检查输入参数格式是否正确']
        }