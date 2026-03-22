"""
自动生成的技能模块
需求: 检查指定路径的文件是否存在，接受JSON字符串参数包含file_path字段
生成时间: 2026-03-21 14:46:25
"""

# skill_name: file_existence_checker
import json
import os

def main(args=None):
    """
    检查指定路径的文件是否存在
    
    参数:
    - args: 包含JSON字符串参数，必须包含file_path字段
    
    返回:
    - dict: 包含检查结果的结构化数据
    """
    if args is None:
        args = {}
    
    # 尝试从参数中获取file_path
    file_path = None
    
    # 首先尝试直接获取file_path
    if 'file_path' in args:
        file_path = args['file_path']
    elif 'json_input' in args:
        # 如果json_input存在，尝试解析
        try:
            json_data = json.loads(args['json_input'])
            if isinstance(json_data, dict) and 'file_path' in json_data:
                file_path = json_data['file_path']
        except (json.JSONDecodeError, TypeError):
            pass
    
    # 如果仍然没有file_path，尝试直接解析args作为JSON
    if file_path is None:
        try:
            args_str = json.dumps(args) if not isinstance(args, str) else args
            json_data = json.loads(args_str)
            if isinstance(json_data, dict) and 'file_path' in json_data:
                file_path = json_data['file_path']
        except (json.JSONDecodeError, TypeError):
            pass
    
    if file_path is None:
        return {
            'result': {
                'error': 'file_path parameter is required',
                'success': False
            },
            'insights': ['缺少必需的file_path参数'],
            'facts': []
        }
    
    # 检查文件是否存在
    exists = os.path.exists(file_path)
    is_file = os.path.isfile(file_path) if exists else False
    
    result = {
        'file_path': file_path,
        'exists': exists,
        'is_file': is_file,
        'success': exists and is_file
    }
    
    if exists:
        if is_file:
            file_size = os.path.getsize(file_path)
            result['file_size'] = file_size
            insights = [f'文件 {file_path} 存在，大小为 {file_size} 字节']
        else:
            insights = [f'路径 {file_path} 存在，但它是一个目录而不是文件']
    else:
        insights = [f'文件 {file_path} 不存在']
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            [file_path, 'exists', str(exists)],
            [file_path, 'is_file', str(is_file)]
        ]
    }