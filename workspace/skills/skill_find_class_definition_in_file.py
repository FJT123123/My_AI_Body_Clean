"""
自动生成的技能模块
需求: 在指定文件中查找特定类的定义，返回类的完整代码
生成时间: 2026-03-21 19:39:20
"""

# skill_name: find_class_definition_in_file

def main(args=None):
    """
    在指定文件中查找特定类的定义，返回类的完整代码
    
    参数:
    - file_path: 要搜索的文件路径
    - class_name: 要查找的类名
    """
    import re
    import os
    
    if args is None:
        args = {}
    
    file_path = args.get('file_path')
    class_name = args.get('class_name')
    
    if not file_path or not class_name:
        return {
            'result': {'error': '缺少必要参数: file_path 或 class_name'},
            'insights': ['需要提供文件路径和类名'],
            'next_skills': []
        }
    
    if not os.path.exists(file_path):
        return {
            'result': {'error': f'文件不存在: {file_path}'},
            'insights': [f'指定的文件路径不存在: {file_path}'],
            'next_skills': []
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 构建正则表达式来查找类定义
        # 匹配 class 类名: 或 class 类名(父类):
        pattern = rf'(class\s+{re.escape(class_name)}\s*(?:\(\s*[\w\.\s,]*\s*\))?\s*:)(.*?)(?=\n\s*class\s+|\Z)'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            return {
                'result': {'class_found': False, 'class_code': None},
                'insights': [f'在文件 {file_path} 中未找到类 {class_name} 的定义'],
                'next_skills': []
            }
        
        # 提取第一个匹配的类定义
        class_header, class_body = matches[0]
        
        # 找到类定义的完整代码
        class_code = class_header + class_body.strip()
        
        # 为了更精确地提取类的完整内容，我们需要使用更复杂的解析
        lines = content.split('\n')
        
        class_start_line = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(f'class {class_name}') or line.strip().startswith(f'class {class_name}('):
                class_start_line = i
                break
        
        if class_start_line == -1:
            return {
                'result': {'class_found': False, 'class_code': None},
                'insights': [f'在文件 {file_path} 中未找到类 {class_name} 的定义'],
                'next_skills': []
            }
        
        # 找到类定义的结束位置
        class_indent = len(lines[class_start_line]) - len(lines[class_start_line].lstrip())
        class_end_line = len(lines)
        
        for i in range(class_start_line + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= class_indent and line.strip().startswith("class ") or (current_indent <= class_indent and not line.strip().startswith("#")):
                class_end_line = i
                break
        
        # 提取类的完整定义
        class_lines = lines[class_start_line:class_end_line]
        class_code = '\n'.join(class_lines)
        
        # 清理类代码末尾的空行
        class_code = class_code.rstrip()
        
        return {
            'result': {
                'class_found': True,
                'class_name': class_name,
                'file_path': file_path,
                'class_code': class_code
            },
            'insights': [f'成功在文件 {file_path} 中找到类 {class_name} 的定义'],
            'memories': [f'在 {file_path} 中定位到了 {class_name} 类的定义'],
            'next_skills': []
        }
        
    except Exception as e:
        return {
            'result': {'error': f'读取文件时发生错误: {str(e)}'},
            'insights': [f'读取文件 {file_path} 时发生错误: {str(e)}'],
            'next_skills': []
        }