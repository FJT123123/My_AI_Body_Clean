"""
自动生成的技能模块
需求: 简单测试：检查给定路径是否存在，使用 os.path.exists()
生成时间: 2026-03-21 11:51:14
"""

# skill_name: path_existence_checker

def main(args=None):
    """
    检查给定路径是否存在
    
    参数:
        args: 包含要检查路径的字典，键为 'path'
    
    返回:
        包含检查结果的字典
    """
    import os
    
    if args is None:
        args = {}
    
    path = args.get('path', '')
    
    if not path:
        return {
            'result': {'error': '未提供路径参数'},
            'insights': ['路径参数缺失'],
            'facts': []
        }
    
    exists = os.path.exists(path)
    
    result = {
        'path': path,
        'exists': exists,
        'is_file': os.path.isfile(path) if exists else False,
        'is_directory': os.path.isdir(path) if exists else False
    }
    
    insights = [f"路径 '{path}' 存在性检查完成"]
    if exists:
        if os.path.isfile(path):
            insights.append(f"路径 '{path}' 是一个文件")
        elif os.path.isdir(path):
            insights.append(f"路径 '{path}' 是一个目录")
    else:
        insights.append(f"路径 '{path}' 不存在")
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            [path, 'exists', str(exists)],
            [path, 'is_file', str(result['is_file'])],
            [path, 'is_directory', str(result['is_directory'])]
        ]
    }