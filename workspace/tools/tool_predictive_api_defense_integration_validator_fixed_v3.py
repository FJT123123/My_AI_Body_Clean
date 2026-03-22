# tool_name: predictive_api_defense_integration_validator_fixed_v3

from typing import Dict, Any, List, Optional
import json
import random
from langchain.tools import tool

@tool
def predictive_api_defense_integration_validator_fixed_v3(input_args: str) -> dict:
    """
    预测性API防御集成验证工具 - 修复版V3
    
    这个工具执行端到端的API调用预测性防御体系验证，通过生成边界测试用例、
    执行真实API调用、并验证整个防御链条的有效性。
    
    使用正确的工具调用机制，通过run_skill来调用其他验证工具。
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
    
    # 执行测试场景 - 使用正确的工具调用方式
    for scenario in test_scenarios:
        if scenario == 'tool_name_length':
            results['test_results']['tool_name_length'] = _test_tool_name_length_validation_fixed()
        elif scenario == 'parameter_contract':
            results['test_results']['parameter_contract'] = _test_parameter_contract_validation_fixed()
        elif scenario == 'boundary_conditions':
            results['test_results']['boundary_conditions'] = _test_boundary_conditions_validation_fixed(
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
            {'tool_name': 'valid_tool_name_123', 'expected_valid': True},  # 有效名称
        ])
    
    # 参数契约边界测试
    if 'parameter_contract' in test_scenarios:
        cases.extend([
            {'parameters': {}, 'contract': {'required_param': {'type': 'string', 'required': True}}, 'expected_valid': False},
            {'parameters': {'required_param': 'test'}, 'contract': {'required_param': {'type': 'string', 'required': True}}, 'expected_valid': True},
        ])
    
    # 根据验证深度增加更多测试用例
    if validation_depth == 'stress_test':
        # 添加大量边界情况
        for i in range(5):
            cases.append({'tool_name': 'a' * (64 + i), 'expected_valid': False})
            cases.append({'tool_name': 'a' * (64 - i), 'expected_valid': True})
    
    return cases


def _test_tool_name_length_validation_fixed() -> Dict[str, Any]:
    """测试工具名称长度验证 - 使用正确的工具调用"""
    try:
        from workspace.skills.skill_list_my_skills import list_my_skills
        from workspace.skills.skill_run_skill import run_skill
        
        # 检查工具是否存在
        skills_list = list_my_skills()
        if "tool_name_length_validator" not in str(skills_list):
            return {'success': False, 'error': 'tool_name_length_validator工具未找到'}
        
        # 测试有效名称
        valid_input = json.dumps({'tool_name': 'valid_tool_name'})
        valid_result = run_skill("tool_name_length_validator", valid_input)
        
        # 处理结果 - 可能是字符串或字典
        if isinstance(valid_result, str):
            try:
                valid_result = json.loads(valid_result)
            except:
                return {'success': False, 'error': '工具返回结果无法解析'}
        
        if not valid_result.get('valid', False):
            return {'success': False, 'error': '有效工具名称被错误地标记为无效'}
        
        # 测试超长名称
        invalid_input = json.dumps({'tool_name': 'a' * 65})
        invalid_result = run_skill("tool_name_length_validator", invalid_input)
        
        if isinstance(invalid_result, str):
            try:
                invalid_result = json.loads(invalid_result)
            except:
                return {'success': False, 'error': '工具返回结果无法解析'}
        
        if invalid_result.get('valid', True):
            return {'success': False, 'error': '超长工具名称未被正确检测为无效'}
        
        return {'success': True, 'message': '工具名称长度验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'工具名称长度验证测试失败: {str(e)}'}


def _test_parameter_contract_validation_fixed() -> Dict[str, Any]:
    """测试参数契约验证 - 使用正确的工具调用"""
    try:
        from workspace.skills.skill_list_my_skills import list_my_skills
        from workspace.skills.skill_run_skill import run_skill
        
        # 检查工具是否存在
        skills_list = list_my_skills()
        if "enhanced_api_parameter_validator" not in str(skills_list):
            return {'success': False, 'error': 'enhanced_api_parameter_validator工具未找到'}
        
        # 测试有效参数
        valid_params = json.dumps({
            'action': 'validate_parameter_contract',
            'parameters': {'test_param': 'value'},
            'parameter_contract': {'test_param': {'type': 'string', 'required': True}}
        })
        valid_result = run_skill("enhanced_api_parameter_validator", valid_params)
        
        if isinstance(valid_result, str):
            try:
                valid_result = json.loads(valid_result)
            except:
                return {'success': False, 'error': '工具返回结果无法解析'}
        
        if not valid_result.get('valid', False):
            return {'success': False, 'error': '有效参数被错误地标记为无效'}
        
        # 测试缺失必需参数
        invalid_params = json.dumps({
            'action': 'validate_parameter_contract',
            'parameters': {},
            'parameter_contract': {'test_param': {'type': 'string', 'required': True}}
        })
        invalid_result = run_skill("enhanced_api_parameter_validator", invalid_params)
        
        if isinstance(invalid_result, str):
            try:
                invalid_result = json.loads(invalid_result)
            except:
                return {'success': False, 'error': '工具返回结果无法解析'}
        
        if invalid_result.get('valid', True):
            return {'success': False, 'error': '缺失必需参数未被正确检测为无效'}
        
        return {'success': True, 'message': '参数契约验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'参数契约验证测试失败: {str(e)}'}


def _test_boundary_conditions_validation_fixed(boundary_cases: List[Dict[str, Any]], execute_real_calls: bool, validation_depth: str) -> Dict[str, Any]:
    """测试边界条件验证 - 使用正确的工具调用"""
    if not execute_real_calls:
        return {'success': True, 'message': '跳过真实API调用测试', 'executed': False}
    
    try:
        from workspace.skills.skill_list_my_skills import list_my_skills
        from workspace.skills.skill_run_skill import run_skill
        
        # 检查工具是否存在
        skills_list = list_my_skills()
        if "unified_tool_contract_defense_system" not in str(skills_list):
            return {'success': False, 'error': 'unified_tool_contract_defense_system工具未找到'}
        
        test_definitions = []
        # 根据验证深度决定测试用例数量
        max_test_cases = 5 if validation_depth == 'stress_test' else 3
        for case in boundary_cases[:max_test_cases]:  # 限制测试数量
            if 'tool_name' in case:
                test_definitions.append({
                    'tool_name': case['tool_name'],
                    'parameters': {},
                    'parameter_contract': {}
                })
        
        if test_definitions:
            test_input = json.dumps({
                'action': 'batch_validate',
                'tool_definitions': test_definitions
            })
            result = run_skill("unified_tool_contract_defense_system", test_input)
            
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except:
                    return {'success': False, 'error': '工具返回结果无法解析'}
            
            if result.get('overall_success', False):
                return {'success': True, 'message': '边界条件验证正常工作', 'cases_tested': len(test_definitions)}
            else:
                return {'success': False, 'error': '边界条件验证失败', 'details': result.get('validation_results', [])}
        else:
            return {'success': True, 'message': '无边界测试用例需要执行'}
            
    except Exception as e:
        return {'success': False, 'error': f'边界条件验证测试失败: {str(e)}'}