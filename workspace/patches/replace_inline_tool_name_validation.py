# patch_purpose: replace_inline_tool_name_validation

import re
import os
from typing import Dict, Any, Optional

def _enhanced_tool_name_validation(tool_name: str, max_length: int = 64) -> Dict[str, Any]:
    """
    增强的工具名称验证函数，处理API约束并提供安全的截断。
    
    Args:
        tool_name: 原始工具名称
        max_length: 最大长度限制，默认64字符
        
    Returns:
        包含验证结果和安全名称的字典
    """
    if not tool_name:
        return {
            "valid": False,
            "original_name": tool_name,
            "safe_name": "tool_auto_generated",
            "error": "工具名称为空"
        }
    
    # 只保留字母、数字和下划线
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", tool_name)
    safe_name = re.sub(r"_+", "_", safe_name).strip("_")
    
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = "tool_" + safe_name
    
    # 确保以tool_前缀开头（如果还没有）
    if not safe_name.startswith("tool_"):
        safe_name = "tool_" + safe_name
    
    original_length = len(safe_name)
    is_valid = original_length <= max_length
    
    if not is_valid:
        # 智能截断：保留前缀和有意义的后缀
        if max_length <= 12:
            safe_name = safe_name[:max_length]
        else:
            # 保留前30个字符和后20个字符，中间用_v2连接
            prefix_len = min(30, max_length // 2 - 2)
            suffix_len = max_length - prefix_len - 3  # 为_v2留出空间
            if suffix_len > 0:
                safe_name = safe_name[:prefix_len] + "_v2" + safe_name[-suffix_len:]
            else:
                safe_name = safe_name[:max_length]
    
    return {
        "valid": is_valid,
        "original_name": tool_name,
        "original_length": original_length,
        "safe_name": safe_name,
        "safe_length": len(safe_name),
        "truncated": original_length > max_length,
        "max_length": max_length,
        "message": f"工具名称 '{tool_name}' ({original_length}字符) 超出API上限{max_length}字符，已自动截断为: '{safe_name}'" if not is_valid else "工具名称符合API约束"
    }

# 注入到全局命名空间
globals()["_enhanced_tool_name_validation"] = _enhanced_tool_name_validation

print("✅ [Patch] 增强型工具名称验证函数已注入，准备替换内联验证逻辑")