# tool_name: name_validator

from typing import Dict, Any
from langchain.tools import tool
import re

@tool
def name_validator(tool_name: str) -> Dict[str, Any]:
    """
    验证工具名称是否符合API长度限制和命名规范
    
    Args:
        tool_name: 要验证的工具名称
        
    Returns:
        dict: 包含验证结果的字典
            - is_valid: 是否有效 (bool)
            - original_name: 原始名称 (str)
            - safe_name: 安全名称（截断后）(str)
            - issues: 发现的问题列表 (list)
            - recommendations: 修复建议 (list)
    """
    result = {
        'is_valid': True,
        'original_name': tool_name,
        'safe_name': tool_name,
        'issues': [],
        'recommendations': []
    }
    
    # 检查长度限制（硬性限制64字符，最佳实践30字符）
    if len(tool_name) > 64:
        result['is_valid'] = False
        result['issues'].append(f"工具名称长度 {len(tool_name)} 超过硬性限制64字符")
        # 截断到64字符
        result['safe_name'] = tool_name[:64]
        result['recommendations'].append(f"建议使用截断后的名称: {result['safe_name']}")
    
    if len(tool_name) > 30:
        result['issues'].append(f"工具名称长度 {len(tool_name)} 超过最佳实践建议的30字符")
        result['recommendations'].append("建议保持工具名称在30字符以内，为未来扩展留出空间")
    
    # 检查命名规范（只能包含字母、数字和下划线）
    if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
        result['is_valid'] = False
        result['issues'].append("工具名称包含非法字符，只能包含字母、数字和下划线")
        # 生成安全名称
        safe_chars = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
        if len(safe_chars) > 64:
            safe_chars = safe_chars[:64]
        result['safe_name'] = safe_chars
        result['recommendations'].append(f"建议使用安全名称: {result['safe_name']}")
    
    # 如果名称以数字开头，添加前缀
    if tool_name and tool_name[0].isdigit():
        result['issues'].append("工具名称不应以数字开头")
        result['safe_name'] = f"tool_{tool_name}"[:64]
        result['recommendations'].append(f"建议使用前缀名称: {result['safe_name']}")
        result['is_valid'] = False
    
    return result