# tool_name: memory_param_sandbox_tester

from typing import Dict, Any, List
from langchain.tools import tool
import json

@tool
def memory_param_sandbox_tester(input_params: str) -> Dict[str, Any]:
    """
    记忆系统参数验证沙盒测试框架：在隔离环境中测试记忆系统相关参数的验证逻辑
    
    Args:
        input_params (str): JSON字符串，包含以下字段：
            - test_scenarios: 测试场景列表，每个场景包含parameters和expected_result
            - parameter_contract: 参数契约定义（与unified_api_parameter_validation_layer兼容）
            - memory_weights: 记忆权重配置（用于memory_system_validation_triad）
            - validation_modes: 要测试的验证模式列表 ["strict", "lenient", "repair"]
    
    Returns:
        dict: 沙盒测试结果，包含：
            - test_summary: 测试概要（总场景数、通过数、失败数）
            - detailed_results: 详细测试结果列表
            - validation_insights: 验证洞察
            - recommendations: 优化建议
    """
    # 解析输入参数
    if isinstance(input_params, str):
        params = json.loads(input_params)
    else:
        params = input_params
    
    test_scenarios = params.get('test_scenarios', [])
    parameter_contract = params.get('parameter_contract', {})
    memory_weights = params.get('memory_weights', {})
    validation_modes = params.get('validation_modes', ['strict'])
    
    results = {
        'test_summary': {
            'total_scenarios': len(test_scenarios),
            'passed': 0,
            'failed': 0,
            'error_count': 0
        },
        'detailed_results': [],
        'validation_insights': [],
        'recommendations': []
    }
    
    # 获取全局验证工具引用
    unified_validator = globals()['unified_api_parameter_validation_layer']
    memory_validator = globals()['memory_system_validation_triad']
    
    for i, scenario in enumerate(test_scenarios):
        scenario_result = {
            'scenario_id': i,
            'input_parameters': scenario.get('parameters', {}),
            'expected_result': scenario.get('expected_result', {}),
            'mode_results': {}
        }
        
        for mode in validation_modes:
            try:
                # 使用统一API参数验证层进行验证
                validator_input = json.dumps({
                    'parameters': scenario.get('parameters', {}),
                    'parameter_contract': parameter_contract,
                    'validation_mode': mode
                })
                
                validation_result = unified_validator(validator_input)
                
                # 记录结果
                scenario_result['mode_results'][mode] = {
                    'is_valid': validation_result.get('is_valid', False),
                    'issues': validation_result.get('issues', []),
                    'recommendations': validation_result.get('recommendations', []),
                    'validated_parameters': validation_result.get('validated_parameters', {})
                }
                
                # 检查是否符合预期
                expected_valid = scenario.get('expected_result', {}).get('is_valid', True)
                actual_valid = validation_result.get('is_valid', False)
                
                if expected_valid == actual_valid:
                    results['test_summary']['passed'] += 1
                else:
                    results['test_summary']['failed'] += 1
                    
            except Exception as e:
                results['test_summary']['error_count'] += 1
                scenario_result['mode_results'][mode] = {
                    'error': str(e),
                    'is_valid': False
                }
        
        results['detailed_results'].append(scenario_result)
    
    # 如果提供了记忆权重，运行三维验证
    if memory_weights and results['test_summary']['total_scenarios'] > 0:
        # 构造修复数据（基于测试结果）
        repair_data = {
            'total_repairs': results['test_summary']['total_scenarios'],
            'successful_repairs': results['test_summary']['passed']
        }
        
        triad_input = json.dumps({
            'patch_content': 'memory_param_validation_logic',
            'memory_weights': memory_weights,
            'repair_data': repair_data,
            'validation_mode': 'full'
        })
        
        triad_result = memory_validator(triad_input)
        results['triad_validation'] = triad_result
    
    # 生成洞察和建议
    pass_rate = results['test_summary']['passed'] / max(results['test_summary']['total_scenarios'], 1)
    if pass_rate < 0.8:
        results['validation_insights'].append(f"参数验证通过率较低 ({pass_rate:.2%})，可能存在契约定义问题")
        results['recommendations'].append("检查参数契约定义是否与实际使用场景匹配")
    
    if results['test_summary']['error_count'] > 0:
        results['validation_insights'].append(f"测试过程中出现 {results['test_summary']['error_count']} 个错误")
        results['recommendations'].append("检查测试场景的参数格式是否正确")
    
    return results