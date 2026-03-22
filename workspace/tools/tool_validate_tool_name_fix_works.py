# tool_name: validate_tool_name_fix_works
from langchain.tools import tool
import json

@tool
def validate_tool_name_fix_works(input_args: str = ""):
    """
    验证工具名称长度限制修复是否真正有效
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str, optional): 需要验证的工具名称，默认使用当前工具名称
            - max_length (int, optional): 最大允许长度，默认64字符
    
    Returns:
        dict: 包含验证结果、洞察、事实和记忆的完整结构化数据
    """
    try:
        # 解析输入参数
        args = {}
        if input_args:
            try:
                args = json.loads(input_args)
            except json.JSONDecodeError:
                pass
        
        # 获取工具名称和最大长度
        tool_name = args.get("tool_name", "validate_tool_name_fix_works")
        max_length = args.get("max_length", 64)
        
        # 执行验证逻辑
        actual_length = len(tool_name)
        within_limit = actual_length <= max_length
        
        result = {
            "validation_success": within_limit,
            "message": f"工具名称长度验证{'通过' if within_limit else '失败'}！",
            "details": {
                "max_allowed_length": max_length,
                "tool_name_used": tool_name,
                "actual_length": actual_length,
                "within_limit": within_limit
            }
        }
        
        if not within_limit:
            result["message"] = f"工具名称长度超出限制！实际长度{actual_length}，最大允许长度{max_length}"
        
        return {
            'result': result,
            'insights': [f'工具名称长度验证结果：{result["message"]}'],
            'facts': [f'工具名称 "{tool_name}" 长度为 {actual_length}，限制为 {max_length}'],
            'memories': [f'成功验证了工具名称 "{tool_name}" 的长度限制修复机制']
        }
        
    except Exception as e:
        return {
            'result': {
                "validation_success": False,
                "message": f"验证过程中发生错误: {str(e)}",
                "details": {}
            },
            'insights': [f'验证工具名称长度限制时发生异常: {str(e)}'],
            'facts': ['工具名称长度验证失败'],
            'memories': [f'工具名称验证失败，错误信息: {str(e)}']
        }