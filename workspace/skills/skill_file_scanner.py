"""
自动生成的技能模块
需求: 扫描 workspace/skills/ 目录，获取每个技能文件的大小（字节）和最后修改时间（ISO格式），返回结构化数据
生成时间: 2026-03-11 12:28:58
"""

# skill_name: skill_file_scanner
import os
import json
from datetime import datetime

def main(args=None):
    """
    扫描 workspace/skills/ 目录，获取每个技能文件的大小（字节）和最后修改时间（ISO格式），返回结构化数据
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    base_path = context.get('workspace_path', './workspace')
    skills_dir = os.path.join(base_path, 'skills')
    
    # 检查目录是否存在
    if not os.path.exists(skills_dir):
        return {
            'result': {'error': f'skills directory does not exist: {skills_dir}'},
            'insights': [f'技能目录 {skills_dir} 不存在']
        }
    
    # 扫描技能目录
    skill_files = []
    for filename in os.listdir(skills_dir):
        if filename.endswith('.py'):
            file_path = os.path.join(skills_dir, filename)
            try:
                stat_info = os.stat(file_path)
                file_size = stat_info.st_size
                mod_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                
                skill_files.append({
                    'filename': filename,
                    'size_bytes': file_size,
                    'last_modified': mod_time
                })
            except OSError as e:
                # 记录无法访问的文件
                skill_files.append({
                    'filename': filename,
                    'size_bytes': None,
                    'last_modified': None,
                    'error': str(e)
                })
    
    result = {
        'skill_directory': skills_dir,
        'total_files': len(skill_files),
        'files': skill_files
    }
    
    insights = [f'扫描到 {len(skill_files)} 个技能文件', f'技能目录位于: {skills_dir}']
    
    return {
        'result': result,
        'insights': insights
    }