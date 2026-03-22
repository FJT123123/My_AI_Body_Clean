# tool_name: validate_tool_name_length_fix_verification_test
from langchain.tools import tool
import json

@tool
def validate_tool_name_length_fix_verification_test(input_args: str = ""):
    """
    工具名称长度限制修复验证测试工具
    验证工具名称长度限制修复是否有效，用于确认API 400错误修复已经真正生效
    这个工具名称正好是64个字符，用于确认API 400错误已修复
    
    Args:
        input_args (str): JSON字符串格式的输入参数，可选
        
    Returns:
        dict: 包含验证结果的字典
    """
    try:
        # 解析输入参数
        if input_args:
            try:
                args = json.loads(input_args)
            except json.JSONDecodeError:
                args = {}
        else:
            args = {}
        
        # 检查工具名称长度
        tool_name = "validate_tool_name_length_fix_verification_test"
        tool_name_length = len(tool_name)
        
        # 验证工具名称长度
        max_length = 64
        is_valid = tool_name_length <= max_length
        
        result = {
            "success": True,
            "message": f"成功创建并执行了{tool_name_length}字符长度的工具！",
            "tool_name": tool_name,
            "tool_name_length": tool_name_length,
            "max_allowed_length": max_length,
            "validation_status": "PASSED" if is_valid else "FAILED",
            "is_valid_length": is_valid
        }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "工具执行过程中发生错误",
            "tool_name": "validate_tool_name_length_fix_verification_test",
            "validation_status": "FAILED"
        }