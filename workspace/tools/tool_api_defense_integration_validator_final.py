# tool_name: api_defense_integration_validator_final

from typing import Dict, Any, List, Optional
import json
from langchain.tools import tool

@tool
def api_defense_integration_validator_final(input_args: str) -> dict:
    """
    最终版API防御集成验证工具
    
    使用直接的函数调用方式，避免复杂的导入问题。
    """
    
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args)
        except json.JSONDecodeError:
            params = {}
    else:
        params = input_args if isinstance(input_args, dict) else {}
    
    test_scenarios = params.get('test_scenarios', ['tool_name_length', 'unified_contract'])
    context = params.get('context', 'api_defense_final_validation')
    
    results = {
        'success': True,
        'test_results': {},
        'insights': [],
        'facts': [],
        'memories': []
    }
    
    # 测试工具名称长度验证
    if 'tool_name_length' in test_scenarios:
        try:
            # 测试有效名称
            from workspace.tools.tool_tool_name_length_validator import tool_name_length_validator
            valid_input = json.dumps({'tool_name': 'valid_test_tool'})
            valid_result = tool_name_length_validator(valid_input)
            if isinstance(valid_result, str):
                valid_result = json.loads(valid_result)
            
            if not valid_result.get('valid', False):
                results['test_results']['tool_name_length'] = {'success': False, 'error': '有效工具名称验证失败'}
                results['success'] = False
                return results
            
            # 测试超长名称
            invalid_input = json.dumps({'tool_name': 'a' * 65})
            invalid_result = tool_name_length_validator(invalid_input)
            if isinstance(invalid_result, str):
                invalid_result = json.loads(invalid_result)
            
            if invalid_result.get('valid', True):
                results['test_results']['tool_name_length'] = {'success': False, 'error': '超长工具名称未被正确拒绝'}
                results['success'] = False
                return results
            
            results['test_results']['tool_name_length'] = {'success': True, 'message': '工具名称长度验证正常工作'}
            
        except Exception as e:
            results['test_results']['tool_name_length'] = {'success': False, 'error': f'工具名称长度验证异常: {str(e)}'}
            results['success'] = False
    
    # 测试统一工具契约防御系统
    if 'unified_contract' in test_scenarios:
        try:
            from workspace.tools.tool_unified_tool_contract_defense_system import unified_tool_contract_defense_system
            test_input = json.dumps({
                'action': 'validate_and_repair',
                'tool_definitions': [{
                    'tool_name': 'test_valid_tool',
                    'parameters': {'param1': 'value1'},
                    'parameter_contract': {'param1': {'type': 'string', 'required': True}}
                }],
                'auto_apply': True
            })
            result = unified_tool_contract_defense_system(test_input)
            if isinstance(result, str):
                result = json.loads(result)
            
            if result.get('success', False) and result.get('defense_effectiveness', 0) >= 0.9:
                results['test_results']['unified_contract'] = {'success': True, 'message': '统一工具契约防御系统正常工作'}
            else:
                results['test_results']['unified_contract'] = {'success': False, 'error': '统一工具契约防御系统验证失败'}
                results['success'] = False
                
        except Exception as e:
            results['test_results']['unified_contract'] = {'success': False, 'error': f'统一工具契约防御系统异常: {str(e)}'}
            results['success'] = False
    
    # 添加见解和事实
    if results['success']:
        results['insights'].append("API防御工具链核心功能验证通过")
        results['facts'].append("工具名称长度验证和统一契约防御系统均正常工作")
    else:
        results['insights'].append("API防御工具链存在功能问题")
        results['facts'].append("需要进一步调试和修复相关组件")
    
    results['memories'].append(f"在 {context} 上下文中完成了API防御工具链最终验证")
    
    return results