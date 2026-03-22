"""
自动生成的技能模块
需求: 将字典参数转换为JSON字符串的工具，用于正确传递参数给其他技能
生成时间: 2026-03-21 13:11:34
"""

# skill_name: dict_to_json_converter

import json
import sys

def main(args=None):
    """
    将字典参数转换为JSON字符串的工具，用于正确传递参数给其他技能
    这个技能接收一个字典格式的参数，将其转换为JSON字符串格式，便于在系统内部传递参数
    """
    if args is None:
        args = {}
    
    # 从参数中获取要转换的字典
    input_dict = args.get('input_dict', {})
    
    # 检查是否为字典类型
    if not isinstance(input_dict, dict):
        return {
            'result': {'error': '输入参数必须是字典类型'},
            'insights': ['输入参数类型错误，需要字典类型'],
            'facts': [('参数类型', '应该是', 'dict')],
            'memories': []
        }
    
    try:
        # 将字典转换为JSON字符串
        json_string = json.dumps(input_dict, ensure_ascii=False, indent=2)
        
        # 返回转换结果
        return {
            'result': {
                'json_string': json_string,
                'input_dict': input_dict,
                'conversion_success': True
            },
            'insights': [f'成功将字典转换为JSON字符串，字符串长度: {len(json_string)}'],
            'facts': [
                ('输入类型', '转换为', 'json_string'),
                ('输入字典键数量', '包含', str(len(input_dict)))
            ],
            'memories': [
                {'event_type': 'skill_executed', 'content': f'字典转JSON成功，输入包含{len(input_dict)}个键值对'}
            ]
        }
    
    except TypeError as e:
        # 处理无法序列化的类型错误
        error_msg = f"无法将字典转换为JSON: {str(e)}"
        return {
            'result': {'error': error_msg, 'conversion_success': False},
            'insights': [error_msg],
            'facts': [('序列化失败', '原因', str(e))],
            'memories': [
                {'event_type': 'skill_executed', 'content': error_msg}
            ]
        }
    except Exception as e:
        # 处理其他异常
        error_msg = f"转换过程中发生错误: {str(e)}"
        return {
            'result': {'error': error_msg, 'conversion_success': False},
            'insights': [error_msg],
            'facts': [('转换失败', '错误类型', type(e).__name__)],
            'memories': [
                {'event_type': 'skill_executed', 'content': error_msg}
            ]
        }