"""
自动生成的技能模块
需求: 搜索指定文件中包含特定字符串的行号和内容
生成时间: 2026-03-21 19:37:06
"""

# skill_name: search_file_content
import os
import re

def main(args=None):
    """
    搜索指定文件中包含特定字符串的行号和内容
    
    参数:
    - file_path: 要搜索的文件路径
    - search_string: 要搜索的字符串
    - case_sensitive: 是否区分大小写，默认为True
    - use_regex: 是否使用正则表达式，默认为False
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path', '')
    search_string = args.get('search_string', '')
    case_sensitive = args.get('case_sensitive', True)
    use_regex = args.get('use_regex', False)
    
    if not file_path or not search_string:
        return {
            'result': {'error': 'file_path 和 search_string 参数不能为空'},
            'insights': ['缺少必要的搜索参数'],
            'next_skills': []
        }
    
    if not os.path.exists(file_path):
        return {
            'result': {'error': f'文件不存在: {file_path}'},
            'insights': [f'指定的文件路径不存在: {file_path}'],
            'next_skills': []
        }
    
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                content = line.rstrip('\n\r')
                
                if use_regex:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    found = re.search(search_string, content, flags)
                else:
                    if case_sensitive:
                        found = search_string in content
                    else:
                        found = search_string.lower() in content.lower()
                
                if (use_regex and found) or (not use_regex and found):
                    results.append({
                        'line_number': line_num,
                        'content': content,
                        'match_position': found.start() if use_regex and found else content.find(search_string)
                    })
        
        return {
            'result': {
                'file_path': file_path,
                'search_string': search_string,
                'total_matches': len(results),
                'matches': results
            },
            'insights': [f'在文件 {file_path} 中找到 {len(results)} 处匹配'],
            'facts': [
                [file_path, 'contains_matches_for', search_string],
                [file_path, 'has_match_count', str(len(results))]
            ],
            'next_skills': []
        }
    
    except UnicodeDecodeError:
        return {
            'result': {'error': f'无法解码文件 {file_path}，可能是二进制文件或编码问题'},
            'insights': [f'文件 {file_path} 的编码无法识别，可能需要其他工具处理'],
            'next_skills': []
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'搜索文件时发生错误: {str(e)}'],
            'next_skills': []
        }