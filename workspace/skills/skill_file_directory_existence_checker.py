"""
自动生成的技能模块
需求: 检查文件或目录是否存在，并返回详细信息
生成时间: 2026-03-21 14:07:32
"""

# skill_name: file_directory_existence_checker

import os
import stat
from datetime import datetime

def main(args=None):
    """
    检查文件或目录是否存在，并返回详细信息
    参数:
    - path: 要检查的文件或目录路径
    - include_details: 是否包含详细信息（如权限、大小、修改时间等）
    """
    if args is None:
        args = {}
    
    path = args.get('path', '')
    include_details = args.get('include_details', True)
    
    if not path:
        return {
            'result': {'error': '路径参数不能为空'},
            'insights': ['需要提供要检查的路径'],
            'facts': [('file_check', 'requires', 'path')],
            'memories': []
        }
    
    path_exists = os.path.exists(path)
    is_file = os.path.isfile(path)
    is_dir = os.path.isdir(path)
    
    result = {
        'path': path,
        'exists': path_exists,
        'is_file': is_file,
        'is_directory': is_dir
    }
    
    if path_exists and include_details:
        try:
            file_stat = os.stat(path)
            result['size'] = file_stat.st_size
            result['permissions'] = oct(file_stat.st_mode)[-3:]
            result['modified_time'] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            result['created_time'] = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            result['access_time'] = datetime.fromtimestamp(file_stat.st_atime).isoformat()
            
            # 检查权限
            result['readable'] = os.access(path, os.R_OK)
            result['writable'] = os.access(path, os.W_OK)
            result['executable'] = os.access(path, os.X_OK)
            
            # 如果是目录，计算文件数量
            if is_dir:
                try:
                    items = os.listdir(path)
                    result['item_count'] = len(items)
                    result['file_count'] = sum(1 for item in items if os.path.isfile(os.path.join(path, item)))
                    result['directory_count'] = sum(1 for item in items if os.path.isdir(os.path.join(path, item)))
                except PermissionError:
                    result['item_count'] = -1  # 无法访问
                    result['file_count'] = -1
                    result['directory_count'] = -1
        except OSError as e:
            result['error'] = f'无法获取文件详细信息: {str(e)}'
    
    insights = []
    if path_exists:
        if is_file:
            insights.append(f'文件 {path} 存在，大小为 {result.get("size", "未知")} 字节')
        elif is_dir:
            insights.append(f'目录 {path} 存在，包含 {result.get("item_count", "未知")} 个项目')
        else:
            insights.append(f'路径 {path} 存在，但既不是文件也不是目录')
    else:
        insights.append(f'路径 {path} 不存在')
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            ('path', 'exists', str(path_exists)),
            ('path', 'type', 'file' if is_file else 'directory' if is_dir else 'other' if path_exists else 'not_exists')
        ],
        'memories': []
    }