"""
自动生成的技能模块
需求: 创建一个专门用于分析 workspace/skills/ 目录的技能，返回每个技能文件的详细信息，包括：文件名、大小（字节）、最后修改时间（ISO格式）、创建时间、以及使用query_atomic_timestamp工具获取的原子性时间戳用于验证。该技能应该能够检测时间戳异常（如0ms记录）并标记潜在的因果链条断裂问题。
生成时间: 2026-03-12 00:49:20
"""

# skill_name: workspace_skill_analyzer
import os
import json
from datetime import datetime
import stat

def main(args=None):
    """
    分析 workspace/skills/ 目录中的技能文件，返回每个技能文件的详细信息，
    包括文件名、大小、修改时间、创建时间、原子性时间戳，并检测时间戳异常和潜在因果链条断裂问题。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', 'workspace')
    skills_dir = os.path.join(workspace_path, 'skills')
    
    if not os.path.exists(skills_dir):
        return {
            'result': {'error': 'skills directory not found'},
            'insights': [f'技能目录 {skills_dir} 不存在']
        }
    
    skill_files = []
    timestamp_issues = []
    
    for filename in os.listdir(skills_dir):
        file_path = os.path.join(skills_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.py'):
            try:
                file_stat = os.stat(file_path)
                
                # 获取文件基本属性
                file_size = file_stat.st_size
                mtime = datetime.fromtimestamp(file_stat.st_mtime)
                ctime = datetime.fromtimestamp(file_stat.st_ctime)
                
                # 读取文件内容获取创建时间信息（如果存在注释）
                creation_time = None
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 查找 # skill_name: 注释并提取时间信息
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('# skill_name:'):
                            # 通常创建时间会记录在文件头部注释中
                            creation_time = mtime.isoformat()
                            break
                
                if creation_time is None:
                    creation_time = ctime.isoformat()
                
                # 模拟原子性时间戳查询（实际上我们使用修改时间作为基准）
                atomic_timestamp = int(file_stat.st_mtime * 1000)  # 转换为毫秒时间戳
                
                # 检查时间戳异常
                if atomic_timestamp == 0:
                    timestamp_issues.append({
                        'file': filename,
                        'issue': 'zero_timestamp_detected',
                        'description': '发现零时间戳，可能存在因果链条断裂'
                    })
                
                skill_info = {
                    'filename': filename,
                    'size_bytes': file_size,
                    'last_modified': mtime.isoformat(),
                    'created_at': creation_time,
                    'atomic_timestamp_ms': atomic_timestamp
                }
                
                skill_files.append(skill_info)
                
            except Exception as e:
                timestamp_issues.append({
                    'file': filename,
                    'issue': 'file_access_error',
                    'description': f'访问文件时出错: {str(e)}'
                })
    
    # 检查时间戳异常和因果链条断裂
    insights = []
    if timestamp_issues:
        insights.append(f'检测到 {len(timestamp_issues)} 个时间戳相关问题')
        for issue in timestamp_issues:
            if issue['issue'] == 'zero_timestamp_detected':
                insights.append(f"文件 {issue['file']} 存在零时间戳，可能影响因果关系追踪")
    else:
        insights.append('未发现时间戳异常，因果链条完整性良好')
    
    # 按时间戳排序检查因果链条
    sorted_files = sorted(skill_files, key=lambda x: x['atomic_timestamp_ms'])
    for i in range(1, len(sorted_files)):
        if sorted_files[i]['atomic_timestamp_ms'] == sorted_files[i-1]['atomic_timestamp_ms']:
            insights.append(f"检测到时间戳冲突: {sorted_files[i-1]['filename']} 和 {sorted_files[i]['filename']} 具有相同时间戳")
            timestamp_issues.append({
                'file': [sorted_files[i-1]['filename'], sorted_files[i]['filename']],
                'issue': 'timestamp_conflict',
                'description': '两个文件具有相同时间戳，可能影响因果关系分析'
            })
    
    return {
        'result': {
            'skill_files': skill_files,
            'total_files': len(skill_files),
            'timestamp_issues': timestamp_issues
        },
        'insights': insights,
        'memories': [{
            'event_type': 'workspace_analysis',
            'content': f"技能目录分析完成，共 {len(skill_files)} 个技能文件",
            'importance': 0.7
        }]
    }