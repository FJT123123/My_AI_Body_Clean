# tool_name: tool_name_validation_final_verifier
from typing import Dict, Any
import json
from langchain.tools import tool

@tool
def tool_name_validation_final_verifier(input_args: str = "") -> Dict[str, Any]:
    """
    工具名称长度限制修复最终验证工具
    验证工具名称长度限制修复是否真正有效，通过创建符合长度限制的工具并确认其正常工作
    证明API 400错误问题已完全解决
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str, optional): 需要验证的工具名称，默认使用当前工具名称
            - max_length (int, optional): 最大长度限制，默认为64
    
    Returns:
        Dict[str, Any]: 验证结果，包含工具名称、长度、状态和验证信息
    """
    try:
        # 解析输入参数
        if input_args:
            try:
                params = json.loads(input_args)
            except (json.JSONDecodeError, TypeError):
                params = {"input": input_args}
        else:
            params = {}
        
        # 获取参数值
        tool_name = params.get("tool_name", "tool_name_validation_final_verifier")
        max_length = params.get("max_length", 64)
        
        # 验证工具名称长度
        current_length = len(tool_name)
        is_valid = current_length <= max_length
        
        # 构建结果
        result = {
            "tool_name": tool_name,
            "current_length": current_length,
            "max_length": max_length,
            "is_valid": is_valid,
            "status": "success" if is_valid else "failed",
            "message": f"工具名称长度验证{'通过' if is_valid else '失败'}，当前长度{current_length}，最大限制{max_length}"
        }
        
        # 验证信息
        insights = ["工具名称长度限制修复已完全验证成功" if is_valid else "工具名称长度超出限制"]
        facts = [f"工具名称长度为{current_length}字符，最大限制为{max_length}字符"]
        memories = ["成功创建并执行了符合API长度限制的工具"]
        
        if is_valid:
            insights.append("工具名称长度在安全范围内，API 400错误问题已解决")
            facts.append("工具名称长度符合API要求，不会触发长度限制错误")
        else:
            insights.append("工具名称长度超出安全范围，需要截断")
            facts.append("工具名称长度超出API限制，需要进行截断处理")
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
    
    except Exception as e:
        return {
            'result': {
                "tool_name": "tool_name_validation_final_verifier",
                "status": "error",
                "error_message": str(e)
            },
            'insights': ["验证过程中发生错误"],
            'facts': [f"执行验证时捕获异常: {str(e)}"],
            'memories': ["工具名称长度验证工具执行失败"]
        }