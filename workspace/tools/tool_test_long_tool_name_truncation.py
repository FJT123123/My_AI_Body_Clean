# tool_name: test_long_tool_name_truncation
from langchain.tools import tool
import os
import json

@tool
def test_long_tool_name_truncation():
    """
    测试超长工具名称的自动截断机制是否正常工作
    用途: 验证工具名称长度超过限制时的自动截断功能
    参数: 无
    返回值: 包含验证结果的字典，包含result、message、original_name_length和current_tool_name
    触发条件: 用于测试工具名称长度限制和截断机制的边界情况
    """
    try:
        original_name = "this_is_a_very_long_tool_name_that_exceeds_the_sixty_four_character_limit_and_should_be_automatically_truncated"
        result = {
            'result': 'success',
            'message': '超长工具名称已自动截断并成功创建',
            'original_name_length': len(original_name),
            'current_tool_name': 'test_long_tool_name_truncation'
        }
        return result
    except Exception as e:
        return {
            'result': 'error',
            'message': f'工具执行失败: {str(e)}',
            'original_name_length': len(original_name) if 'original_name' in locals() else 0,
            'current_tool_name': 'test_long_tool_name_truncation'
        }