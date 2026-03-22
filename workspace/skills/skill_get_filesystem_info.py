"""
自动生成的技能模块
需求: 获取当前工作目录和文件系统信息
生成时间: 2026-03-22 04:31:03
"""

# skill_name: get_filesystem_info

import os
import subprocess
import platform
from pathlib import Path

def main(args=None):
    """
    获取当前工作目录和文件系统信息，包括当前路径、磁盘使用情况、文件系统类型等
    """
    args = args or {}
    context = args.get('__context__', {})
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    
    # 获取当前用户主目录
    home_dir = os.path.expanduser("~")
    
    # 获取当前目录内容
    try:
        dir_contents = os.listdir(current_dir)
        files = []
        directories = []
        for item in dir_contents:
            item_path = os.path.join(current_dir, item)
            if os.path.isfile(item_path):
                files.append(item)
            elif os.path.isdir(item_path):
                directories.append(item)
    except PermissionError:
        dir_contents = []
        files = []
        directories = []
    
    # 获取系统信息
    system_info = {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'hostname': platform.node(),
    }
    
    # 获取磁盘使用情况
    try:
        disk_usage = shutil.disk_usage(current_dir)
        disk_info = {
            'total': disk_usage.total,
            'used': disk_usage.used,
            'free': disk_usage.free,
            'total_gb': round(disk_usage.total / (1024**3), 2),
            'used_gb': round(disk_usage.used / (1024**3), 2),
            'free_gb': round(disk_usage.free / (1024**3), 2),
        }
    except:
        disk_info = {}
    
    # 获取文件系统类型 (Linux/MacOS)
    fs_type = "Unknown"
    if platform.system() in ['Linux', 'Darwin']:
        try:
            result = subprocess.run(['df', '-T', current_dir], capture_output=True, text=True, check=True)
            lines = result.stdout.split('\n')
            if len(lines) > 1:
                # Second line contains the filesystem info
                fs_info = lines[1].split()
                if len(fs_info) >= 2:
                    fs_type = fs_info[1]
        except:
            pass
    elif platform.system() == 'Windows':
        fs_type = "NTFS"  # Default assumption for Windows
    
    # 统计信息
    stats = {
        'total_files': len(files),
        'total_directories': len(directories),
        'total_items': len(dir_contents),
    }
    
    result = {
        'current_directory': current_dir,
        'home_directory': home_dir,
        'directory_contents': dir_contents,
        'files': files,
        'directories': directories,
        'system_info': system_info,
        'disk_info': disk_info,
        'filesystem_type': fs_type,
        'stats': stats
    }
    
    insights = [
        f"当前工作目录: {current_dir}",
        f"系统平台: {system_info['platform']}",
        f"文件系统类型: {fs_type}",
        f"目录中有 {stats['total_files']} 个文件和 {stats['total_directories']} 个子目录"
    ]
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            ['current_directory', 'is_path', current_dir],
            ['current_directory', 'has_file_count', str(stats['total_files'])],
            ['current_directory', 'has_directory_count', str(stats['total_directories'])],
            ['current_directory', 'has_filesystem_type', fs_type],
            ['system', 'platform', system_info['platform']]
        ]
    }

# For compatibility in case shutil is not available
try:
    import shutil
except ImportError:
    import os
    def disk_usage(path):
        """Fallback implementation of disk_usage if shutil is not available"""
        statvfs = os.statvfs(path)
        total = statvfs.f_frsize * statvfs.f_blocks
        free = statvfs.f_frsize * statvfs.f_bavail
        used = total - free
        return type('DiskUsage', (), {'total': total, 'used': used, 'free': free})()
    import os
    os.disk_usage = disk_usage