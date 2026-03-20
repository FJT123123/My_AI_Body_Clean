"""
自动生成的技能模块
需求: 列出workspace目录中的所有文件
生成时间: 2026-03-12 16:26:48
"""

# skill_name: workspace_file_lister
import os
from pathlib import Path

def main(args=None):
    """
    列出workspace目录中的所有文件
    
    该技能会扫描workspace目录（通常为当前工作目录或指定路径），
    并返回其中包含的所有文件和子目录列表，包括文件名、路径、大小等信息
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', os.getcwd())
    
    # 如果没有指定workspace路径，则使用当前目录
    if not workspace_path or workspace_path == '':
        workspace_path = os.getcwd()
    
    # 验证路径是否存在
    if not os.path.exists(workspace_path):
        return {
            'result': {'error': f'Workspace路径不存在: {workspace_path}'},
            'insights': [f'尝试访问的workspace路径 {workspace_path} 不存在']
        }
    
    # 验证路径是否为目录
    if not os.path.isdir(workspace_path):
        return {
            'result': {'error': f'Workspace路径不是一个目录: {workspace_path}'},
            'insights': [f'workspace路径 {workspace_path} 不是有效目录']
        }
    
    files_info = []
    try:
        # 遍历workspace目录中的所有文件和子目录
        for item in os.listdir(workspace_path):
            item_path = os.path.join(workspace_path, item)
            
            # 获取文件/目录的基本信息
            stat_info = os.stat(item_path)
            item_info = {
                'name': item,
                'path': item_path,
                'is_file': os.path.isfile(item_path),
                'is_directory': os.path.isdir(item_path),
                'size_bytes': stat_info.st_size,
                'modified_time': stat_info.st_mtime,
                'created_time': stat_info.st_ctime
            }
            files_info.append(item_info)
        
        # 按类型和名称排序：目录优先，然后是文件
        files_info.sort(key=lambda x: (not x['is_directory'], x['name']))
        
        result = {
            'workspace_path': workspace_path,
            'total_items': len(files_info),
            'files': [item for item in files_info if item['is_file']],
            'directories': [item for item in files_info if item['is_directory']],
            'all_items': files_info
        }
        
        insights = [f'在workspace目录 {workspace_path} 中找到 {len(files_info)} 个项目']
        
        return {
            'result': result,
            'insights': insights
        }
        
    except PermissionError:
        return {
            'result': {'error': f'没有权限访问workspace目录: {workspace_path}'},
            'insights': [f'访问workspace目录 {workspace_path} 时遇到权限问题']
        }
    except Exception as e:
        return {
            'result': {'error': f'扫描workspace目录时发生错误: {str(e)}'},
            'insights': [f'扫描workspace目录 {workspace_path} 时发生异常: {str(e)}']
        }