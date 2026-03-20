"""
自动生成的技能模块
需求: 创建一个简单的文件系统检查技能，用于验证当前工作目录和文件存在性
生成时间: 2026-03-12 16:22:24
"""

# skill_name: file_system_integrity_checker
import os
import json
from pathlib import Path

def main(args=None):
    """
    文件系统完整性检查技能
    验证当前工作目录和指定文件的存在性，确保文件系统路径可访问
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    work_dir = os.getcwd()
    
    # 获取要检查的文件路径列表
    files_to_check = args.get('files_to_check', [])
    if isinstance(files_to_check, str):
        files_to_check = [files_to_check]
    
    results = {
        'current_work_dir': work_dir,
        'work_dir_exists': os.path.exists(work_dir),
        'work_dir_readable': os.access(work_dir, os.R_OK),
        'work_dir_writable': os.access(work_dir, os.W_OK),
        'file_checks': []
    }
    
    for file_path in files_to_check:
        file_info = {
            'file_path': file_path,
            'exists': os.path.exists(file_path),
            'is_file': os.path.isfile(file_path),
            'is_dir': os.path.isdir(file_path),
            'readable': os.access(file_path, os.R_OK) if os.path.exists(file_path) else False,
            'writable': os.access(file_path, os.W_OK) if os.path.exists(file_path) else False,
            'size': os.path.getsize(file_path) if os.path.exists(file_path) and os.path.isfile(file_path) else 0
        }
        results['file_checks'].append(file_info)
    
    # 检查最近的文件系统相关记忆
    db_path = context.get('db_path', '')
    recent_memories = context.get('recent_memories', [])
    
    fs_related_memories = []
    for mem in recent_memories:
        if isinstance(mem, dict) and any(keyword in mem.get('content', '').lower() 
                                        for keyword in ['file', 'directory', 'path', 'filesystem', 'folder']):
            fs_related_memories.append(mem)
    
    insights = []
    if results['work_dir_exists'] and results['work_dir_readable']:
        insights.append(f"当前工作目录 {work_dir} 存在且可读")
    else:
        insights.append(f"当前工作目录 {work_dir} 存在问题：存在={results['work_dir_exists']}, 可读={results['work_dir_readable']}")
    
    for file_info in results['file_checks']:
        if file_info['exists']:
            insights.append(f"文件 {file_info['file_path']} 存在，类型={'文件' if file_info['is_file'] else '目录'}")
        else:
            insights.append(f"文件 {file_info['file_path']} 不存在")
    
    return {
        'result': results,
        'insights': insights,
        'memories': [
            {
                'event_type': 'skill_executed',
                'content': f"文件系统检查结果: {json.dumps(results, ensure_ascii=False)}",
                'importance': 0.5
            }
        ]
    }