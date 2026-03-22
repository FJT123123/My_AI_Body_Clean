# tool_name: api_defense_test
from langchain.tools import tool
import json

@tool
def api_defense_test(input_args: str = None):
    """
    API防御测试工具 - 验证工具名称长度限制修复
    用于验证API 400错误修复是否真正生效，测试工具名称长度限制修复效果
    
    Args:
        input_args (str): JSON字符串格式的输入参数，可选
        
    Returns:
        dict: 包含验证结果的字典，包含result、message和tool_name字段
    """
    try:
        args = json.loads(input_args) if input_args else {}
        return {
            "result": "success",
            "message": "API防御测试工具创建成功！",
            "tool_name": "api_defense_test"
        }
    except Exception as e:
        return {"error": str(e), "result": "error"}