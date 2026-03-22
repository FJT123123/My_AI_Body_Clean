# tool_name: api_defense_coordinator
from langchain.tools import tool
import json
import traceback

@tool
def api_defense_coordinator(input_args: str) -> dict:
    """
    智能API防御与自我修复协调器
    
    这个工具整合了现有的API参数验证、工具名称验证、错误映射和自动修复功能，
    提供端到端的API调用保护和自我修复能力。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str): 要调用的工具名称
            - parameters (dict): 工具参数字典
            - parameter_contract (dict, optional): 参数契约定义
            - context (str, optional): 执行上下文
            - auto_repair (bool, optional): 是否自动修复，默认True
    
    Returns:
        dict: 包含验证结果、修复状态、执行结果和经验记忆的字典
    """
    # 运行时注入API
    from openclaw_continuity.api import invoke_tool, load_capability_module
    
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            try:
                args_dict = json.loads(input_args)
            except json.JSONDecodeError:
                return {
                    'result': {'error': '缺少有效的JSON格式输入参数'},
                    'insights': ['参数解析失败：输入必须是有效的JSON字符串'],
                    'facts': [],
                    'memories': []
                }
        else:
            args_dict = input_args
    
        # 验证必需参数
        tool_name = args_dict.get('tool_name')
        parameters = args_dict.get('parameters', {})
        parameter_contract = args_dict.get('parameter_contract', {})
        context = args_dict.get('context', 'api_defense_coordinator')
        auto_repair = args_dict.get('auto_repair', True)
    
        if not tool_name:
            return {
                'result': {'error': '缺少 tool_name 参数'},
                'insights': ['参数校验失败：必须提供tool_name'],
                'facts': [],
                'memories': []
            }
    
        if not isinstance(parameters, dict):
            return {
                'result': {'error': 'parameters 必须是字典类型'},
                'insights': ['参数校验失败：parameters必须是字典'],
                'facts': [],
                'memories': []
            }
    
        # 第一步：工具名称验证
        tool_name_validation_input = json.dumps({
            'tool_name': tool_name,
            'max_length': 64
        })
        tool_name_result = invoke_tool('tool_enhanced_tool_name_validator', tool_name_validation_input)
    
        safe_tool_name = tool_name_result.get('safe_name', tool_name)
        tool_name_valid = tool_name_result.get('is_valid', False)
    
        # 第二步：参数契约验证和修复
        validation_input = json.dumps({
            'action': 'validate_and_repair',
            'tool_name': safe_tool_name,
            'parameters': parameters,
            'parameter_contract': parameter_contract,
            'auto_apply': auto_repair
        })
        validation_result = invoke_tool('tool_enhanced_api_parameter_defense_validator', validation_input)
    
        repaired_parameters = validation_result.get('repaired_parameters', parameters)
        validation_success = validation_result.get('success', False)
    
        # 第三步：如果验证通过且需要执行，则调用目标工具
        execution_result = None
        if validation_success and auto_repair:
            try:
                # 将修复后的参数转换为JSON字符串
                repaired_params_str = json.dumps(repaired_parameters)
                
                # 使用invoke_tool函数调用目标工具
                execution_result = invoke_tool(safe_tool_name, repaired_params_str)
                
                # 如果执行成功，记录成功经验
                if execution_result and 'error' not in str(execution_result).lower():
                    success_memory = f"成功使用智能API防御协调器调用{safe_tool_name}，参数已自动修复并执行成功"
                    # 记住这个经验（假设）
                    if 'memories' in execution_result:
                        execution_result['memories'] = execution_result.get('memories', []) + [success_memory]
                    else:
                        execution_result['memories'] = [success_memory]
                        
            except Exception as e:
                error_msg = f"工具执行失败: {str(e)}"
                execution_result = {'error': error_msg}
                
                # 记录失败经验用于改进
                failure_memory = f"API防御协调器执行{safe_tool_name}时失败: {str(e)}"
                if 'memories' in execution_result:
                    execution_result['memories'] = execution_result.get('memories', []) + [failure_memory]
                else:
                    execution_result['memories'] = [failure_memory]
    
        # 第四步：生成综合报告
        report = {
            'tool_name_validation': {
                'original_name': tool_name,
                'safe_name': safe_tool_name,
                'is_valid': tool_name_valid,
                'issues': tool_name_result.get('issues', [])
            },
            'parameter_validation': {
                'success': validation_success,
                'original_parameters': parameters,
                'repaired_parameters': repaired_parameters,
                'issues_found': validation_result.get('issues_found', []),
                'repair_applied': validation_result.get('repair_applied', False)
            },
            'execution_result': execution_result,
            'overall_status': 'success' if validation_success and execution_result and 'error' not in str(execution_result).lower() else 'failed'
        }
    
        # 生成见解和事实
        insights = []
        facts = []
    
        if not tool_name_valid:
            insights.append(f"工具名称 '{tool_name}' 需要修正以符合API约束")
            facts.append("工具名称长度限制为64字符，只能包含字母、数字和下划线")
    
        if validation_result.get('repair_applied'):
            insights.append("参数已自动修复以符合契约要求")
            facts.append("API参数契约验证成功应用了自动修复")
    
        if report['overall_status'] == 'success':
            insights.append("智能API防御协调器成功完成端到端验证和执行")
            facts.append("API 400错误预防机制有效工作")
    
        return {
            'result': report,
            'insights': insights,
            'facts': facts,
            'memories': []
        }
    
    except Exception as e:
        error_trace = traceback.format_exc()
        return {
            'result': {'error': f'API防御协调器执行失败: {str(e)}', 'traceback': error_trace},
            'insights': [f'内部错误：{str(e)}'],
            'facts': ['API防御协调器遇到未预期的内部错误'],
            'memories': []
        }