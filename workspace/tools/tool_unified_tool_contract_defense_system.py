# tool_name: unified_tool_contract_defense_system
from typing import Dict, Any, List
import json
from langchain.tools import tool

@tool
def unified_tool_contract_defense_system(input_args: str) -> Dict[str, Any]:
    """
    高级工具契约防御系统 - 集成工具名称验证、参数契约验证、自动修复和防御机制
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的操作类型 ('validate_and_repair', 'batch_validate', 'generate_safe_names', 'create_defense_report')
            - tool_definitions (list, optional): 工具定义列表
            - context (dict, optional): 当前执行上下文
            - auto_apply (bool, optional): 是否自动应用修复 (默认False)
    
    Returns:
        Dict[str, Any]: 包含验证结果、修复建议和防御报告的字典
    """
    import json
    import re
    from typing import Dict, Any, List, Optional
    
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        action = params.get('action', 'validate_and_repair')
        tool_definitions = params.get('tool_definitions', [])
        context = params.get('context', {})
        auto_apply = params.get('auto_apply', False)
        
        def _validate_tool_name(tool_name: str, max_length: int = 64) -> Dict[str, Any]:
            """验证工具名称是否符合API约束"""
            result = {
                'valid': True,
                'original_name': tool_name,
                'truncated_name': tool_name,
                'issues': []
            }
            
            # 检查长度
            if len(tool_name) > max_length:
                result['valid'] = False
                result['issues'].append(f'工具名称超过{max_length}字符限制')
                # 安全截断
                safe_name = tool_name[:max_length-4] + '_trc'
                # 确保只包含合法字符
                safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)
                result['truncated_name'] = safe_name
            
            # 检查字符合法性
            if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
                result['valid'] = False
                result['issues'].append('工具名称包含非法字符，只能包含字母、数字和下划线')
                safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
                if len(safe_name) > max_length:
                    safe_name = safe_name[:max_length-4] + '_trc'
                result['truncated_name'] = safe_name
            
            return result
        
        def _validate_parameter_contract(parameters: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
            """验证参数是否符合契约"""
            result = {
                'valid': True,
                'missing_params': [],
                'type_mismatches': [],
                'extra_params': []
            }
            
            if not contract:
                return result
                
            # 检查必需参数
            required_params = contract.get('required', [])
            for param in required_params:
                if param not in parameters:
                    result['valid'] = False
                    result['missing_params'].append(param)
            
            # 检查参数类型
            param_types = contract.get('types', {})
            for param, expected_type in param_types.items():
                if param in parameters:
                    actual_value = parameters[param]
                    if expected_type == 'string' and not isinstance(actual_value, str):
                        result['valid'] = False
                        result['type_mismatches'].append(f'{param}: expected string, got {type(actual_value).__name__}')
                    elif expected_type == 'integer' and not isinstance(actual_value, int):
                        result['valid'] = False
                        result['type_mismatches'].append(f'{param}: expected integer, got {type(actual_value).__name__}')
                    elif expected_type == 'boolean' and not isinstance(actual_value, bool):
                        result['valid'] = False
                        result['type_mismatches'].append(f'{param}: expected boolean, got {type(actual_value).__name__}')
                    elif expected_type == 'object' and not isinstance(actual_value, dict):
                        result['valid'] = False
                        result['type_mismatches'].append(f'{param}: expected object, got {type(actual_value).__name__}')
                    elif expected_type == 'array' and not isinstance(actual_value, list):
                        result['valid'] = False
                        result['type_mismatches'].append(f'{param}: expected array, got {type(actual_value).__name__}')
            
            return result
        
        def _repair_parameter_format(parameters: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
            """自动修复参数格式"""
            repaired = parameters.copy()
            
            if not contract:
                return repaired
                
            # 添加缺失的默认值
            defaults = contract.get('defaults', {})
            for param, default_value in defaults.items():
                if param not in repaired:
                    repaired[param] = default_value
            
            # 修复类型
            param_types = contract.get('types', {})
            for param, expected_type in param_types.items():
                if param in repaired:
                    actual_value = repaired[param]
                    if expected_type == 'string' and not isinstance(actual_value, str):
                        repaired[param] = str(actual_value)
                    elif expected_type == 'integer' and not isinstance(actual_value, int):
                        try:
                            repaired[param] = int(actual_value)
                        except (ValueError, TypeError):
                            repaired[param] = 0
                    elif expected_type == 'boolean' and not isinstance(actual_value, bool):
                        repaired[param] = bool(actual_value)
            
            return repaired
        
        def _generate_safe_tool_name(base_name: str, max_length: int = 64) -> str:
            """生成安全的工具名称"""
            # 移除非法字符
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
            # 截断到最大长度
            if len(safe_name) > max_length:
                safe_name = safe_name[:max_length-4] + '_trc'
            return safe_name
        
        # 根据action执行相应操作
        if action == 'validate_and_repair':
            results = []
            for tool_def in tool_definitions:
                tool_name = tool_def.get('tool_name', '')
                parameters = tool_def.get('parameters', {})
                parameter_contract = tool_def.get('parameter_contract', {})
                
                # 验证工具名称
                name_validation = _validate_tool_name(tool_name)
                
                # 验证参数契约
                param_validation = _validate_parameter_contract(parameters, parameter_contract)
                
                # 修复参数（如果需要）
                repaired_parameters = parameters
                if not param_validation['valid'] and auto_apply:
                    repaired_parameters = _repair_parameter_format(parameters, parameter_contract)
                    # 重新验证修复后的参数
                    param_validation = _validate_parameter_contract(repaired_parameters, parameter_contract)
                
                result = {
                    'tool_name_validation': name_validation,
                    'parameter_validation': param_validation,
                    'repaired_parameters': repaired_parameters if auto_apply else None,
                    'overall_valid': name_validation['valid'] and param_validation['valid']
                }
                results.append(result)
            
            return {
                'success': all(r['overall_valid'] for r in results),
                'results': results,
                'defense_effectiveness': sum(1 for r in results if r['overall_valid']) / len(results) if results else 0.0
            }
        
        elif action == 'batch_validate':
            results = []
            for tool_def in tool_definitions:
                tool_name = tool_def.get('tool_name', '')
                parameters = tool_def.get('parameters', {})
                parameter_contract = tool_def.get('parameter_contract', {})
                
                name_validation = _validate_tool_name(tool_name)
                param_validation = _validate_parameter_contract(parameters, parameter_contract)
                
                result = {
                    'tool_name': tool_name,
                    'name_valid': name_validation['valid'],
                    'param_valid': param_validation['valid'],
                    'issues': name_validation['issues'] + param_validation['missing_params'] + param_validation['type_mismatches']
                }
                results.append(result)
            
            return {
                'validation_results': results,
                'total_valid': sum(1 for r in results if r['name_valid'] and r['param_valid']),
                'total_invalid': len(results) - sum(1 for r in results if r['name_valid'] and r['param_valid'])
            }
        
        elif action == 'generate_safe_names':
            safe_names = []
            for tool_def in tool_definitions:
                original_name = tool_def.get('tool_name', '')
                safe_name = _generate_safe_tool_name(original_name)
                safe_names.append({
                    'original': original_name,
                    'safe': safe_name,
                    'needs_truncation': len(original_name) > 64 or original_name != safe_name
                })
            
            return {'safe_names': safe_names}
        
        elif action == 'create_defense_report':
            # 综合报告
            report = {
                'context': context,
                'timestamp': __import__('datetime').datetime.now().isoformat(),
                'defense_capabilities': [
                    '工具名称长度验证 (64字符限制)',
                    '工具名称字符合法性验证',
                    '参数契约完整性验证',
                    '参数类型验证',
                    '自动参数修复',
                    '安全工具名称生成'
                ],
                'validation_rules': {
                    'tool_name_max_length': 64,
                    'tool_name_allowed_chars': 'a-zA-Z0-9_',
                    'parameter_validation_levels': ['required', 'type', 'format']
                }
            }
            return report
        
        else:
            return {'error': f'未知的操作类型: {action}'}
    
    except Exception as e:
        return {'error': f'工具执行异常: {str(e)}'}