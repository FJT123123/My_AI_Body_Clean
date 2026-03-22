"""
自动生成的技能模块
需求: 使用Python os.path模块检查文件是否存在，并返回文件信息包括大小和修改时间。
生成时间: 2026-03-22 01:16:58
"""

# skill_name: check_file_info
import os
import time
import json

def main(args=None):
    """
    检查文件是否存在，并返回文件信息包括大小和修改时间
    参数:
        args: 包含文件路径的字典，键为 'file_path'
    返回:
        包含文件信息的字典
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path', '')
    
    if not file_path:
        return {
            'result': {'error': '文件路径未提供'},
            'insights': ['缺少必要的文件路径参数'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return {
            'result': {'exists': False, 'file_path': file_path, 'error': '文件不存在'},
            'insights': [f'文件 {file_path} 不存在'],
            'facts': [(file_path, '不存在', '文件')],
            'memories': [f'检查文件 {file_path} 不存在'],
            'capabilities': [],
            'next_skills': []
        }
    
    # 获取文件信息
    file_stat = os.stat(file_path)
    file_size = file_stat.st_size
    modification_time = file_stat.st_mtime
    
    # 转换修改时间格式
    mod_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modification_time))
    
    # 获取文件名和扩展名
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_path)[1]
    
    file_info = {
        'exists': True,
        'file_path': file_path,
        'file_name': file_name,
        'file_size_bytes': file_size,
        'file_size_kb': round(file_size / 1024, 2),
        'file_size_mb': round(file_size / (1024 * 1024), 2),
        'modification_time': mod_time_str,
        'file_extension': file_ext,
        'is_file': os.path.isfile(file_path),
        'is_directory': os.path.isdir(file_path)
    }
    
    insights = [f'文件 {file_path} 存在，大小为 {file_info["file_size_kb"]} KB，修改时间为 {mod_time_str}']
    
    facts = [
        (file_path, '存在', 'True'),
        (file_path, '文件大小(字节)', str(file_size)),
        (file_path, '修改时间', mod_time_str),
        (file_path, '文件扩展名', file_ext)
    ]
    
    memories = [f'文件检查结果: {file_path} 存在，大小 {file_info["file_size_kb"]} KB，修改时间 {mod_time_str}']
    
    return {
        'result': file_info,
        'insights': insights,
        'facts': facts,
        'memories': memories,
        'capabilities': [],
        'next_skills': []
    }