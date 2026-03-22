# tool_name: naming_convention_analyzer

from langchain.tools import tool
import json
import re
from typing import Dict, Any, List, Optional

def load_capability_module(module_name: str):
    """运行时注入API：加载能力模块"""
    import importlib
    return importlib.import_module(module_name)

@tool
def naming_convention_analyzer(input_args: str = "") -> Dict[str, Any]:
    """
    命名约定分析与验证工具
    
    该工具用于分析和验证命名约定，确保工具名称符合API要求，避免命名冲突和格式错误。
    使用semantic_innovation_capability进行命名模式分析和语义验证。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action: 执行的动作 ('validate', 'analyze', 'suggest')
            - name: 待分析的名称
            - domain: 概念领域（可选）
            - context: 上下文信息（可选）
    
    Returns:
        Dict[str, Any]: 包含分析结果的字典
    """
    
    def _validate_naming_convention(name: str) -> Dict[str, Any]:
        """验证命名约定是否符合API要求"""
        result = {
            'valid': True,
            'name': name,
            'issues': [],
            'suggestions': []
        }
        
        # 检查长度（最大64字符）
        if len(name) > 64:
            result['valid'] = False
            result['issues'].append(f"名称长度超过64字符限制（当前长度: {len(name)}）")
            result['suggestions'].append(f"建议截断至64字符以内")
        
        # 检查字符合法性（字母、数字、下划线，不以数字开头）
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            result['valid'] = False
            result['issues'].append("名称只能包含字母、数字和下划线，且不能以数字开头")
            result['suggestions'].append("建议使用字母或下划线开头，仅包含字母、数字和下划线")
        
        # 检查是否为Python关键字
        import keyword
        if keyword.iskeyword(name):
            result['valid'] = False
            result['issues'].append(f"名称 '{name}' 是Python关键字，不能用作工具名称")
            result['suggestions'].append(f"建议在名称前添加前缀，如 'tool_{name}'")
        
        return result

    def _generate_safe_name(name: str) -> str:
        """生成符合命名约定的安全名称"""
        # 只保留字母、数字和下划线
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # 确保不以数字开头
        if safe_name and safe_name[0].isdigit():
            safe_name = 'tool_' + safe_name
        # 确保不为空
        if not safe_name:
            safe_name = 'unnamed_tool'
        # 截断到最大长度
        if len(safe_name) > 64:
            safe_name = safe_name[:64]
        # 移除连续的下划线
        safe_name = re.sub(r'_+', '_', safe_name)
        # 移除开头和结尾的下划线
        safe_name = safe_name.strip('_')
        
        # 确保不为空
        if not safe_name:
            safe_name = 'tool_default'
        
        # 检查是否为Python关键字
        import keyword
        if keyword.iskeyword(safe_name):
            safe_name = 'tool_' + safe_name
            
        return safe_name

    try:
        if input_args:
            params = json.loads(input_args)
        else:
            params = {}
    except json.JSONDecodeError:
        return {
            'error': '输入参数必须是有效的JSON字符串',
            'result': {'valid': False, 'issues': ['输入参数格式错误']}
        }
    
    action = params.get('action', 'validate')
    name = params.get('name', '')
    domain = params.get('domain', '')
    context = params.get('context', '')
    
    if action == 'validate':
        if not name:
            return {
                'error': '缺少name参数',
                'result': {'valid': False, 'issues': ['必须提供name参数']}
            }
        result = _validate_naming_convention(name)
        return {'result': result}
    
    elif action == 'suggest':
        if not name:
            return {
                'error': '缺少name参数',
                'result': {'valid': False, 'issues': ['必须提供name参数']}
            }
        safe_name = _generate_safe_name(name)
        validation_result = _validate_naming_convention(safe_name)
        return {
            'result': {
                'original_name': name,
                'suggested_name': safe_name,
                'validation': validation_result
            }
        }
    
    elif action == 'analyze':
        if not name:
            return {
                'error': '缺少name参数',
                'result': {'valid': False, 'issues': ['必须提供name参数']}
            }
        
        # 使用semantic_innovation_capability进行命名模式分析
        try:
            semantic_capability = load_capability_module('semantic_innovation_capability')
            naming_analysis = semantic_capability.analyze_naming_patterns(domain) if domain else {}
            semantic_validity = semantic_capability.evaluate_semantic_validity([name], context)
            
            validation_result = _validate_naming_convention(name)
            
            return {
                'result': {
                    'name': name,
                    'validation': validation_result,
                    'naming_analysis': naming_analysis,
                    'semantic_validity': semantic_validity
                }
            }
        except Exception as e:
            return {
                'error': f'调用semantic_innovation_capability失败: {str(e)}',
                'result': {
                    'name': name,
                    'validation': _validate_naming_convention(name)
                }
            }
    
    else:
        return {
            'error': f'不支持的操作: {action}',
            'result': {'valid': False, 'issues': ['支持的操作: validate, analyze, suggest']}
        }