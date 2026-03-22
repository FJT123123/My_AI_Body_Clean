# tool_name: tool_name_length_validator
from langchain.tools import tool
import re

@tool
def tool_name_length_validator(input_args: str) -> dict:
    """
    验证工具名称长度是否符合API约束
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str, required): 工具名称
            - max_length (int, optional): 最大允许长度，默认64字符
    
    Returns:
        dict: 包含验证结果的字典，包含valid、original_name、truncated_name等字段
    """
    import json
    
    try:
        args = json.loads(input_args)
        tool_name = args.get("tool_name")
        max_length = args.get("max_length", 64)
        
        if not tool_name:
            return {
                'valid': False,
                'error': '缺少必需的tool_name参数'
            }
        
        if not isinstance(tool_name, str):
            return {
                'valid': False,
                'error': 'tool_name必须是字符串类型'
            }
        
        if not isinstance(max_length, int) or max_length <= 0:
            return {
                'valid': False,
                'error': 'max_length必须是正整数'
            }
        
        # 验证工具名称是否符合规范（字母、数字、下划线）
        if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
            return {
                'valid': False,
                'original_name': tool_name,
                'truncated_name': tool_name,
                'error': '工具名称只能包含字母、数字和下划线',
                'recommendation': '请使用符合规范的工具名称'
            }
        
        if len(tool_name) > max_length:
            truncated_name = tool_name[:max_length]
            return {
                'valid': False,
                'original_name': tool_name,
                'truncated_name': truncated_name,
                'error': f'工具名称超过{max_length}字符限制，建议使用截断后的名称',
                'recommendation': f'使用 "{truncated_name}" 作为工具名称'
            }
        else:
            return {
                'valid': True,
                'original_name': tool_name,
                'truncated_name': tool_name,
                'message': f'工具名称 "{tool_name}" 符合长度要求'
            }
    
    except json.JSONDecodeError:
        return {
            'valid': False,
            'error': 'input_args必须是有效的JSON字符串'
        }
    except Exception as e:
        return {
            'valid': False,
            'error': f'验证过程中发生错误: {str(e)}'
        }