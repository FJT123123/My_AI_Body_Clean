"""
自动生成的技能模块
需求: 调试技能输入解析器：接收原始 input_args 字符串，输出其类型、内容和 JSON 解析结果（如果可能），用于诊断 run_skill 的参数传递问题。
生成时间: 2026-03-11 13:02:55
"""

# skill_name: debug_input_args_parser
import json
import re
from typing import Dict, Any, Optional

def main(args=None):
    """
    调试技能输入解析器：接收原始 input_args 字符串，输出其类型、内容和 JSON 解析结果（如果可能），用于诊断 run_skill 的参数传递问题。
    """
    if args is None:
        args = {}
    
    # 从参数中获取 input_args
    input_args = args.get('input_args', '')
    
    result = {
        'input_type': type(input_args).__name__,
        'input_content': str(input_args),
        'input_length': len(str(input_args)),
        'is_json_parsable': False,
        'parsed_json': None,
        'parsing_error': None,
        'analysis': []
    }
    
    # 分析输入内容
    if isinstance(input_args, str):
        result['analysis'].append('输入为字符串类型')
        
        # 检查是否为有效的JSON格式
        if input_args.strip():
            try:
                parsed_data = json.loads(input_args)
                result['is_json_parsable'] = True
                result['parsed_json'] = parsed_data
                result['analysis'].append('输入可解析为JSON')
            except json.JSONDecodeError as e:
                result['parsing_error'] = str(e)
                result['analysis'].append(f'JSON解析失败: {str(e)}')
        else:
            result['analysis'].append('输入为空字符串')
    elif isinstance(input_args, (dict, list)):
        result['is_json_parsable'] = True
        result['parsed_json'] = input_args
        result['analysis'].append('输入为已解析的Python对象')
    else:
        result['analysis'].append(f'输入类型为: {type(input_args).__name__}')
    
    # 检查是否包含特殊字符或潜在问题
    input_str = str(input_args)
    if '\n' in input_str:
        result['analysis'].append('输入包含换行符')
    if '\t' in input_str:
        result['analysis'].append('输入包含制表符')
    if input_str.startswith('{') and input_str.endswith('}'):
        result['analysis'].append('输入看起来像JSON对象')
    elif input_str.startswith('[') and input_str.endswith(']'):
        result['analysis'].append('输入看起来像JSON数组')
    
    # 提取可能的变量替换标记
    var_pattern = r'\{[^}]+\}'
    variables = re.findall(var_pattern, input_str)
    if variables:
        result['variables_found'] = variables
        result['analysis'].append(f'发现变量替换标记: {variables}')
    
    return {
        'result': result,
        'insights': [f"输入参数类型: {result['input_type']}", f"解析状态: {'成功' if result['is_json_parsable'] else '失败'}"],
        'facts': [
            {'subject': 'input_args', 'relation': 'has_type', 'object': result['input_type']},
            {'subject': 'input_args', 'relation': 'is_parsable', 'object': str(result['is_json_parsable'])}
        ]
    }