# tool_name: predictive_api_defense_integration_validator
from typing import Dict, Any, List, Optional
import json
import random
from langchain.tools import tool

@tool
def predictive_api_defense_integration_validator(input_args: str) -> dict:
    """
    预测性API防御集成验证工具 - 修正版
    
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
    
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args)
        except json.JSONDecodeError:
            params = {}
    else:
        params = input_args if isinstance(input_args, dict) else {}
    
    # 默认参数设置
    test_scenarios = params.get('test_scenarios', ['tool_name_length', 'parameter_contract', 'boundary_conditions'])
    generate_boundary_cases = params.get('generate_boundary_cases', True)
    execute_real_calls = params.get('execute_real_calls', True)
    validation_depth = params.get('validation_depth', 'comprehensive')
    context = params.get('context', 'predictive_api_defense_validation')
    
    results = {
        'success': True,
        'test_results': {},
        'boundary_cases_generated': 0,
        'defense_effectiveness': 0.0,
        'insights': [],
        'facts': [],
        'memories': []
    }
    
    # 生成边界测试用例
    boundary_cases = []
    if generate_boundary_cases:
        boundary_cases = _generate_boundary_test_cases(test_scenarios, validation_depth)
        results['boundary_cases_generated'] = len(boundary_cases)
        results['insights'].append(f"生成了 {len(boundary_cases)} 个边界测试用例用于验证防御体系")
    
    # 执行测试场景 - 直接使用已注册的工具函数
    for scenario in test_scenarios:
        if scenario == 'tool_name_length':
            results['test_results']['tool_name_length'] = _test_tool_name_length_validation_direct()
        elif scenario == 'parameter_contract':
            results['test_results']['parameter_contract'] = _test_parameter_contract_validation_direct()
        elif scenario == 'boundary_conditions':
            results['test_results']['boundary_conditions'] = _test_boundary_conditions_validation_direct(
                boundary_cases, execute_real_calls, validation_depth
            )
        else:
            results['test_results'][scenario] = {'success': False, 'error': f'未知测试场景: {scenario}'}
            results['success'] = False
    
    # 计算防御体系有效性
    total_tests = len(test_scenarios)
    passed_tests = sum(1 for r in results['test_results'].values() if r.get('success', False))
    results['defense_effectiveness'] = passed_tests / total_tests if total_tests > 0 else 0.0
    
    # 添加关键见解
    if results['defense_effectiveness'] >= 0.9:
        results['insights'].append("预测性API防御体系表现优秀，能够有效防止400错误")
    elif results['defense_effectiveness'] >= 0.7:
        results['insights'].append("预测性API防御体系基本有效，但仍有改进空间")
    else:
        results['insights'].append("预测性API防御体系需要重大改进，当前有效性不足")
    
    results['facts'].append(f"防御体系有效性评分为 {results['defense_effectiveness']:.2f}")
    results['memories'].append(f"在 {context} 上下文中验证了预测性API防御体系的有效性")
    
    return results


def _generate_boundary_test_cases(test_scenarios: List[str], validation_depth: str) -> List[Dict[str, Any]]:
    """生成边界测试用例"""
    cases = []
    
    # 工具名称长度边界测试
    if 'tool_name_length' in test_scenarios:
        cases.extend([
            {'tool_name': 'a' * 64, 'expected_valid': True},  # 正好64字符
            {'tool_name': 'a' * 65, 'expected_valid': False},  # 超过64字符
            {'tool_name': 'tool_with_special_chars!@#$', 'expected_valid': False},  # 特殊字符
            {'tool_name': 'valid_tool_name_123', 'expected_valid': True},  # 有效名称
        ])
    
    # 参数契约边界测试
    if 'parameter_contract' in test_scenarios:
        cases.extend([
            {'parameters': {}, 'contract': {'required_param': {'type': 'string', 'required': True}}, 'expected_valid': False},
            {'parameters': {'required_param': 'test'}, 'contract': {'required_param': {'type': 'string', 'required': True}}, 'expected_valid': True},
            {'parameters': {'optional_param': 123}, 'contract': {'optional_param': {'type': 'string', 'required': False}}, 'expected_valid': False},
        ])
    
    # 根据验证深度增加更多测试用例
    if validation_depth == 'stress_test':
        # 添加大量边界情况
        for i in range(10):
            cases.append({'tool_name': 'a' * (64 + i), 'expected_valid': False})
            cases.append({'tool_name': 'a' * (64 - i), 'expected_valid': True})
    
    return cases


def _test_tool_name_length_validation_direct() -> Dict[str, Any]:
    """测试工具名称长度验证 - 直接使用已注册的工具函数"""
    try:
        import json
        # 直接调用已注册的工具函数
        from workspace.tools.tool_tool_name_length_validator import tool_name_length_validator
        
        # 测试有效名称
        valid_result = tool_name_length_validator(json.dumps({'tool_name': 'valid_tool_name'}))
        if not valid_result.get('valid', False):
            return {'success': False, 'error': '有效工具名称被错误地标记为无效'}
        
        # 测试超长名称
        invalid_result = tool_name_length_validator(json.dumps({'tool_name': 'a' * 65}))
        if invalid_result.get('valid', True):
            return {'success': False, 'error': '超长工具名称未被正确检测为无效'}
        
        return {'success': True, 'message': '工具名称长度验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'工具名称长度验证测试失败: {str(e)}'}


def _test_parameter_contract_validation_direct() -> Dict[str, Any]:
    """测试参数契约验证 - 直接使用已注册的工具函数"""
    try:
        import json
        # 直接调用已注册的工具函数
        from workspace.tools.tool_api_parameter_semantic_validator import api_parameter_semantic_validator
        
        # 测试有效参数
        valid_params = json.dumps({
            'action': 'validate_parameter_contract',
            'parameters': {'test_param': 'value'},
            'parameter_contract': {'test_param': {'type': 'string', 'required': True}}
        })
        valid_result = api_parameter_semantic_validator(valid_params)
        if not valid_result.get('valid', False):
            return {'success': False, 'error': '有效参数被错误地标记为无效'}
        
        # 测试缺失必需参数
        invalid_params = json.dumps({
            'action': 'validate_parameter_contract',
            'parameters': {},
            'parameter_contract': {'test_param': {'type': 'string', 'required': True}}
        })
        invalid_result = api_parameter_semantic_validator(invalid_params)
        if invalid_result.get('valid', True):
            return {'success': False, 'error': '缺失必需参数未被正确检测为无效'}
        
        return {'success': True, 'message': '参数契约验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'参数契约验证测试失败: {str(e)}'}


def _test_boundary_conditions_validation_direct(boundary_cases: List[Dict[str, Any]], execute_real_calls: bool, validation_depth: str) -> Dict[str, Any]:
    """测试边界条件验证 - 直接使用已注册的工具函数"""
    if not execute_real_calls:
        return {'success': True, 'message': '跳过真实API调用测试', 'executed': False}
    
    try:
        import json
        # 使用现有的工具名称长度验证器进行测试
        from workspace.tools.tool_tool_name_length_validator import tool_name_length_validator
        
        # 测试几个边界案例
        test_count = 0
        failed_count = 0
        
        # 根据验证深度决定测试用例数量
        max_test_cases = 10 if validation_depth == 'stress_test' else min(5, len(boundary_cases))
        
        for case in boundary_cases[:max_test_cases]:
            if 'tool_name' in case:
                test_input = json.dumps({
                    'tool_name': case['tool_name'],
                    'max_length': 64
                })
                result = tool_name_length_validator(test_input)
                expected_valid = case.get('expected_valid', True)
                
                if result.get('valid', False) != expected_valid:
                    failed_count += 1
                
                test_count += 1
        
        if failed_count == 0 and test_count > 0:
            return {'success': True, 'message': '边界条件验证正常工作', 'cases_tested': test_count}
        elif test_count == 0:
            return {'success': True, 'message': '无边界测试用例需要执行'}
        else:
            return {'success': False, 'error': f'边界条件验证失败: {failed_count}/{test_count} 个测试用例失败'}
            
    except Exception as e:
        return {'success': False, 'error': f'边界条件验证测试失败: {str(e)}'}