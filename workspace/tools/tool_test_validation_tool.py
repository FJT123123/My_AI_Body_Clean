# tool_name: test_validation_tool
from langchain.tools import tool
import json

@tool
def test_validation_tool(input_data: str = None) -> dict:
    """
    测试工具验证机制，用于验证工具创建和运行机制是否正常工作。
    
    Args:
        input_data (str): 可选的输入数据，用于测试各种参数处理
    
    Returns:
        dict: 包含测试结果的字典
    """
    try:
        result = {
            "status": "success",
            "message": "Test validation tool executed successfully",
            "input_data": input_data,
            "validation_passed": True,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # 如果有输入数据，尝试解析JSON
        if input_data:
            try:
                parsed_input = json.loads(input_data)
                result["parsed_input"] = parsed_input
            except json.JSONDecodeError:
                result["parsed_input"] = input_data
                result["input_format"] = "raw_string"
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Test validation tool failed: {str(e)}",
            "validation_passed": False,
            "error_type": type(e).__name__
        }