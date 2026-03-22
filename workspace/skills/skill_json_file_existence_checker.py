"""
自动生成的技能模块
需求: 正确解析JSON字符串输入的文件检查技能，验证文件是否存在
生成时间: 2026-03-21 13:32:13
"""

# skill_name: json_file_existence_checker
import json
import os

def main(args=None):
    """
    解析JSON字符串输入的文件检查技能，验证文件是否存在
    输入参数应包含一个JSON字符串，解析后获取文件路径并验证文件是否存在
    """
    if args is None:
        args = {}
    
    result = {}
    insights = []
    facts = []
    
    # 获取输入的JSON字符串
    input_json_str = args.get('input_json', '')
    
    if not input_json_str:
        return {
            'result': {'error': '缺少input_json参数'},
            'insights': ['输入参数错误：未提供JSON字符串'],
            'facts': []
        }
    
    try:
        # 解析JSON字符串
        parsed_json = json.loads(input_json_str)
    except json.JSONDecodeError as e:
        return {
            'result': {'error': f'JSON解析失败: {str(e)}'},
            'insights': [f'JSON格式错误: {str(e)}'],
            'facts': []
        }
    
    # 检查是否包含文件路径
    file_path = parsed_json.get('file_path', '')
    
    if not file_path:
        return {
            'result': {'error': 'JSON中未找到file_path字段'},
            'insights': ['输入的JSON中缺少file_path字段'],
            'facts': []
        }
    
    # 检查文件是否存在
    file_exists = os.path.exists(file_path)
    
    # 检查是否为文件（而不是目录）
    is_file = os.path.isfile(file_path)
    
    result['file_path'] = file_path
    result['exists'] = file_exists
    result['is_file'] = is_file
    
    if file_exists:
        if is_file:
            insights.append(f'文件存在: {file_path}')
            facts.append(('file', 'exists', file_path))
            facts.append((file_path, 'type', 'file'))
        else:
            insights.append(f'路径存在但不是文件(可能是目录): {file_path}')
            facts.append((file_path, 'type', 'directory'))
    else:
        insights.append(f'文件不存在: {file_path}')
        facts.append((file_path, 'exists', 'false'))
    
    # 获取文件大小（如果存在）
    if file_exists and is_file:
        file_size = os.path.getsize(file_path)
        result['file_size'] = file_size
        facts.append((file_path, 'size', str(file_size)))
    
    return {
        'result': result,
        'insights': insights,
        'facts': facts
    }