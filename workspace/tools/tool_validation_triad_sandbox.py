# tool_name: validation_triad_sandbox

from langchain.tools import tool
import json

@tool
def validation_triad_sandbox(test_config_json: str) -> dict:
    """
    端到端验证框架三元组测试沙盒
    
    Args:
        test_config_json (str): JSON字符串，包含测试配置
        
    Returns:
        dict: 完整的测试结果报告
    """
    try:
        # 解析输入参数
        if isinstance(test_config_json, str):
            test_config = json.loads(test_config_json)
        else:
            test_config = test_config_json
            
        # 获取测试配置
        test_scenarios = test_config.get('test_scenarios', [])
        
        results = {
            'test_summary': {
                'total_scenarios': len(test_scenarios),
                'passed_scenarios': 0,
                'failed_scenarios': 0,
                'validation_modes_tested': ['strict'],
                'integration_modes_tested': ['sequential']
            },
            'detailed_results': [],
            'validation_insights': [],
            'recommendations': []
        }
        
        # 测试每个场景
        for i, scenario in enumerate(test_scenarios):
            scenario_name = scenario.get('name', f'scenario_{i+1}')
            parameters = scenario.get('parameters', {})
            parameter_contract = scenario.get('parameter_contract', {})
            memory_weights = scenario.get('memory_weights', {})
            
            scenario_result = {
                'scenario_name': scenario_name,
                'steps': [],
                'overall_success': True
            }
            
            # 步骤1: 验证工具名称（如果提供）
            if 'tool_name' in scenario:
                tool_name = scenario['tool_name']
                try:
                    # 使用 eval to call tool_name_validator
                    name_validation = eval("tool_name_validator(tool_name=tool_name)")
                    scenario_result['steps'].append({
                        'step': 'tool_name_validation',
                        'result': name_validation,
                        'success': name_validation.get('is_valid', False)
                    })
                    if not name_validation.get('is_valid', False):
                        scenario_result['overall_success'] = False
                except Exception as e:
                    scenario_result['steps'].append({
                        'step': 'tool_name_validation',
                        'error': str(e),
                        'success': False
                    })
                    scenario_result['overall_success'] = False
            
            # 步骤2: 验证参数契约
            try:
                # 使用正确的参数格式
                param_validation_input = json.dumps({
                    'parameters': parameters,
                    'parameter_contract': parameter_contract
                })
                # 使用 eval to call unified_api_parameter_validation_layer
                param_validation = eval("unified_api_parameter_validation_layer(input_args=param_validation_input)")
                scenario_result['steps'].append({
                    'step': 'parameter_contract_validation',
                    'result': param_validation,
                    'success': param_validation.get('is_valid', False)
                })
                if not param_validation.get('is_valid', False):
                    scenario_result['overall_success'] = False
            except Exception as e:
                scenario_result['steps'].append({
                    'step': 'parameter_contract_validation',
                    'error': str(e),
                    'success': False
                })
                scenario_result['overall_success'] = False
            
            # 步骤3: 验证记忆系统（如果提供memory_weights）
            if memory_weights:
                try:
                    # 使用正确的参数格式
                    memory_validation_input = json.dumps({
                        'patch_content': 'test',
                        'memory_weights': memory_weights,
                        'repair_data': {'success': True, 'message': 'test'},
                        'validation_mode': 'full'
                    })
                    # 使用 eval to call memory_system_validation_triad_v2
                    memory_validation = eval("memory_system_validation_triad_v2(input_params=memory_validation_input)")
                    scenario_result['steps'].append({
                        'step': 'memory_system_validation',
                        'result': memory_validation,
                        'success': memory_validation.get('overall_validity', 0) > 0.5
                    })
                    if memory_validation.get('overall_validity', 0) <= 0.5:
                        scenario_result['overall_success'] = False
                except Exception as e:
                    scenario_result['steps'].append({
                        'step': 'memory_system_validation',
                        'error': str(e),
                        'success': False
                    })
                    scenario_result['overall_success'] = False
            
            # 更新统计
            if scenario_result['overall_success']:
                results['test_summary']['passed_scenarios'] += 1
            else:
                results['test_summary']['failed_scenarios'] += 1
                
            results['detailed_results'].append(scenario_result)
        
        # 生成洞察和建议
        if results['test_summary']['failed_scenarios'] == 0:
            results['validation_insights'].append('所有测试场景通过，验证框架三元组工作正常')
            results['recommendations'].append('可以安全使用验证框架三元组进行生产环境部署')
        else:
            results['validation_insights'].append(f'发现 {results["test_summary"]["failed_scenarios"]} 个失败场景，需要修复')
            results['recommendations'].append('检查失败场景的具体错误信息，修复相应的验证逻辑')
            
        return results
        
    except Exception as e:
        return {
            'error': str(e),
            'test_summary': {
                'total_scenarios': 0,
                'passed_scenarios': 0,
                'failed_scenarios': 0,
                'validation_modes_tested': [],
                'integration_modes_tested': []
            },
            'detailed_results': [],
            'validation_insights': [f'测试执行失败: {str(e)}'],
            'recommendations': ['检查测试配置格式是否正确']
        }