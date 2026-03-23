# tool_name: integration_validation_coordinator

from langchain.tools import tool
import json
from typing import Dict, Any, List

@tool
def integration_validation_coordinator(input_params: str) -> Dict[str, Any]:
    """
    集成验证协调器：验证统一API参数验证层与类型沙盒验证器的协同效果
    
    Args:
        input_params (str): JSON字符串，包含：
            - test_scenarios: 测试场景列表，每个包含parameters, parameter_contract, patch_content
            - integration_modes: 集成模式列表 ["sequential", "parallel", "nested"]
            - stress_factors: 压力因子配置
    
    Returns:
        dict: 集成验证结果，包含：
            - integration_score: 集成有效性评分 (0-1)
            - failure_patterns: 识别出的失效模式
            - performance_metrics: 性能指标
            - recommendations: 优化建议
    """
    try:
        # 解析输入参数
        if isinstance(input_params, str):
            params = json.loads(input_params)
        else:
            params = input_params
            
        test_scenarios = params.get('test_scenarios', [])
        integration_modes = params.get('integration_modes', ['sequential'])
        stress_factors = params.get('stress_factors', {})
        
        results = {
            'integration_score': 0.0,
            'failure_patterns': [],
            'performance_metrics': {
                'total_scenarios': len(test_scenarios),
                'total_modes': len(integration_modes),
                'failure_rate': 0.0,
                'average_score': 0.0
            },
            'recommendations': []
        }
        
        # 如果没有测试场景，返回空结果
        if not test_scenarios:
            results['recommendations'].append('未提供测试场景，请提供有效的测试场景')
            return results
            
        # 执行集成验证
        total_score = 0.0
        failure_count = 0
        
        for mode in integration_modes:
            for i, scenario in enumerate(test_scenarios):
                scenario_name = scenario.get('name', f'scenario_{i+1}')
                parameters = scenario.get('parameters', {})
                parameter_contract = scenario.get('parameter_contract', {})
                patch_content = scenario.get('patch_content', '')
                
                # 验证参数契约
                try:
                    param_validation_result = unified_api_parameter_validation_layer.invoke({
                        'parameters': parameters,
                        'parameter_contract': parameter_contract
                    })
                    param_valid = param_validation_result.get('is_valid', False)
                except Exception as e:
                    param_valid = False
                    results['failure_patterns'].append({
                        'mode': mode,
                        'scenario': scenario_name,
                        'failure_type': 'parameter_validation_error',
                        'details': str(e)
                    })
                    failure_count += 1
                    continue
                
                # 验证类型沙盒（如果提供类型契约）
                type_valid = True
                if 'type_contract' in scenario:
                    try:
                        type_validation_result = type_sandbox_validator.invoke({
                            'parameters': parameters,
                            'type_contract': scenario.get('type_contract', {}),
                            'validation_mode': 'strict'
                        })
                        type_valid = type_validation_result.get('is_valid', True)
                    except Exception as e:
                        type_valid = False
                        results['failure_patterns'].append({
                            'mode': mode,
                            'scenario': scenario_name,
                            'failure_type': 'type_validation_error',
                            'details': str(e)
                        })
                        failure_count += 1
                        continue
                
                # 计算场景得分
                if param_valid and type_valid:
                    scenario_score = 1.0
                elif param_valid or type_valid:
                    scenario_score = 0.5
                else:
                    scenario_score = 0.0
                    failure_count += 1
                    
                total_score += scenario_score
                
                if scenario_score < 1.0:
                    results['failure_patterns'].append({
                        'mode': mode,
                        'scenario': scenario_name,
                        'failure_type': 'partial_validation_failure',
                        'details': f'参数验证: {param_valid}, 类型验证: {type_valid}'
                    })
        
        # 计算最终结果
        total_tests = len(test_scenarios) * len(integration_modes)
        if total_tests > 0:
            results['integration_score'] = total_score / total_tests
            results['performance_metrics']['failure_rate'] = failure_count / total_tests
            results['performance_metrics']['average_score'] = results['integration_score']
            
        # 生成建议
        if results['integration_score'] >= 0.8:
            results['recommendations'].append('集成验证通过，可以安全使用')
        elif results['integration_score'] >= 0.5:
            results['recommendations'].append('集成验证部分通过，建议修复失败场景')
        else:
            results['recommendations'].append('集成验证失败，需要全面修复验证逻辑')
            
        results['recommendations'].extend([
            "需要加强参数契约与类型沙盒的错误处理一致性",
            "建议增加边界条件和异常场景的测试覆盖率"
        ])
        
        return results
        
    except Exception as e:
        return {
            'integration_score': 0.0,
            'failure_patterns': [{
                'mode': 'unknown',
                'scenario': 'unknown',
                'failure_type': 'integration_error',
                'details': str(e)
            }],
            'performance_metrics': {
                'total_scenarios': 0,
                'total_modes': 0,
                'failure_rate': 1.0,
                'average_score': 0.0
            },
            'recommendations': [
                "集成验证过程中发生错误，请检查输入参数格式",
                "需要加强参数契约与类型沙盒的错误处理一致性",
                "建议增加边界条件和异常场景的测试覆盖率"
            ]
        }