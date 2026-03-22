"""
自动生成的技能模块
需求: 检查文件或目录是否存在，并返回详细信息包括文件大小、修改时间等元数据。
生成时间: 2026-03-22 01:16:26
"""

# skill_file_directory_metadata_checker

import os
import stat
import time
from datetime import datetime

def main(args=None):
    """
    检查文件或目录是否存在，并返回详细信息包括文件大小、修改时间等元数据。
    输入参数应包含 'path' 字段，指定要检查的文件或目录路径。
    """
    if args is None:
        args = {}
    
    path = args.get('path', '')
    
    if not path:
        return {
            'result': {'error': '未提供路径参数'},
            'insights': ['需要提供路径参数'],
            'facts': []
        }
    
    # 检查路径是否存在
    if not os.path.exists(path):
        return {
            'result': {'exists': False, 'path': path},
            'insights': [f'路径 {path} 不存在'],
            'facts': [['path', 'exists', 'false']]
        }
    
    # 获取文件/目录状态
    try:
        file_stat = os.stat(path)
        
        # 判断是文件还是目录
        is_file = os.path.isfile(path)
        is_dir = os.path.isdir(path)
        is_link = os.path.islink(path)
        
        # 格式化时间
        mod_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        create_time = datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        access_time = datetime.fromtimestamp(file_stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取权限信息
        mode = file_stat.st_mode
        permissions = {
            'readable': bool(mode & stat.S_IRUSR),
            'writable': bool(mode & stat.S_IWUSR),
            'executable': bool(mode & stat.S_IXUSR),
        }
        
        # 构造结果
        metadata = {
            'exists': True,
            'path': path,
            'is_file': is_file,
            'is_directory': is_dir,
            'is_symlink': is_link,
            'size_bytes': file_stat.st_size,
            'size_kb': round(file_stat.st_size / 1024, 2) if file_stat.st_size > 0 else 0,
            'size_mb': round(file_stat.st_size / (1024*1024), 2) if file_stat.st_size > 0 else 0,
            'modified_time': mod_time,
            'created_time': create_time,
            'accessed_time': access_time,
            'permissions': permissions,
            'owner_uid': file_stat.st_uid,
            'owner_gid': file_stat.st_gid
        }
        
        # 检查是否为特殊文件类型
        file_type = 'unknown'
        if stat.S_ISREG(mode):
            file_type = 'regular_file'
        elif stat.S_ISDIR(mode):
            file_type = 'directory'
        elif stat.S_ISLNK(mode):
            file_type = 'symlink'
        elif stat.S_ISCHR(mode):
            file_type = 'character_device'
        elif stat.S_ISBLK(mode):
            file_type = 'block_device'
        elif stat.S_ISFIFO(mode):
            file_type = 'fifo'
        elif stat.S_ISSOCK(mode):
            file_type = 'socket'
        
        metadata['file_type'] = file_type
        
        # 生成洞察
        insights = [f'路径 {path} 存在', f'类型: {file_type}']
        if is_file:
            insights.append(f'文件大小: {metadata["size_mb"]} MB')
        elif is_dir:
            insights.append('这是一个目录')
        
        # 生成事实
        facts = [
            ['path', 'exists', 'true'],
            ['path', 'type', file_type],
            ['path', 'size_bytes', str(file_stat.st_size)]
        ]
        
        if is_file:
            facts.append(['path', 'size_mb', str(metadata['size_mb'])])
            facts.append(['file', 'modified_at', mod_time])
        elif is_dir:
            facts.append(['directory', 'contains_files', 'unknown'])
        
        return {
            'result': metadata,
            'insights': insights,
            'facts': facts
        }
        
    except OSError as e:
        return {
            'result': {'error': str(e), 'path': path},
            'insights': [f'无法获取路径 {path} 的元数据: {str(e)}'],
            'facts': [['path', 'metadata_access_error', str(e)]]
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}', 'path': path},
            'insights': [f'检查路径时发生未知错误: {str(e)}'],
            'facts': [['path', 'unknown_error', str(e)]]
        }