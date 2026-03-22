# tool_name: attention_driven_api_defense_validator

from langchain.tools import tool
import json

@tool
def attention_driven_api_defense_validator(input_args: str) -> dict:
    """
    注意力驱动的API防御预测验证器 - 动态优先级集成版
    
    这个工具实现了完整的API参数语义验证框架，专门用于在参数生成阶段就进行
    语义完整性验证，避免400错误发生。支持工具名称长度验证、参数契约验证、
    自动修复和详细诊断。
    
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
        # 解析输入参数
        if isinstance(input_args, str):
            try:
                args = json.loads(input_args)
            except json.JSONDecodeError:
                return {
                    'result': {'error': '缺少有效的JSON格式input_args参数'},
                    'insights': ['参数校验失败：必须提供有效的JSON格式input_args'],
                    'facts': [],
                    'memories': []
                }
        else:
            args = input_args
        
        # 验证必需参数
        action = args.get('action')
        if not action:
            return {
                'result': {'error': '缺少 action 参数'},
                'insights': ['参数校验失败：必须提供action参数'],
                'facts': [],
                'memories': []
            }
        
        # 导入能力模块
        video_validator_capability = load_capability_module("video_parameter_contract_validator_capability")
        
        # 执行不同动作
        if action == 'validate_tool_name':
            tool_name = args.get('tool_name')
            max_length = args.get('max_length', 64)
            
            if not tool_name:
                return {
                    'result': {'error': '缺少 tool_name 参数'},
                    'insights': ['参数校验失败：必须提供tool_name参数'],
                    'facts': [],
                    'memories': []
                }
                
            # 验证工具名称长度
            if len(tool_name) > max_length:
                return {
                    'result': {
                        'valid': False,
                        'original_name': tool_name,
                        'truncated_name': tool_name[:max_length],
                        'message': f'工具名称超过{max_length}字符限制！实际长度{len(tool_name)}'
                    },
                    'insights': [f'工具名称长度验证结果：工具名称超过{max_length}字符限制！实际长度{len(tool_name)}'],
                    'facts': [f'tool_name_validation_result_{tool_name[:20]}'],
                    'memories': [f'成功验证了工具名称 "{tool_name}" 的长度限制']
                }
            else:
                return {
                    'result': {
                        'valid': True,
                        'original_name': tool_name,
                        'message': f'工具名称符合{max_length}字符限制'
                    },
                    'insights': [f'工具名称长度验证结果：工具名称符合{max_length}字符限制'],
                    'facts': [f'tool_name_validation_success_{tool_name[:20]}'],
                    'memories': [f'成功验证了工具名称 "{tool_name}" 符合长度限制']
                }
        
        elif action == 'validate_parameter_contract':
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            
            if not parameter_contract:
                return {
                    'result': {'error': '缺少 parameter_contract 参数'},
                    'insights': ['参数校验失败：必须提供parameter_contract参数'],
                    'facts': [],
                    'memories': []
                }
            
            # 使用能力模块验证参数契约
            validation_result = video_validator_capability.validate_parameter_contract(parameters, parameter_contract)
            
            return {
                'result': validation_result,
                'insights': ['完成参数契约验证'],
                'facts': ['parameter_contract_validation_completed'],
                'memories': ['成功执行了参数契约验证']
            }
        
        elif action == 'repair_parameter_format':
            parameters = args.get('parameters', {})
            
            if not parameters:
                return {
                    'result': {'error': '缺少 parameters 参数'},
                    'insights': ['参数校验失败：必须提供parameters参数'],
                    'facts': [],
                    'memories': []
                }
            
            # 使用能力模块修复参数格式
            repair_result = video_validator_capability.repair_parameter_format(parameters)
            
            return {
                'result': repair_result,
                'insights': ['完成参数格式修复'],
                'facts': ['parameter_format_repair_completed'],
                'memories': ['成功执行了参数格式修复']
            }
        
        elif action == 'generate_error_info':
            error_context = args.get('error_context', {})
            
            # 使用能力模块生成错误信息
            error_info_result = video_validator_capability.generate_parameter_error_info(error_context, {})
            
            return {
                'result': error_info_result,
                'insights': ['生成参数错误信息'],
                'facts': ['parameter_error_info_generated'],
                'memories': ['成功生成了参数错误信息']
            }
        
        elif action == 'run_validation_cycle':
            # 运行完整的验证周期
            tool_name = args.get('tool_name')
            parameters = args.get('parameters', {})
            parameter_contract = args.get('parameter_contract', {})
            max_length = args.get('max_length', 64)
            auto_apply = args.get('auto_apply', True)
            
            results = {
                'tool_name_validation': None,
                'parameter_validation': None,
                'overall_success': False
            }
            
            # 验证工具名称
            if tool_name:
                results['tool_name_validation'] = validate_tool_name(tool_name, max_length)
            
            # 验证参数契约
            if parameters and parameter_contract:
                results['parameter_validation'] = video_validator_capability.validate_parameter_contract(parameters, parameter_contract)
            
            # 判断整体成功状态
            tool_valid = results['tool_name_validation'] is None or results['tool_name_validation'].get('valid', False)
            param_valid = results['parameter_validation'] is None or results['parameter_validation'].get('valid', False)
            results['overall_success'] = tool_valid and param_valid
            
            return {
                'result': results,
                'insights': ['完成完整的API防御验证周期'],
                'facts': ['api_defense_validation_cycle_completed'],
                'memories': ['成功执行了完整的API防御验证周期']
            }
        
        else:
            return {
                'result': {'error': f'不支持的动作: {action}'},
                'insights': [f'API防御验证器不支持的动作: {action}'],
                'facts': [],
                'memories': []
            }
    
    except Exception as e:
        return {
            'result': {'error': f'执行过程中发生错误: {str(e)}'},
            'insights': [f'API防御验证器执行错误: {str(e)}'],
            'facts': [],
            'memories': []
        }

def validate_tool_name(tool_name, max_length=64):
    """验证工具名称长度"""
    if len(tool_name) > max_length:
        return {
            'valid': False,
            'original_name': tool_name,
            'truncated_name': tool_name[:max_length],
            'message': f'工具名称超过{max_length}字符限制！实际长度{len(tool_name)}'
        }
    else:
        return {
            'valid': True,
            'original_name': tool_name,
            'message': f'工具名称符合{max_length}字符限制'
        }