"""
自动生成的技能模块
需求: 检查指定文件路径是否存在，并返回详细信息
生成时间: 2026-03-21 11:48:54
"""

# skill_file_path_checker
import os
import stat
import time
from pathlib import Path

def main(args=None):
    """
    检查指定文件路径是否存在，并返回详细信息
    参数 args: 包含 'file_path' 键的字典，值为要检查的文件路径
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path', '')
    
    if not file_path:
        return {
            'result': {'exists': False, 'error': '未提供文件路径'},
            'insights': ['文件路径参数为空，无法进行检查'],
            'memories': ['尝试检查空文件路径的存在性']
        }
    
    # 转换为 Path 对象以进行更准确的路径处理
    path_obj = Path(file_path)
    
    # 检查文件是否存在
    exists = path_obj.exists()
    
    result = {
        'file_path': str(path_obj),
        'exists': exists,
        'is_file': False,
        'is_directory': False,
        'size': 0,
        'created_time': None,
        'modified_time': None,
        'permissions': None,
        'absolute_path': str(path_obj.absolute())
    }
    
    if exists:
        # 获取文件详细信息
        stat_info = path_obj.stat()
        
        # 判断是文件还是目录
        result['is_file'] = path_obj.is_file()
        result['is_directory'] = path_obj.is_dir()
        
        # 获取文件大小（字节）
        result['size'] = stat_info.st_size
        
        # 获取时间信息（转换为可读格式）
        result['created_time'] = time.ctime(stat_info.st_ctime)
        result['modified_time'] = time.ctime(stat_info.st_mtime)
        
        # 获取权限信息
        mode = stat_info.st_mode
        result['permissions'] = {
            'owner': {
                'read': bool(mode & stat.S_IRUSR),
                'write': bool(mode & stat.S_IWUSR),
                'execute': bool(mode & stat.S_IXUSR)
            },
            'group': {
                'read': bool(mode & stat.S_IRGRP),
                'write': bool(mode & stat.S_IWGRP),
                'execute': bool(mode & stat.S_IXGRP)
            },
            'others': {
                'read': bool(mode & stat.S_IROTH),
                'write': bool(mode & stat.S_IWOTH),
                'execute': bool(mode & stat.S_IXOTH)
            }
        }
    
    # 生成洞察信息
    insights = []
    if exists:
        if result['is_file']:
            insights.append(f"文件 {file_path} 存在，大小为 {result['size']} 字节")
        elif result['is_directory']:
            insights.append(f"目录 {file_path} 存在")
    else:
        insights.append(f"路径 {file_path} 不存在")
    
    return {
        'result': result,
        'insights': insights,
        'memories': [f"检查了文件路径 {file_path} 的存在性，结果: {'存在' if exists else '不存在'}"]
    }