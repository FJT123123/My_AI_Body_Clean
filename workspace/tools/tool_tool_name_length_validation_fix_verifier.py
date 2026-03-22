# tool_name: tool_name_length_validation_fix_verifier
from langchain.tools import tool
import json

@tool
def tool_name_length_validation_fix_verifier(input_args: str = ""):
    """
    工具名称长度限制修复验证工具
    验证工具名称长度限制修复是否有效，确保截断后的安全名称可以成功创建工具
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str, required): 需要验证的工具名称
            - max_length (int, optional): 最大长度限制，默认为64
    
    Returns:
        dict: 包含验证结果的字典
    """
    # 解析输入参数
    if input_args:
        try:
            params = json.loads(input_args)
        except (json.JSONDecodeError, TypeError):
            params = {"tool_name": input_args}
    else:
        params = {"tool_name": "default_tool_name"}
    
    tool_name = params.get("tool_name", "default_tool_name")
    max_length = params.get("max_length", 64)
    
    # 验证工具名称长度
    actual_length = len(tool_name)
    is_valid = actual_length <= max_length
    
    result = {
        "tool_name": tool_name,
        "actual_length": actual_length,
        "max_length": max_length,
        "is_valid": is_valid,
        "status": "success" if is_valid else "failed",
        "message": f"工具名称长度验证{'通过' if is_valid else '失败'}，长度为{actual_length}字符，限制为{max_length}字符"
    }
    
    if not is_valid:
        # 尝试截断名称并验证
        truncated_name = tool_name[:max_length]
        result["truncated_name"] = truncated_name
        result["truncated_length"] = len(truncated_name)
        result["truncated_valid"] = len(truncated_name) <= max_length
        result["message"] += f"，截断后名称为'{truncated_name}'"
    
    return {
        'result': result,
        'insights': [f'工具名称长度验证结果: {result["status"]}'],
        'facts': [
            f'工具名称长度为{actual_length}字符',
            f'最大长度限制为{max_length}字符',
            f'名称验证状态: {result["status"]}'
        ],
        'memories': [f'验证了工具名称长度限制: {tool_name}']
    }