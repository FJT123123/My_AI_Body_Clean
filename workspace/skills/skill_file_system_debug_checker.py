"""
自动生成的技能模块
需求: 运行文件系统调试检查，验证test_image.png是否存在
生成时间: 2026-03-12 16:24:55
"""

# skill_name: file_system_debug_checker
import os

def main(args=None):
    """
    运行文件系统调试检查，验证test_image.png是否存在
    返回文件检查结果和路径验证信息
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    
    # 检查当前工作目录
    current_dir = os.getcwd()
    
    # 检查test_image.png文件是否存在
    file_name = "test_image.png"
    file_path = os.path.join(current_dir, file_name)
    file_exists = os.path.exists(file_path)
    
    # 检查当前目录下的所有文件
    all_files = []
    try:
        all_files = os.listdir(current_dir)
    except PermissionError:
        all_files = ["Permission denied to list directory contents"]
    
    result_data = {
        'file_name': file_name,
        'file_path': file_path,
        'file_exists': file_exists,
        'current_directory': current_dir,
        'all_files_in_directory': all_files
    }
    
    insights = []
    if file_exists:
        insights.append(f"文件 {file_name} 在路径 {file_path} 存在")
        file_size = os.path.getsize(file_path)
        insights.append(f"文件大小: {file_size} 字节")
    else:
        insights.append(f"文件 {file_name} 在路径 {file_path} 不存在")
        insights.append(f"当前目录包含 {len(all_files)} 个项目")
    
    return {
        'result': result_data,
        'insights': insights
    }