"""
自动生成的技能模块
需求: 扫描 workspace/skills/ 目录，获取每个技能文件的大小（字节）和最后修改时间（ISO格式），返回结构化列表
生成时间: 2026-03-11 13:25:44
"""

# skill_name: skill_workspace_scanner
import os
from datetime import datetime

def main(args=None):
    """
    扫描 workspace/skills/ 目录，获取每个技能文件的大小（字节）和最后修改时间（ISO格式），返回结构化列表
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', 'workspace')
    
    skills_dir = os.path.join(workspace_path, 'skills')
    
    if not os.path.exists(skills_dir):
        return {
            'result': {'error': 'skills directory does not exist'},
            'insights': [f'Skills directory not found at {skills_dir}']
        }
    
    skill_files_info = []
    
    for filename in os.listdir(skills_dir):
        file_path = os.path.join(skills_dir, filename)
        
        # 跳过子目录，只处理文件
        if os.path.isfile(file_path):
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            mod_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            
            skill_files_info.append({
                'filename': filename,
                'size_bytes': file_size,
                'last_modified': mod_time
            })
    
    # 按文件名排序
    skill_files_info.sort(key=lambda x: x['filename'])
    
    insights = [f'Found {len(skill_files_info)} skill files in workspace/skills/']
    
    return {
        'result': skill_files_info,
        'insights': insights
    }