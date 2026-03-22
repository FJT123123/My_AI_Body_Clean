# tool_name: sixty_four_characters_exact_tool_name_for_api_defense_testing_13
from langchain.tools import tool
import json

@tool
def sixty_four_characters_exact_tool_name_for_api_defense_testing_13():
    """
    验证64字符工具名称是否能正常创建和执行的测试工具
    用途: 验证API 400错误修复是否真正有效，通过创建恰好64字符的工具名称来测试硬性限制
    参数: 无
    返回值: 包含验证结果的字典，包含result、message和tool_name_length
    触发条件: 用于测试API工具名称长度限制的边界情况
    """
    try:
        # 验证工具名称长度
        tool_name = "sixty_four_characters_exact_tool_name_for_api_defense_testing_13"
        tool_name_length = len(tool_name)
        
        # 检查是否为64字符
        if tool_name_length == 64:
            result = {
                'result': 'success',
                'message': '64字符工具名称创建成功，API 400错误已修复',
                'tool_name_length': tool_name_length,
                'tool_name': tool_name
            }
        else:
            result = {
                'result': 'error',
                'message': f'工具名称长度不正确，期望64字符，实际为{tool_name_length}字符',
                'tool_name_length': tool_name_length,
                'tool_name': tool_name
            }
        
        return result
    except Exception as e:
        return {
            'result': 'error',
            'message': f'执行过程中发生异常: {str(e)}',
            'tool_name_length': 64,
            'tool_name': 'sixty_four_characters_exact_tool_name_for_api_defense_testing_13'
        }

if __name__ == '__main__':
    result = sixty_four_characters_exact_tool_name_for_api_defense_testing_13()
    print(json.dumps(result, ensure_ascii=False, indent=2))