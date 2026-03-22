# tool_name: test_truncated_tool_name_validation
from langchain.tools import tool
import json

@tool
def test_truncated_tool_name_validation():
    """
    测试截断后的工具名称是否有效
    
    该工具验证截断后的工具名称是否能成功创建，从而确认修复已生效。
    使用增强型工具名称长度验证器来测试名称截断功能。
    
    Args:
        无参数
        
    Returns:
        dict: 包含测试结果和验证信息的字典
    """
    try:
        # 需要测试的超长工具名称
        long_tool_name = "this_is_an_extremely_long_tool_name_that_exceeds_the_sixty_four_character_limit_for_api_validation"
        
        # 准备输入参数
        input_args = {
            "tool_name": long_tool_name,
            "max_length": 64
        }
        
        # 调用增强型工具名称长度验证器
        validation_result = invoke_tool(
            "enhanced_tool_name_length_validator",
            json.dumps(input_args)
        )
        
        # 检查验证结果
        if isinstance(validation_result, dict):
            if validation_result.get("validation_passed", False):
                return {
                    "status": "success",
                    "message": "截断后的工具名称创建成功",
                    "original_name": long_tool_name,
                    "truncated_name": validation_result.get("safe_name", ""),
                    "validation_details": validation_result
                }
            else:
                return {
                    "status": "failed",
                    "message": "截断后的工具名称验证失败",
                    "original_name": long_tool_name,
                    "validation_details": validation_result
                }
        else:
            return {
                "status": "error",
                "message": "验证工具调用失败或返回格式不正确",
                "original_name": long_tool_name,
                "validation_result": validation_result
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"测试过程中发生异常: {str(e)}",
            "original_name": long_tool_name if 'long_tool_name' in locals() else "unknown"
        }