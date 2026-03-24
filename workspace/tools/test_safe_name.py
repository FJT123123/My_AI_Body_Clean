# tool_name: test_safe_name

from langchain.tools import tool
import re

def _generate_safe_tool_name(base_name: str, max_length: int = 64, best_practice_length: int = 30) -> dict:
    """
    生成安全的工具名称，确保符合长度限制
    """
    # 确保只包含合法字符
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
    
    result = {
        'original_name': base_name,
        'safe_name': safe_name,
        'needs_truncation': False,
        'truncated_name': safe_name,
        'recommendation': '',
        'valid': True
    }
    
    if len(safe_name) > max_length:
        result['needs_truncation'] = True
        result['truncated_name'] = safe_name[:max_length]
        result['valid'] = False
        result['recommendation'] = f"工具名称超过{max_length}字符限制，使用截断版本: '{safe_name[:max_length]}'"
    elif len(safe_name) > best_practice_length:
        result['recommendation'] = f"工具名称较长 ({len(safe_name)} 字符)，建议保持在{best_practice_length}字符以内"
    else:
        result['recommendation'] = f"工具名称 '{safe_name}' 符合所有要求"
    
    return result

@tool
def test_safe_name(input_args: str) -> dict:
    """测试安全工具名称生成函数"""
    import json
    args = json.loads(input_args)
    tool_name = args.get("tool_name", "")
    result = _generate_safe_tool_name(tool_name)
    return {"result": result}