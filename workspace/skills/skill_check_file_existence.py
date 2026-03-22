"""
自动生成的技能模块
需求: 创建一个文件存在性检查技能，从args['input']获取文件路径字符串，检查文件是否存在。
生成时间: 2026-03-21 14:32:41
"""

# skill_name: check_file_existence
import os

def main(args=None):
    """
    检查文件是否存在
    
    参数:
        args: 包含 'input' 键的字典，'input' 对应文件路径字符串
    """
    if args is None:
        args = {}
    
    file_path = args.get('input', '')
    
    if not file_path:
        return {
            'result': {'exists': False, 'error': '未提供文件路径'},
            'insights': ['输入参数中未包含文件路径'],
            'facts': [('file_path', 'is_empty', True)]
        }
    
    exists = os.path.exists(file_path)
    is_file = os.path.isfile(file_path) if exists else False
    
    result = {
        'file_path': file_path,
        'exists': exists,
        'is_file': is_file
    }
    
    if exists and is_file:
        file_size = os.path.getsize(file_path)
        result['file_size'] = file_size
        insights = [f'文件 {file_path} 存在，大小为 {file_size} 字节']
        facts = [('file', 'exists', file_path), ('file', 'size', str(file_size))]
    elif exists and not is_file:
        result['is_directory'] = True
        insights = [f'路径 {file_path} 存在但为目录，不是文件']
        facts = [('path', 'exists', file_path), ('path', 'type', 'directory')]
    else:
        insights = [f'文件 {file_path} 不存在']
        facts = [('file', 'not_exists', file_path)]
    
    return {
        'result': result,
        'insights': insights,
        'facts': facts
    }