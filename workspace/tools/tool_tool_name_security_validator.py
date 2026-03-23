# tool_name: tool_name_security_validator
from langchain.tools import tool
import json
import re

def _generate_safe_tool_name(original_name: str, max_length: int = 64) -> str:
    """
    生成安全的工具名称，确保符合API长度限制和命名规范
    
    Args:
        original_name: 原始工具名称
        max_length: 最大长度限制，默认64字符
        
    Returns:
        str: 安全的工具名称（只包含字母、数字、下划线，且不超过max_length）
    """
    # 移除或替换非法字符，只保留字母、数字、下划线
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', original_name)
    
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = 'tool_' + safe_name
    
    # 截断到最大长度
    if len(safe_name) > max_length:
        # 尝试在有意义的位置截断（如在下划线处）
        if '_' in safe_name[:max_length]:
            # 找到最后一个下划线的位置
            last_underscore = safe_name[:max_length].rfind('_')
            safe_name = safe_name[:last_underscore]
        else:
            safe_name = safe_name[:max_length]
    
    # 确保名称不为空
    if not safe_name:
        safe_name = 'unnamed_tool'
    
    return safe_name

def validate_and_generate_tool_name(original_name: str) -> dict:
    """
    验证并生成安全的工具名称
    
    Args:
        original_name: 原始工具名称
        
    Returns:
        dict: 包含验证结果和建议的字典
    """
    MAX_TOOL_NAME_LENGTH = 64
    
    result = {
        'original_name': original_name,
        'is_valid': True,
        'safe_name': original_name,
        'issues': [],
        'recommendations': []
    }
    
    # 检查长度
    if len(original_name) > MAX_TOOL_NAME_LENGTH:
        result['is_valid'] = False
        result['issues'].append(f"工具名称长度超过限制: {len(original_name)} > {MAX_TOOL_NAME_LENGTH}")
        result['safe_name'] = _generate_safe_tool_name(original_name, MAX_TOOL_NAME_LENGTH)
        result['recommendations'].append(f"建议使用截断后的名称: {result['safe_name']}")
    
    # 检查字符合法性
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', original_name):
        if result['is_valid']:  # 如果之前是有效的，现在标记为无效
            result['is_valid'] = False
        result['issues'].append("工具名称包含非法字符，只能包含字母、数字和下划线，且不能以数字开头")
        new_safe_name = _generate_safe_tool_name(original_name, MAX_TOOL_NAME_LENGTH)
        if new_safe_name != result['safe_name']:
            result['safe_name'] = new_safe_name
        result['recommendations'].append(f"建议使用规范化后的名称: {result['safe_name']}")
    
    # 最佳实践建议
    if len(original_name) > 30:
        result['recommendations'].append("最佳实践：建议工具名称保持在30字符以内，为未来扩展留出空间")
    
    return result

@tool
def tool_name_security_validator(tool_name: str) -> dict:
    """
    验证工具名称的安全性，确保符合API长度限制和命名规范
    
    Args:
        tool_name: 要验证的工具名称
        
    Returns:
        dict: 包含验证结果的字典
            - original_name: 原始名称 (str)
            - is_valid: 是否有效 (bool)
            - safe_name: 安全名称 (str)
            - issues: 发现的问题列表 (list)
            - recommendations: 建议列表 (list)
    """
    try:
        if not tool_name:
            return {
                'error': '缺少 tool_name 参数',
                'result': None
            }
        
        # 执行验证
        result = validate_and_generate_tool_name(tool_name)
        return result
    except Exception as e:
        return {
            'error': str(e),
            'result': None
        }