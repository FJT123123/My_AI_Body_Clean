"""
自动生成的技能模块
需求: 创建记忆系统文件路径安全验证工具，专门用于验证所有记忆系统相关的文件操作路径。该工具应该检查路径是否在允许的目录范围内（workspace目录及其子目录），防止路径穿越攻击，验证文件扩展名的安全性，并确保路径符合操作系统规范。
生成时间: 2026-03-24 12:31:51
"""

# skill_name: memory_path_security_validator

import os
import re
from pathlib import Path

def main(args=None):
    """
    验证记忆系统文件路径安全性，防止路径穿越攻击，检查扩展名安全性，并确保路径符合操作系统规范。
    """
    if args is None:
        args = {}
    
    # 获取 workspace 目录
    context = args.get('__context__', {})
    workspace_dir = context.get('workspace_dir', os.getcwd())
    
    # 获取要验证的路径
    path_to_check = args.get('path', '')
    
    if not path_to_check:
        return {
            'result': {'error': '缺少路径参数'},
            'insights': ['路径验证失败: 缺少验证目标路径'],
            'capabilities': ['path_validation']
        }
    
    # 验证路径安全
    result = validate_memory_path_security(path_to_check, workspace_dir)
    
    if result['is_secure']:
        return {
            'result': {'secure': True, 'path': path_to_check, 'details': result['details']},
            'insights': [f'路径验证成功: {path_to_check} 通过安全检查'],
            'capabilities': ['path_validation']
        }
    else:
        return {
            'result': {'secure': False, 'path': path_to_check, 'details': result['details']},
            'insights': [f'路径验证失败: {path_to_check} 存在安全风险: {result["details"]["issues"]}'],
            'capabilities': ['path_validation']
        }

def validate_memory_path_security(path, workspace_dir):
    """
    验证路径是否安全，包括路径穿越、扩展名、格式等
    """
    result = {
        'is_secure': True,
        'details': {
            'original_path': path,
            'normalized_path': '',
            'issues': [],
            'checks': {}
        }
    }
    
    # 检查路径是否为字符串
    if not isinstance(path, str):
        result['is_secure'] = False
        result['details']['issues'].append('路径必须是字符串')
        return result
    
    # 规范化路径
    try:
        # 使用 Path 处理路径，防止路径穿越
        path_obj = Path(path).resolve()
        normalized_path = str(path_obj)
        result['details']['normalized_path'] = normalized_path
    except Exception as e:
        result['is_secure'] = False
        result['details']['issues'].append(f'路径解析失败: {str(e)}')
        return result
    
    # 检查路径是否在 workspace 目录范围内
    try:
        workspace_path = Path(workspace_dir).resolve()
        path_obj.relative_to(workspace_path)
        result['details']['checks']['path_in_workspace'] = True
    except ValueError:
        result['is_secure'] = False
        result['details']['issues'].append(f'路径不在 workspace 目录范围内: {workspace_dir}')
        result['details']['checks']['path_in_workspace'] = False
    
    # 检查路径是否包含危险模式（如 ../ 或 ..\ 等）
    dangerous_patterns = [r'\.\./', r'\.\.\\', r'\.\.', r'\.\.']
    path_str = path.replace('\\', '/')  # 统一路径分隔符
    for pattern in dangerous_patterns:
        if re.search(pattern, path_str):
            result['is_secure'] = False
            result['details']['issues'].append(f'路径包含危险模式: {pattern}')
            break
    
    # 检查路径是否包含特殊字符（可能用于注入攻击）
    special_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in special_chars:
        if char in path:
            result['is_secure'] = False
            result['details']['issues'].append(f'路径包含特殊字符: {char}')
            break
    
    # 检查文件扩展名安全性
    extension_check = check_file_extension_security(path)
    result['details']['checks']['extension_safe'] = extension_check['is_safe']
    if not extension_check['is_safe']:
        result['is_secure'] = False
        result['details']['issues'].extend(extension_check['issues'])
    
    # 检查路径长度（防止超长路径攻击）
    if len(path) > 1000:  # 路径长度限制
        result['is_secure'] = False
        result['details']['issues'].append('路径长度超过限制')
    
    # 检查路径中是否包含空字符
    if '\0' in path:
        result['is_secure'] = False
        result['details']['issues'].append('路径包含空字符')
    
    return result

def check_file_extension_security(path):
    """
    检查文件扩展名是否安全
    """
    result = {
        'is_safe': True,
        'issues': []
    }
    
    # 获取文件扩展名
    path_obj = Path(path)
    extension = path_obj.suffix.lower()
    
    # 定义不安全的扩展名
    unsafe_extensions = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.wsf', '.msi',
        '.jar', '.sh', '.pl', '.py', '.rb', '.php', '.asp', '.aspx', '.jsp', '.html',
        '.htm', '.svg', '.xml', '.dll', '.sys', '.bin', '.out', '.app', '.jar', '.war'
    ]
    
    # 如果没有扩展名，检查是否为目录
    if not extension:
        if path.endswith('/') or path.endswith('\\'):
            # 是目录，安全
            pass
        else:
            # 无扩展名文件，需要特别注意
            result['is_safe'] = False
            result['issues'].append('文件无扩展名，可能存在安全风险')
            return result
    
    # 检查扩展名
    if extension in unsafe_extensions:
        result['is_safe'] = False
        result['issues'].append(f'文件扩展名不安全: {extension}')
    
    # 检查是否为记忆系统允许的扩展名
    allowed_extensions = ['.db', '.json', '.txt', '.log', '.sqlite', '.sqlite3', '.csv', '.md']
    if extension in allowed_extensions:
        result['is_safe'] = True
        return result
    
    # 检查是否为常见数据文件格式
    data_extensions = ['.db', '.sqlite', '.json', '.csv', '.xml', '.yaml', '.yml', '.txt', '.log']
    if extension in data_extensions:
        result['is_safe'] = True
        return result
    
    # 如果扩展名不在已知安全列表中，需要进一步检查
    if extension and extension not in unsafe_extensions:
        # 对于未知扩展名，暂时标记为安全，但可以记录
        pass
    
    return result