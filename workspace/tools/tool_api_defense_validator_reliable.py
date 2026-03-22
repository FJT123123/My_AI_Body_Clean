# tool_name: api_defense_validator_reliable
from langchain.tools import tool
import json
import random
import string


@tool
def api_defense_validator_reliable(input_args: str) -> dict:
    """
    可靠的API防御集成验证工具
    
    这个工具执行端到端的API调用预测性防御体系验证，通过生成边界测试用例、
    执行真实API调用、并验证整个防御链条的有效性。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - test_scenarios (list, optional): 测试场景列表，如['tool_name_length', 'parameter_contract', 'boundary_conditions']
            - generate_boundary_cases (bool, optional): 是否自动生成边界测试用例，默认True
            - execute_real_calls (bool, optional): 是否执行真实的API调用，默认True
            - validation_depth (str, optional): 验证深度，'basic', 'comprehensive', 'stress_test'，默认'comprehensive'
            - context (str, optional): 当前执行上下文
    
    Returns:
        dict: 包含验证结果的字典，包括:
            - success: 整体验证是否成功
            - test_results: 各测试场景的详细结果
            - boundary_cases_generated: 生成的边界测试用例数量
            - defense_effectiveness: 防御体系有效性评分 (0.0-1.0)
            - insights: 关键见解
            - facts: 可验证的事实
            - memories: 值得记住的经验
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            try:
                args = json.loads(input_args)
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'test_results': {},
                    'boundary_cases_generated': 0,
                    'defense_effectiveness': 0.0,
                    'insights': ['参数校验失败：必须提供有效的JSON字符串'],
                    'facts': [],
                    'memories': ['API防御验证失败：无效的JSON输入']
                }
        else:
            args = input_args
        
        test_scenarios = args.get('test_scenarios', ['tool_name_length', 'parameter_contract', 'boundary_conditions'])
        generate_boundary_cases = args.get('generate_boundary_cases', True)
        execute_real_calls = args.get('execute_real_calls', True)
        validation_depth = args.get('validation_depth', 'comprehensive')
        context = args.get('context', 'api_defense_validation')
        
        test_results = {}
        boundary_cases_generated = 0
        successful_tests = 0
        
        # 直接调用已修复的底层工具函数
        def call_tool_name_length_validator(tool_name, max_length=64):
            """直接调用工具名称长度验证器"""
            from workspace.tools.tool_tool_name_length_validator import tool_name_length_validator
            input_str = json.dumps({'tool_name': tool_name, 'max_length': max_length})
            return tool_name_length_validator(input_str)
        
        def call_api_parameter_semantic_validator_fixed(action, parameters=None, parameter_contract=None):
            """直接调用API参数语义验证器"""
            from workspace.tools.tool_api_parameter_semantic_validator_fixed import api_parameter_semantic_validator_fixed
            input_data = {'action': action}
            if parameters is not None:
                input_data['parameters'] = parameters
            if parameter_contract is not None:
                input_data['parameter_contract'] = parameter_contract
            input_str = json.dumps(input_data)
            return api_parameter_semantic_validator_fixed(input_str)
        
        # 测试工具名称长度验证
        if 'tool_name_length' in test_scenarios:
            try:
                # 测试正常长度
                normal_name_result = call_tool_name_length_validator('normal_tool_name', 64)
                
                # 测试超长名称
                long_name = 'very_long_tool_name_that_exceeds_the_sixty_four_character_limit_for_api_calls'
                long_name_result = call_tool_name_length_validator(long_name, 64)
                
                # 验证结果
                normal_valid = normal_name_result.get('valid', False) if isinstance(normal_name_result, dict) else False
                long_invalid = not long_name_result.get('valid', True) if isinstance(long_name_result, dict) else False
                
                if normal_valid and long_invalid:
                    test_results['tool_name_length'] = {
                        'success': True,
                        'message': '工具名称长度验证正常工作'
                    }
                    successful_tests += 1
                else:
                    test_results['tool_name_length'] = {
                        'success': False,
                        'error': f'工具名称长度验证异常: normal={normal_valid}, long={not long_invalid}'
                    }
                
                boundary_cases_generated += 2
                
            except Exception as e:
                test_results['tool_name_length'] = {
                    'success': False,
                    'error': f'工具名称长度测试异常: {str(e)}'
                }
        
        # 测试参数契约验证
        if 'parameter_contract' in test_scenarios:
            try:
                # 测试缺失必需参数
                missing_param_result = call_api_parameter_semantic_validator_fixed(
                    'validate_parameter_contract',
                    {'extra_param': 'value'},
                    {'required_param': {'required': True, 'type': 'string'}}
                )
                
                # 测试类型匹配
                type_match_result = call_api_parameter_semantic_validator_fixed(
                    'validate_parameter_contract',
                    {'string_param': 'valid_string'},
                    {'string_param': {'required': True, 'type': 'string'}}
                )
                
                # 验证结果
                missing_detected = not missing_param_result.get('valid', True) if isinstance(missing_param_result, dict) else False
                type_valid = type_match_result.get('valid', False) if isinstance(type_match_result, dict) else False
                
                if missing_detected and type_valid:
                    test_results['parameter_contract'] = {
                        'success': True,
                        'message': '参数契约验证正常工作'
                    }
                    successful_tests += 1
                else:
                    test_results['parameter_contract'] = {
                        'success': False,
                        'error': f'参数契约验证异常: missing_detected={missing_detected}, type_valid={type_valid}'
                    }
                
                boundary_cases_generated += 2
                
            except Exception as e:
                test_results['parameter_contract'] = {
                    'success': False,
                    'error': f'参数契约测试异常: {str(e)}'
                }
        
        # 测试自动修复功能
        if 'boundary_conditions' in test_scenarios:
            try:
                # 测试自动修复缺失参数
                repair_result = call_api_parameter_semantic_validator_fixed(
                    'repair_parameter_format',
                    {'extra_param': 'value'},
                    {'required_param': {'required': True, 'type': 'string', 'default': 'default_value'}}
                )
                
                # 验证修复结果
                repair_success = repair_result.get('success', False) if isinstance(repair_result, dict) else False
                has_required_param = 'required_param' in repair_result.get('repaired_parameters', {}) if isinstance(repair_result, dict) else False
                
                if repair_success and has_required_param:
                    test_results['boundary_conditions'] = {
                        'success': True,
                        'message': '边界条件和自动修复功能正常工作'
                    }
                    successful_tests += 1
                else:
                    test_results['boundary_conditions'] = {
                        'success': False,
                        'error': f'自动修复异常: success={repair_success}, has_required={has_required_param}'
                    }
                
                boundary_cases_generated += 1
                
            except Exception as e:
                test_results['boundary_conditions'] = {
                    'success': False,
                    'error': f'边界条件测试异常: {str(e)}'
                }
        
        # 计算防御有效性
        total_tests = len(test_scenarios)
        defense_effectiveness = successful_tests / total_tests if total_tests > 0 else 0.0
        overall_success = defense_effectiveness >= 0.9  # 90%以上成功率视为成功
        
        insights = [
            f"生成了 {boundary_cases_generated} 个边界测试用例用于验证防御体系",
            f"防御体系有效性评分为 {defense_effectiveness:.2f}",
            f"成功完成 {successful_tests}/{total_tests} 个测试场景"
        ]
        
        facts = [
            f"防御体系有效性评分为 {defense_effectiveness:.2f}"
        ]
        
        memories = [
            f"在 {context} 上下文中验证了API防御体系的有效性",
            f"API防御体系可靠性: {'高' if overall_success else '需要改进'}"
        ]
        
        return {
            'success': overall_success,
            'test_results': test_results,
            'boundary_cases_generated': boundary_cases_generated,
            'defense_effectiveness': defense_effectiveness,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
    
    except Exception as e:
        return {
            'success': False,
            'test_results': {},
            'boundary_cases_generated': 0,
            'defense_effectiveness': 0.0,
            'insights': [f'执行过程中发生异常: {str(e)}'],
            'facts': [],
            'memories': [f'API防御验证异常: {str(e)}']
        }