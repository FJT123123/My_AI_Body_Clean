"""
自动生成的技能模块
需求: 获取当前工作目录路径并列出指定目录的内容
生成时间: 2026-03-21 11:48:25
"""

# skill_name: get_current_directory_and_list_contents

import os
import subprocess

def main(args=None):
    """
    获取当前工作目录路径，并列出指定目录的内容
    
    参数:
    - target_dir: 要列出内容的目录路径，默认为当前工作目录
    """
    if args is None:
        args = {}
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 获取目标目录，默认为当前工作目录
    target_dir = args.get('target_dir', current_dir)
    
    # 验证目录是否存在
    if not os.path.exists(target_dir):
        return {
            'result': {
                'error': f'目录不存在: {target_dir}',
                'current_dir': current_dir
            },
            'insights': [f'尝试访问的目录 {target_dir} 不存在']
        }
    
    if not os.path.isdir(target_dir):
        return {
            'result': {
                'error': f'路径不是目录: {target_dir}',
                'current_dir': current_dir
            },
            'insights': [f'路径 {target_dir} 不是有效的目录']
        }
    
    # 列出目录内容
    try:
        dir_contents = os.listdir(target_dir)
        # 区分文件和文件夹
        files = []
        directories = []
        for item in dir_contents:
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                directories.append(item)
        
        result = {
            'current_dir': current_dir,
            'target_dir': target_dir,
            'contents': dir_contents,
            'files': files,
            'directories': directories,
            'total_count': len(dir_contents),
            'files_count': len(files),
            'directories_count': len(directories)
        }
        
        insights = [
            f'当前工作目录: {current_dir}',
            f'目标目录: {target_dir}',
            f'目录内容总数: {len(dir_contents)} (文件: {len(files)}, 目录: {len(directories)})'
        ]
        
        return {
            'result': result,
            'insights': insights
        }
    except PermissionError:
        return {
            'result': {
                'error': f'权限不足，无法访问目录: {target_dir}',
                'current_dir': current_dir
            },
            'insights': [f'没有权限访问目录 {target_dir}']
        }