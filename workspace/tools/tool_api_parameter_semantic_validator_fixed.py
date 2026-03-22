# tool_name: api_parameter_semantic_validator_fixed

from langchain.tools import tool
import json
import re

@tool
def api_parameter_semantic_validator_fixed(input_args):
    """
    API参数语义验证与400错误预测性防御工具 - 修复版

    这个工具实现了完整的API参数语义验证框架，用于在参数生成阶段就进行语义完整性验证，
    避免400错误发生。支持工具名称长度验证、参数契约验证、自动修复和详细诊断。

    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'validate_tool_name', 'validate_parameter_contract', 
                                    'repair_parameter_format', 'generate_error_info', 'run_validation_cycle'
            - tool_name (str, optional): 工具名称（用于validate_tool_name动作）
            - parameters (dict, optional): 参数字典（用于validate_parameter_contract动作）
            - parameter_contract (dict, optional): 参数契约定义（用于validate_parameter_contract动作）
            - error_context (dict, optional): 错误上下文信息（用于generate_error_info动作）
            - max_length (int, optional): 最大允许长度，默认64字符（用于validate_tool_name动作）
            - auto_apply (bool, optional): 是否自动应用修复，默认True

    Returns:
        dict: 包含验证结果的字典
    """
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
                'recommendation': '请提供有效的字符串作为工具名称'
            }

        # 检查长度
        if len(tool_name) > max_length:
            # 安全截断，保留前缀，并添加_trc标识
            prefix_len = max_length - 4  # 为"_trc"留出空间
            if prefix_len <= 0:
                safe_name = "safe_tool_trc"
            else:
                safe_name = tool_name[:prefix_len] + "_trc"

            # 确保只包含合法字符
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)

            return {
                'valid': False,
                'original_name': tool_name,
                'safe_tool_name': safe_name,
                'error': f'工具名称超过{max_length}字符限制',
                'recommendation': f'使用 "{safe_name}" 作为工具名称'
            }

        # 检查字符合法性
        if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
            return {
                'valid': False,
                'original_name': tool_name,
                'safe_tool_name': safe_name,
                'error': '工具名称只能包含字母、数字和下划线',
                'recommendation': f'使用 "{safe_name}" 作为工具名称'
            }

        return {
            'valid': True,
            'original_name': tool_name,
            'safe_tool_name': tool_name,
            'message': f'工具名称 "{tool_name}" 符合长度要求'
        }

    def validate_parameter_contract(parameters, parameter_contract):
        """验证参数是否符合契约"""
        if not isinstance(parameters, dict):
            parameters = {}

        if not isinstance(parameter_contract, dict):
            return {
                'valid': False,
                'errors': ['参数契约必须是字典类型'],
                'warnings': [],
                'missing_required': ['parameter_contract'],
                'type_mismatches': [],
                'suggestions': [],
                'recommendation': '请提供有效的参数契约字典'
            }

        missing_required = []
        type_mismatches = []
        errors = []
        warnings = []

        # 检查必需参数是否存在
        for param_name, param_def in parameter_contract.items():
            if param_def.get('required', False):
                if param_name not in parameters:
                    missing_required.append(param_name)
                    errors.append(f'缺少必需参数: {param_name}')
                else:
                    # 检查类型
                    expected_type = param_def.get('type', 'any')
                    actual_value = parameters[param_name]
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
                        if not isinstance(actual_value, expected_python_type):
                            type_mismatches.append({
                                'param': param_name,
                                'expected': expected_type,
                                'actual': type(actual_value).__name__
                            })
                            errors.append(f'参数 {param_name} 类型错误: 期望 {expected_type}, 实际 {type(actual_value).__name__}')

        valid = len(missing_required) == 0 and len(type_mismatches) == 0

        result = {
            'valid': valid,
            'errors': errors,
            'warnings': warnings,
            'missing_required': missing_required,
            'type_mismatches': type_mismatches,
            'suggestions': []
        }

        if not valid:
            if missing_required:
                result['recommendation'] = f'请提供缺失的必需参数: {", ".join(missing_required)}'
            elif type_mismatches:
                result['recommendation'] = '请修正参数类型错误'

        return result

    def repair_parameter_format(parameters, parameter_contract):
        """自动修复参数格式问题"""
        if not isinstance(parameters, dict):
            parameters = {}

        if not isinstance(parameter_contract, dict):
            return {
                'success': False,
                'repaired_parameters': parameters,
                'repairs_applied': [f'参数契约类型错误: {type(parameter_contract)}'],
                'message': '无法修复：参数契约无效'
            }

        repaired = parameters.copy()
        repairs_applied = []

        # 添加缺失的必需参数（使用默认值或类型默认值）
        repairs_applied.append(f'开始修复，参数契约有 {len(parameter_contract)} 个参数')
        for param_name, param_def in parameter_contract.items():
            required_check = param_def.get('required', False)
            # 如果不是布尔类型，尝试转换
            if not isinstance(required_check, bool):
                if str(required_check).lower() in ['true', '1', 'yes']:
                    required_check = True
                else:
                    required_check = False
            
            if required_check:
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
                    expected_type = param_def.get('type', 'any')
                    actual_value = repaired[param_name]
                    if expected_type != 'any':
                        type_map = {
                            'string': str,
                            'integer': int,
                            'number': float,
                            'boolean': bool,
                            'array': list,
                            'object': dict
                        }
                        expected_python_type = type_map.get(expected_type, object)
                        if not isinstance(actual_value, expected_python_type):
                            # 尝试转换类型
                            try:
                                if expected_type == 'string':
                                    repaired[param_name] = str(actual_value)
                                    repairs_applied.append(f'转换类型 {param_name} 为字符串')
                                elif expected_type == 'integer':
                                    repaired[param_name] = int(float(actual_value))  # 先转float再转int处理字符串数字
                                    repairs_applied.append(f'转换类型 {param_name} 为整数')
                                elif expected_type == 'number':
                                    repaired[param_name] = float(actual_value)
                                    repairs_applied.append(f'转换类型 {param_name} 为数字')
                                elif expected_type == 'boolean':
                                    repaired[param_name] = bool(actual_value)
                                    repairs_applied.append(f'转换类型 {param_name} 为布尔值')
                                elif expected_type == 'array' and not isinstance(actual_value, list):
                                    repaired[param_name] = [actual_value]
                                    repairs_applied.append(f'转换类型 {param_name} 为数组')
                                elif expected_type == 'object' and not isinstance(actual_value, dict):
                                    repaired[param_name] = {'value': actual_value}
                                    repairs_applied.append(f'转换类型 {param_name} 为对象')
                            except (ValueError, TypeError):
                                # 转换失败，保留原值或使用默认值
                                if 'default' in param_def:
                                    repaired[param_name] = param_def['default']
                                    repairs_applied.append(f'使用默认值 {param_name} = {param_def["default"]} (转换失败)')
                                else:
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
                                    repairs_applied.append(f'使用默认值 {param_name} = {default_value} (转换失败)')

        return {
            'success': True,
            'repaired_parameters': repaired,
            'repairs_applied': repairs_applied,
            'message': f'成功应用 {len(repairs_applied)} 个修复'
        }

    # 获取操作类型和参数
    action = args.get('action', 'run_validation_cycle')
    auto_apply = args.get('auto_apply', True)
    
    if action == 'run_validation_cycle':
        # 执行完整的验证周期
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

        # 步骤3: 自动修复参数格式
        if auto_apply:
            repair_result = repair_parameter_format(parameters, parameter_contract)
        else:
            repair_result = {
                'success': True,
                'repaired_parameters': parameters,
                'repairs_applied': [],
                'message': '未启用自动修复'
            }
        validation_steps.append({
            'step': 'repair_parameter_format',
            'result': repair_result
        })

        # 步骤4: 修复后重新验证
        if repair_result['success']:
            revalidated_params = repair_result['repaired_parameters']
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

        return {
            'validation_steps': validation_steps,
            'final_result': {
                'valid': final_valid,
                'message': '验证通过' if final_valid else '验证失败'
            },
            'overall_valid': final_valid,
            'repaired_parameters': final_params
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

    elif action == 'generate_error_info':
        error_context = args.get('error_context', {})
        return {
            'error_type': 'parameter_validation_error',
            'context': error_context,
            'recommendations': [
                '检查工具名称长度是否超过64字符',
                '确保所有必需参数都已提供',
                '验证参数类型是否符合契约定义',
                '使用auto_apply=True启用自动修复'
            ]
        }

    else:
        return {
            'result': {'error': f'不支持的操作类型: {action}'},
            'insights': ['支持的操作类型: run_validation_cycle, validate_tool_name, validate_parameter_contract, repair_parameter_format, generate_error_info'],
            'facts': [],
            'memories': []
        }