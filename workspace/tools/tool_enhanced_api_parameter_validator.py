# tool_name: enhanced_api_parameter_validator
from langchain.tools import tool
import json

@tool
def enhanced_api_parameter_validator(input_args: str) -> dict:
    """
    增强型API参数验证与防御工具
    
    这个工具实现了完整的API参数语义验证框架，专门用于在参数生成阶段就进行
    语义完整性验证，避免400错误发生。支持工具名称长度验证、参数契约验证、
    自动修复和详细诊断。通过复用视频参数契约验证能力提供更精确的验证结果。
    
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
    try:
        import json
        
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        action = params.get('action')
        if not action:
            return {
                'result': {'error': '缺少 action 参数'},
                'insights': ['参数校验失败：必须提供action'],
                'facts': [],
                'memories': []
            }
        
        # 动态加载能力模块
        capability_module = __import__('workspace.tools.video_parameter_contract_validator_capability', fromlist=['validate_parameter_contract'])
        validate_parameter_contract = getattr(capability_module, 'validate_parameter_contract')
        run_parameter_validation_cycle = getattr(capability_module, 'run_parameter_validation_cycle')
        generate_parameter_error_info = getattr(capability_module, 'generate_parameter_error_info')
        repair_parameter_format = getattr(capability_module, 'repair_parameter_format')
        unified_parameter_parser = getattr(capability_module, 'unified_parameter_parser')
        
        if action == 'validate_tool_name':
            tool_name = params.get('tool_name')
            max_length = params.get('max_length', 64)
            
            if not tool_name:
                return {
                    'valid': False,
                    'error': '缺少 tool_name 参数',
                    'action': action
                }
            
            # 验证工具名称长度（简单实现）
            if len(tool_name) > max_length:
                return {
                    'valid': False,
                    'error': f'工具名称长度超过限制: {len(tool_name)} > {max_length}',
                    'tool_name': tool_name,
                    'actual_length': len(tool_name),
                    'max_length': max_length,
                    'action': action
                }
            
            # 检查是否包含非法字符
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
                return {
                    'valid': False,
                    'error': '工具名称包含非法字符，只允许字母、数字和下划线',
                    'tool_name': tool_name,
                    'action': action
                }
            
            return {
                'valid': True,
                'tool_name': tool_name,
                'length': len(tool_name),
                'action': action
            }
        
        elif action == 'validate_parameter_contract':
            parameters = params.get('parameters')
            parameter_contract = params.get('parameter_contract')
            
            if parameters is None:
                return {
                    'valid': False,
                    'error': '缺少 parameters 参数',
                    'action': action
                }
            
            if parameter_contract is None:
                return {
                    'valid': False,
                    'error': '缺少 parameter_contract 参数',
                    'action': action
                }
            
            # 使用能力模块进行参数契约验证
            validation_result = validate_parameter_contract(parameters, parameter_contract)
            
            return {
                'valid': validation_result.get('valid', False),
                'validation_details': validation_result,
                'action': action
            }
        
        elif action == 'repair_parameter_format':
            parameters = params.get('parameters')
            
            if parameters is None:
                return {
                    'valid': False,
                    'error': '缺少 parameters 参数',
                    'action': action
                }
            
            # 使用能力模块进行参数格式修复
            repair_result = repair_parameter_format(parameters)
            
            return {
                'valid': True,
                'repaired_parameters': repair_result.get('repaired_parameters', parameters),
                'repair_details': repair_result,
                'action': action
            }
        
        elif action == 'generate_error_info':
            error_context = params.get('error_context')
            
            if error_context is None:
                return {
                    'valid': False,
                    'error': '缺少 error_context 参数',
                    'action': action
                }
            
            # 使用能力模块生成错误信息
            error_info = generate_parameter_error_info(error_context, {})
            
            return {
                'valid': True,
                'error_info': error_info,
                'action': action
            }
        
        elif action == 'run_validation_cycle':
            tool_name = params.get('tool_name')
            parameters = params.get('parameters', {})
            parameter_contract = params.get('parameter_contract', {})
            max_length = params.get('max_length', 64)
            
            results = {}
            
            # 验证工具名称
            if tool_name:
                results['tool_name_validation'] = enhanced_api_parameter_validator(json.dumps({
                    'action': 'validate_tool_name',
                    'tool_name': tool_name,
                    'max_length': max_length
                }))
            
            # 验证参数契约
            if parameters and parameter_contract:
                results['parameter_validation'] = enhanced_api_parameter_validator(json.dumps({
                    'action': 'validate_parameter_contract',
                    'parameters': parameters,
                    'parameter_contract': parameter_contract
                }))
            
            # 整体有效性
            overall_valid = True
            for result in results.values():
                if isinstance(result, dict) and not result.get('valid', True):
                    overall_valid = False
                    break
            
            return {
                'valid': overall_valid,
                'validation_results': results,
                'action': action
            }
        
        else:
            return {
                'valid': False,
                'error': f'不支持的动作: {action}',
                'supported_actions': ['validate_tool_name', 'validate_parameter_contract', 'repair_parameter_format', 'generate_error_info', 'run_validation_cycle'],
                'action': action
            }
    
    except Exception as e:
        return {
            'valid': False,
            'error': f'执行过程中发生错误: {str(e)}',
            'action': 'unknown'
        }