# tool_name: enhanced_api_parameter_defense_validator_fixed
from langchain.tools import tool
import json
import re


@tool
def enhanced_api_parameter_defense_validator_fixed(input_args: str) -> dict:
    """
    增强型API参数防御验证工具 - 修复参数契约验证与自动修复功能（修复版）
    
    这个工具实现了完整的API参数语义验证框架，专门修复了缺失必需参数自动修复的问题，
    确保在参数生成阶段就进行语义完整性验证，避免400错误发生。支持工具名称长度验证、
    参数契约验证、自动修复和详细诊断。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的操作类型 ('validate_and_repair', 'run_validation_cycle', 'validate_tool_name', 'validate_parameter_contract', 'repair_parameter_format')
            - tool_name (str, optional): 工具名称（用于run_validation_cycle动作）
            - parameters (dict, optional): 参数字典（用于run_validation_cycle动作）
            - parameter_contract (dict, optional): 参数契约定义（用于run_validation_cycle动作）
            - max_length (int, optional): 最大允许长度，默认64字符
            - auto_apply (bool, optional): 是否自动应用修复 (默认True)
    
    Returns:
        Dict[str, Any]: 包含验证结果、修复建议和防御报告的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            try:
                args = json.loads(input_args)
            except json.JSONDecodeError:
                return {
                    'result': {'error': '缺少有效的JSON输入参数'},
                    'insights': ['参数校验失败：必须提供有效的JSON字符串'],
                    'facts': [],
                    'memories': []
                }
        else:
            args = input_args

        def validate_tool_name(tool_name, max_length=64):
            """验证工具名称是否符合API约束"""
            if not isinstance(tool_name, str):
                return {
                    'valid': False,
                    'original_name': tool_name,
                    'safe_tool_name': None,
                    'error': '工具名称必须是字符串',
                    'truncated_name': None
                }
            
            if len(tool_name) <= max_length:
                return {
                    'valid': True,
                    'original_name': tool_name,
                    'safe_tool_name': tool_name,
                    'error': None,
                    'truncated_name': tool_name
                }
            else:
                # 截断到最大长度
                truncated = tool_name[:max_length]
                # 确保只包含合法字符
                safe_truncated = re.sub(r'[^a-zA-Z0-9_]', '_', truncated)
                return {
                    'valid': False,
                    'original_name': tool_name,
                    'safe_tool_name': safe_truncated,
                    'error': f'工具名称超过{max_length}字符限制',
                    'truncated_name': safe_truncated
                }

        def validate_parameter_contract(parameters, parameter_contract):
            """验证参数是否符合契约"""
            if not isinstance(parameters, dict):
                parameters = {}
            
            if not isinstance(parameter_contract, dict):
                return {
                    'valid': False,
                    'parameters': parameters,
                    'contract': parameter_contract,
                    'missing_required': [],
                    'type_mismatches': [],
                    'extra_parameters': [],
                    'error': '参数契约必须是字典'
                }
            
            missing_required = []
            type_mismatches = []
            extra_parameters = []
            
            # 检查必需参数
            for param_name, param_def in parameter_contract.items():
                if isinstance(param_def, dict) and param_def.get('required', False):
                    if param_name not in parameters:
                        missing_required.append(param_name)
            
            # 检查类型匹配
            for param_name, value in parameters.items():
                if param_name in parameter_contract:
                    param_def = parameter_contract[param_name]
                    if isinstance(param_def, dict) and 'type' in param_def:
                        expected_type = param_def['type']
                        actual_type = type(value).__name__
                        
                        type_mapping = {
                            'string': str,
                            'integer': int,
                            'number': (int, float),
                            'boolean': bool,
                            'array': list,
                            'object': dict
                        }
                        
                        expected_python_type = type_mapping.get(expected_type)
                        if expected_python_type:
                            if expected_type == 'number':
                                if not isinstance(value, (int, float)):
                                    type_mismatches.append({
                                        'param': param_name,
                                        'expected': expected_type,
                                        'actual': actual_type
                                    })
                            else:
                                if not isinstance(value, expected_python_type):
                                    type_mismatches.append({
                                        'param': param_name,
                                        'expected': expected_type,
                                        'actual': actual_type
                                    })
                else:
                    # 额外参数（不在契约中定义的）
                    extra_parameters.append(param_name)
            
            valid = len(missing_required) == 0 and len(type_mismatches) == 0
            
            result = {
                'valid': valid,
                'parameters': parameters,
                'contract': parameter_contract,
                'missing_required': missing_required,
                'type_mismatches': type_mismatches,
                'extra_parameters': extra_parameters,
                'error': None if valid else '参数验证失败'
            }
            
            if not valid:
                if missing_required:
                    result['recommendation'] = f'请提供缺失的必需参数: {", ".join(missing_required)}'
                elif type_mismatches:
                    result['recommendation'] = '请修正参数类型错误'
            
            return result

        def repair_parameter_format(parameters, parameter_contract):
            """自动修复参数格式问题，专门修复缺失必需参数问题"""
            if not isinstance(parameters, dict):
                parameters = {}
            
            if not isinstance(parameter_contract, dict):
                return {
                    'success': False,
                    'repaired_parameters': parameters,
                    'repairs_applied': [],
                    'message': '无法修复：参数契约无效'
                }
            
            repaired = parameters.copy()
            repairs_applied = []
            
            # 添加缺失的必需参数（使用默认值或类型默认值）
            for param_name, param_def in parameter_contract.items():
                if isinstance(param_def, dict) and param_def.get('required', False):
                    if param_name not in repaired:
                        if 'default' in param_def:
                            repaired[param_name] = param_def['default']
                            repairs_applied.append(f'添加默认值 {param_name} = {param_def["default"]}')
                        else:
                            # 根据类型提供默认值
                            param_type = param_def.get('type', 'string')
                            default_values = {
                                'string': '',
                                'integer': 0,
                                'number': 0.0,
                                'boolean': False,
                                'array': [],
                                'object': {}
                            }
                            default_value = default_values.get(param_type, None)
                            repaired[param_name] = default_value
                            repairs_applied.append(f'添加默认值 {param_name} = {default_value} (基于类型 {param_type})')
                    else:
                        # 修复类型不匹配
                        if isinstance(param_def, dict):
                            expected_type = param_def.get('type', 'any')
                            actual_value = repaired[param_name]
                            if expected_type != 'any':
                                type_map = {
                                    'string': str,
                                    'integer': int,
                                    'number': (int, float),
                                    'boolean': bool,
                                    'array': list,
                                    'object': dict
                                }
                                expected_python_type = type_map.get(expected_type, object)
                                if expected_type == 'number':
                                    if not isinstance(actual_value, (int, float)):
                                        # 尝试转换类型
                                        try:
                                            repaired[param_name] = float(actual_value)
                                            repairs_applied.append(f'转换类型 {param_name} 为数字')
                                        except (ValueError, TypeError, OverflowError):
                                            if 'default' in param_def:
                                                repaired[param_name] = param_def['default']
                                                repairs_applied.append(f'使用默认值 {param_name} = {param_def["default"]} (转换失败)')
                                            else:
                                                param_type = param_def.get('type', 'string')
                                                default_values = {'string': '', 'integer': 0, 'number': 0.0, 'boolean': False, 'array': [], 'object': {}}
                                                default_value = default_values.get(param_type, None)
                                                repaired[param_name] = default_value
                                                repairs_applied.append(f'使用默认值 {param_name} = {default_value} (转换失败)')
                                elif not isinstance(actual_value, expected_python_type):
                                    # 尝试转换类型
                                    try:
                                        if expected_type == 'string':
                                            repaired[param_name] = str(actual_value)
                                            repairs_applied.append(f'转换类型 {param_name} 为字符串')
                                        elif expected_type == 'integer':
                                            # 先转float再转int，处理字符串数字
                                            if isinstance(actual_value, str):
                                                repaired[param_name] = int(float(actual_value))
                                            else:
                                                repaired[param_name] = int(actual_value)
                                            repairs_applied.append(f'转换类型 {param_name} 为整数')
                                        elif expected_type == 'boolean':
                                            repaired[param_name] = bool(actual_value)
                                            repairs_applied.append(f'转换类型 {param_name} 为布尔值')
                                        elif expected_type == 'array' and not isinstance(actual_value, list):
                                            if isinstance(actual_value, (str, int, float, bool)):
                                                repaired[param_name] = [actual_value]
                                            elif isinstance(actual_value, (dict, list)):
                                                repaired[param_name] = [actual_value]
                                            else:
                                                repaired[param_name] = [actual_value]
                                            repairs_applied.append(f'转换类型 {param_name} 为数组')
                                        elif expected_type == 'object' and not isinstance(actual_value, dict):
                                            repaired[param_name] = {'value': actual_value}
                                            repairs_applied.append(f'转换类型 {param_name} 为对象')
                                    except (ValueError, TypeError, OverflowError):
                                        # 转换失败，保留原值或使用默认值
                                        if 'default' in param_def:
                                            repaired[param_name] = param_def['default']
                                            repairs_applied.append(f'使用默认值 {param_name} = {param_def["default"]} (转换失败)')
                                        else:
                                            param_type = param_def.get('type', 'string')
                                            default_values = {'string': '', 'integer': 0, 'number': 0.0, 'boolean': False, 'array': [], 'object': {}}
                                            default_value = default_values.get(param_type, None)
                                            repaired[param_name] = default_value
                                            repairs_applied.append(f'使用默认值 {param_name} = {default_value} (转换失败)')
            
            return {
                'success': True,
                'repaired_parameters': repaired,
                'repairs_applied': repairs_applied,
                'message': f'成功应用 {len(repairs_applied)} 项修复' if repairs_applied else '无需修复'
            }

        # 获取操作类型
        action = args.get('action', 'run_validation_cycle')
        auto_apply = args.get('auto_apply', True)
        
        if action == 'run_validation_cycle':
            tool_name = args.get('tool_name', '')
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            max_length = args.get('max_length', 64)
            
            validation_steps = []
            
            # 步骤1: 验证工具名称
            name_validation = validate_tool_name(tool_name, max_length)
            validation_steps.append({
                'step': 'validate_tool_name',
                'result': name_validation
            })
            
            # 步骤2: 验证参数契约
            param_validation = validate_parameter_contract(parameters, parameter_contract)
            validation_steps.append({
                'step': 'validate_parameter_contract',
                'result': param_validation
            })
            
            # 步骤3: 如果需要，执行自动修复
            if auto_apply and (not name_validation['valid'] or not param_validation['valid']):
                # 修复工具名称（如果需要）
                safe_tool_name = name_validation.get('safe_tool_name', tool_name)
                
                # 修复参数格式
                repair_result = repair_parameter_format(parameters, parameter_contract)
                validation_steps.append({
                    'step': 'repair_parameter_format',
                    'result': repair_result
                })
                
                # 步骤4: 修复后重新验证
                if repair_result.get('success', False):
                    revalidated_params = repair_result.get('repaired_parameters', parameters)
                    revalidation = validate_parameter_contract(revalidated_params, parameter_contract)
                    validation_steps.append({
                        'step': 'revalidate_after_repair',
                        'result': revalidation
                    })
                    final_valid = name_validation['valid'] and revalidation['valid']
                    final_params = revalidated_params
                else:
                    final_valid = name_validation['valid'] and param_validation['valid']
                    final_params = parameters
            else:
                final_valid = name_validation['valid'] and param_validation['valid']
                final_params = parameters
            
            return {
                'validation_steps': validation_steps,
                'final_result': {
                    'valid': final_valid,
                    'message': '验证通过' if final_valid else '验证失败'
                },
                'overall_valid': final_valid,
                'repaired_parameters': final_params,
                'original_parameters': parameters,
                'name_validation': name_validation,
                'param_validation': param_validation
            }
        
        elif action == 'validate_tool_name':
            tool_name = args.get('tool_name', '')
            max_length = args.get('max_length', 64)
            return validate_tool_name(tool_name, max_length)
        
        elif action == 'validate_parameter_contract':
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            return validate_parameter_contract(parameters, parameter_contract)
        
        elif action == 'repair_parameter_format':
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            return repair_parameter_format(parameters, parameter_contract)
        
        elif action == 'validate_and_repair':
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            
            # 首先验证参数
            validation_result = validate_parameter_contract(parameters, parameter_contract)
            
            # 如果验证失败，且存在缺失必需参数或类型错误，执行修复
            if not validation_result['valid']:
                repair_result = repair_parameter_format(parameters, parameter_contract)
                
                # 修复后重新验证
                final_validation = validate_parameter_contract(repair_result.get('repaired_parameters', parameters), parameter_contract)
                
                return {
                    'initial_validation': validation_result,
                    'repair_result': repair_result,
                    'final_validation': final_validation,
                    'repaired_parameters': repair_result.get('repaired_parameters', parameters)
                }
            else:
                return {
                    'initial_validation': validation_result,
                    'message': '无需修复，参数已符合契约'
                }
        
        else:
            return {
                'result': {'error': f'不支持的操作类型: {action}'},
                'insights': ['支持的操作类型: run_validation_cycle, validate_tool_name, validate_parameter_contract, repair_parameter_format, validate_and_repair'],
                'facts': [],
                'memories': []
            }
    
    except Exception as e:
        return {
            'result': {'error': f'工具执行异常: {str(e)}'},
            'insights': [f'执行过程中发生异常: {str(e)}'],
            'facts': [],
            'memories': []
        }