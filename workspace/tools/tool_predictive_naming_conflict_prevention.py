# tool_name: predictive_naming_conflict_prevention
from langchain.tools import tool
import json
import re
from typing import Dict, Any, List, Optional

@tool
def predictive_naming_conflict_prevention(input_args: str = "") -> Dict[str, Any]:
    """
    预测性API命名冲突检测与预防系统
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action: 执行的动作 ('validate_single', 'predict_conflicts', 'generate_safe_name')
            - tool_name: 工具名称（用于validate_single和generate_safe_name）
            - tool_definitions: 工具定义列表（用于predict_conflicts）
            - max_length: 最大长度限制（默认64）
            - context: 上下文信息（可选）
    
    Returns:
        Dict[str, Any]: 包含操作结果的字典
    """
    
    def _generate_safe_tool_name(base_name: str, max_length: int = 64) -> str:
        """生成符合API约束的安全工具名称"""
        # 只保留字母、数字和下划线
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        # 确保不以数字开头
        if safe_name and safe_name[0].isdigit():
            safe_name = 'tool_' + safe_name
        # 截断到最大长度
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length]
        # 移除连续的下划线
        safe_name = re.sub(r'_+', '_', safe_name)
        # 移除开头和结尾的下划线
        safe_name = safe_name.strip('_')
        return safe_name

    def validate_tool_name(tool_name: str, max_length: int = 64) -> Dict[str, Any]:
        """验证工具名称是否符合API约束"""
        result = {
            'valid': True,
            'original_name': tool_name,
            'safe_name': tool_name,
            'issues': [],
            'suggestions': []
        }
        
        # 检查长度
        if len(tool_name) > max_length:
            result['valid'] = False
            result['issues'].append(f"工具名称长度超过{max_length}字符限制")
            result['safe_name'] = _generate_safe_tool_name(tool_name, max_length)
            result['suggestions'].append(f"建议使用截断后的名称: {result['safe_name']}")
        
        # 检查字符合法性
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', tool_name):
            result['valid'] = False
            result['issues'].append("工具名称只能包含字母、数字和下划线，且不能以数字开头")
            safe_candidate = _generate_safe_tool_name(tool_name, max_length)
            if safe_candidate != result['safe_name']:
                result['safe_name'] = safe_candidate
            result['suggestions'].append(f"建议使用安全名称: {result['safe_name']}")
        
        return result

    def predict_naming_conflicts(tool_definitions: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """预测工具定义中的命名冲突"""
        results = {
            'conflicts_detected': False,
            'tool_validations': [],
            'overall_status': 'valid',
            'recommendations': []
        }
        
        for tool_def in tool_definitions:
            tool_name = tool_def.get('name', '')
            validation_result = validate_tool_name(tool_name)
            results['tool_validations'].append({
                'tool_name': tool_name,
                'validation': validation_result
            })
            
            if not validation_result['valid']:
                results['conflicts_detected'] = True
                results['overall_status'] = 'invalid'
                results['recommendations'].extend(validation_result['suggestions'])
        
        return results

    try:
        if input_args:
            params = json.loads(input_args)
        else:
            params = {}
    except json.JSONDecodeError:
        return {
            'error': '缺少有效的JSON参数',
            'result': {'valid': False, 'issues': ['输入参数必须是有效的JSON字符串']}
        }
    
    action = params.get('action', 'validate_single')
    max_length = params.get('max_length', 64)
    context = params.get('context', {})
    
    if action == 'validate_single':
        tool_name = params.get('tool_name', '')
        if not tool_name:
            return {
                'error': '缺少 tool_name 参数',
                'result': {'valid': False, 'issues': ['必须提供tool_name参数']}
            }
        result = validate_tool_name(tool_name, max_length)
        return {'result': result}
    
    elif action == 'predict_conflicts':
        tool_definitions = params.get('tool_definitions', [])
        if not tool_definitions:
            return {
                'error': '缺少 tool_definitions 参数',
                'result': {'conflicts_detected': False, 'tool_validations': [], 'overall_status': 'invalid', 'issues': ['必须提供tool_definitions参数']}
            }
        result = predict_naming_conflicts(tool_definitions, context)
        return {'result': result}
    
    elif action == 'generate_safe_name':
        base_name = params.get('tool_name', '')
        if not base_name:
            return {
                'error': '缺少 tool_name 参数',
                'result': {'safe_name': '', 'issues': ['必须提供tool_name参数']}
            }
        safe_name = _generate_safe_tool_name(base_name, max_length)
        return {'result': {'original_name': base_name, 'safe_name': safe_name}}
    
    else:
        return {
            'error': f'不支持的操作: {action}',
            'result': {'valid': False, 'issues': [f'支持的操作: validate_single, predict_conflicts, generate_safe_name']}
        }