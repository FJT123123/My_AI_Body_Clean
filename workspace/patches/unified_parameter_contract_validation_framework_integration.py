import re

def validate_tool_name_length(tool_name: str, max_length: int = 64) -> dict:
    """
    验证工具名称长度并确保符合命名规范
    """
    result = {
        "valid": True,
        "original_name": tool_name,
        "safe_name": tool_name,
        "errors": []
    }
    
    # 检查长度
    if len(tool_name) > max_length:
        result["valid"] = False
        result["errors"].append(f"Tool name exceeds maximum length of {max_length} characters")
        # 截断并确保不以数字或特殊字符结尾
        truncated = tool_name[:max_length].rstrip('_-0123456789')
        if not truncated or not truncated[0].isalpha():
            truncated = f"default_tool_{tool_name[:max_length-13]}"
        result["safe_name"] = truncated
    
    # 检查字符合法性
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', result["safe_name"]):
        result["valid"] = False
        result["errors"].append("Tool name must start with letter and only contain alphanumeric, underscore, and hyphen")
        result["safe_name"] = f"default_tool_{tool_name[:50]}"
    
    return result

def integrate_tool_name_with_parameter_contract(tool_name: str, parameters: dict, parameter_contract: dict) -> dict:
    """
    将工具名称验证与参数契约验证集成
    """
    # 验证工具名称
    name_validation = validate_tool_name_length(tool_name)
    
    # 验证参数契约
    param_validation = {
        "valid": True,
        "missing_required": [],
        "errors": []
    }
    
    required_params = parameter_contract.get("required_params", [])
    for param in required_params:
        if param not in parameters:
            param_validation["valid"] = False
            param_validation["missing_required"].append(param)
            param_validation["errors"].append(f"Missing required parameter: {param}")
    
    # 合并结果
    overall_result = {
        "tool_name_validation": name_validation,
        "parameter_validation": param_validation,
        "overall_valid": name_validation["valid"] and param_validation["valid"],
        "safe_tool_name": name_validation["safe_name"]
    }
    
    return overall_result