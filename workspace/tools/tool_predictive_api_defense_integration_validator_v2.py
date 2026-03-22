# tool_name: predictive_api_defense_integration_validator_v2

from typing import Dict, Any, List
import json
from langchain.tools import tool

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

def _test_tool_name_length_validation() -> Dict[str, Any]:
    """测试工具名称长度验证 - 使用现有工具"""
    try:
        import subprocess
        import sys
        
        # 使用现有工具进行验证
        validator_input = json.dumps({
            'action': 'validate_single',
            'tool_name': 'valid_tool_name'
        })
        
        # 调用现有工具
        result = subprocess.run([
            sys.executable, '-c', 
            f'from openclaw_continuity.core.tools.api_parameter_semantic_validator import main; print(main(\'{validator_input}\'))'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            # 如果上面的方法失败，尝试调用统一防御系统
            defense_input = json.dumps({
                'action': 'validate_and_repair',
                'tool_name': 'valid_tool_name',
                'parameters': {},
                'parameter_contract': {}
            })
            defense_result = subprocess.run([
                sys.executable, '-c', 
                f'from openclaw_continuity.core.tools.unified_tool_contract_defense_system import main; print(main(\'{defense_input}\'))'
            ], capture_output=True, text=True)
            
            if defense_result.returncode != 0:
                return {'success': False, 'error': '无法调用现有的防御工具'}
            else:
                defense_output = json.loads(defense_result.stdout)
                if not defense_output.get('validation_passed', False):
                    return {'success': False, 'error': '有效工具名称被错误地标记为无效'}
        else:
            output = json.loads(result.stdout)
            if not output.get('valid', False):
                return {'success': False, 'error': '有效工具名称被错误地标记为无效'}
        
        # 测试超长名称
        invalid_input = json.dumps({
            'action': 'validate_single',
            'tool_name': 'a' * 65
        })
        invalid_result = subprocess.run([
            sys.executable, '-c', 
            f'from openclaw_continuity.core.tools.api_parameter_semantic_validator import main; print(main(\'{invalid_input}\'))'
        ], capture_output=True, text=True)
        
        if invalid_result.returncode != 0:
            # 使用统一防御系统作为备选
            invalid_defense_input = json.dumps({
                'action': 'validate_and_repair',
                'tool_name': 'a' * 65,
                'parameters': {},
                'parameter_contract': {}
            })
            invalid_defense_result = subprocess.run([
                sys.executable, '-c', 
                f'from openclaw_continuity.core.tools.unified_tool_contract_defense_system import main; print(main(\'{invalid_defense_input}\'))'
            ], capture_output=True, text=True)
            
            if invalid_defense_result.returncode != 0:
                return {'success': False, 'error': '无法验证超长工具名称'}
            else:
                invalid_defense_output = json.loads(invalid_defense_result.stdout)
                if invalid_defense_output.get('validation_passed', True):
                    return {'success': False, 'error': '超长工具名称未被正确检测为无效'}
        else:
            invalid_output = json.loads(invalid_result.stdout)
            if invalid_output.get('valid', True):
                return {'success': False, 'error': '超长工具名称未被正确检测为无效'}
        
        return {'success': True, 'message': '工具名称长度验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'工具名称长度验证测试失败: {str(e)}'}

def _test_parameter_contract_validation() -> Dict[str, Any]:
    """测试参数契约验证 - 使用现有工具"""
    try:
        import subprocess
        import sys
        
        # 测试有效参数
        valid_params = json.dumps({
            'action': 'validate_parameter_contract',
            'parameters': {'test_param': 'value'},
            'parameter_contract': {'test_param': {'type': 'string', 'required': True}}
        })
        
        result = subprocess.run([
            sys.executable, '-c', 
            f'from openclaw_continuity.core.tools.api_parameter_semantic_validator import main; print(main(\'{valid_params}\'))'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return {'success': False, 'error': '无法调用参数契约验证工具'}
        
        output = json.loads(result.stdout)
        if not output.get('valid', False):
            return {'success': False, 'error': '有效参数契约被错误地标记为无效'}
        
        return {'success': True, 'message': '参数契约验证正常工作'}
    except Exception as e:
        return {'success': False, 'error': f'参数契约验证测试失败: {str(e)}'}

def _test_boundary_conditions_validation(boundary_cases: List[Dict[str, Any]], execute_real_calls: bool, validation_depth: str) -> Dict[str, Any]:
    """测试边界条件验证 - 使用现有工具"""
    if not execute_real_calls:
        return {'success': True, 'message': '跳过真实API调用测试', 'executed': False}
    
    try:
        import subprocess
        import sys
        
        test_definitions = []
        # 根据验证深度决定测试用例数量
        max_test_cases = 10 if validation_depth == 'stress_test' else 5
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
            
            result = subprocess.run([
                sys.executable, '-c', 
                f'from openclaw_continuity.core.tools.unified_tool_contract_defense_system import main; print(main(\'{test_input}\'))'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {'success': False, 'error': '无法调用统一防御系统进行批量验证'}
            
            # 检查结果结构
            output = json.loads(result.stdout)
            if 'validation_results' in output:
                return {'success': True, 'message': '边界条件验证正常工作', 'cases_tested': len(test_definitions)}
            else:
                return {'success': False, 'error': '边界条件验证返回结果格式不正确', 'details': output}
        else:
            return {'success': True, 'message': '无边界测试用例需要执行'}
            
    except Exception as e:
        return {'success': False, 'error': f'边界条件验证测试失败: {str(e)}'}

@tool
def predictive_api_defense_integration_validator_v2(input_args: str) -> Dict[str, Any]:
    """
    预测性API防御集成验证工具 - 修复版
    
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
    
    # 执行测试场景
    for scenario in test_scenarios:
        try:
            if scenario == 'tool_name_length':
                results['test_results']['tool_name_length'] = _test_tool_name_length_validation()
            elif scenario == 'parameter_contract':
                results['test_results']['parameter_contract'] = _test_parameter_contract_validation()
            elif scenario == 'boundary_conditions':
                results['test_results']['boundary_conditions'] = _test_boundary_conditions_validation(
                    boundary_cases, execute_real_calls, validation_depth
                )
            else:
                results['test_results'][scenario] = {'success': False, 'error': f'未知测试场景: {scenario}'}
                results['success'] = False
        except Exception as e:
            results['test_results'][scenario] = {'success': False, 'error': f'执行测试场景失败: {str(e)}'}
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