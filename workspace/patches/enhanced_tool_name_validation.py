# patch_purpose: enhance_tool_name_validation

import re
import os
from typing import Dict, Any, Optional

def _generate_safe_tool_name(original_name: str, max_length: int = 64) -> str:
    """
    生成符合API约束的安全工具名称。
    
    Args:
        original_name: 原始工具名称
        max_length: 最大长度限制，默认64字符
        
    Returns:
        符合长度限制和字符集要求的安全工具名称
    """
    if not original_name:
        return "tool_auto_generated"
    
    # 只保留字母、数字和下划线
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", original_name)
    safe_name = re.sub(r"_+", "_", safe_name).strip("_")
    
    # 截断到最大长度
    if len(safe_name) > max_length:
        # 保留前缀和后缀，中间用...替换
        if max_length <= 10:
            safe_name = safe_name[:max_length]
        else:
            prefix_len = max_length // 2 - 2
            suffix_len = max_length - prefix_len - 3
            safe_name = safe_name[:prefix_len] + "..." + safe_name[-suffix_len:]
    
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = "tool_" + safe_name
    
    # 确保以tool_前缀开头
    if not safe_name.startswith("tool_"):
        safe_name = "tool_" + safe_name
    
    return safe_name[:max_length]

def _validate_and_truncate_tool_name(tool_name: str, max_length: int = 64) -> Dict[str, Any]:
    """
    验证并截断工具名称，返回详细的验证结果。
    
    Args:
        tool_name: 工具名称
        max_length: 最大长度限制
        
    Returns:
        包含验证结果的字典
    """
    original_length = len(tool_name)
    is_valid = original_length <= max_length
    safe_name = _generate_safe_tool_name(tool_name, max_length)
    
    result = {
        "valid": is_valid,
        "original_name": tool_name,
        "original_length": original_length,
        "safe_name": safe_name,
        "safe_length": len(safe_name),
        "truncated": original_length > max_length,
        "max_length": max_length
    }
    
    if not is_valid:
        result["message"] = f"工具名称 '{tool_name}' ({original_length}字符) 超出API上限{max_length}字符，已自动截断为: '{safe_name}'"
    
    return result

# 注入到全局命名空间
globals()["_generate_safe_tool_name"] = _generate_safe_tool_name
globals()["_validate_and_truncate_tool_name"] = _validate_and_truncate_tool_name

print("✅ [Patch] 增强型工具名称验证机制已注入")