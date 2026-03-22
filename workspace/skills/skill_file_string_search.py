"""
自动生成的技能模块
需求: 搜索文件中包含特定字符串的行，并返回行号和内容
生成时间: 2026-03-21 21:49:02
"""

# skill_name: file_string_search
import os

def main(args=None):
    """
    搜索文件中包含特定字符串的行，并返回行号和内容
    
    参数:
    - file_path: 要搜索的文件路径
    - search_string: 要搜索的字符串
    - case_sensitive: 是否区分大小写，默认为True
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path')
    search_string = args.get('search_string')
    case_sensitive = args.get('case_sensitive', True)
    
    if not file_path or not search_string:
        return {
            'result': {'error': '缺少必需参数: file_path 或 search_string'},
            'insights': ['参数验证失败'],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(file_path):
        return {
            'result': {'error': f'文件不存在: {file_path}'},
            'insights': ['指定的文件路径不存在'],
            'facts': [],
            'memories': []
        }
    
    try:
        results = []
        
        # 读取文件并搜索
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                search_line = line if case_sensitive else line.lower()
                search_target = search_string if case_sensitive else search_string.lower()
                
                if search_target in search_line:
                    results.append({
                        'line_number': line_num,
                        'content': line.rstrip('\n\r'),
                        'matched_string': search_string
                    })
        
        # 检查是否找到匹配项
        if not results:
            return {
                'result': {
                    'file_path': file_path,
                    'search_string': search_string,
                    'case_sensitive': case_sensitive,
                    'matches': [],
                    'total_matches': 0
                },
                'insights': [f'在文件 {file_path} 中未找到字符串 "{search_string}"'],
                'facts': [
                    [file_path, 'contains_string', f'"{search_string}":false'],
                    [file_path, 'search_string', search_string]
                ],
                'memories': []
            }
        
        # 返回匹配结果
        return {
            'result': {
                'file_path': file_path,
                'search_string': search_string,
                'case_sensitive': case_sensitive,
                'matches': results,
                'total_matches': len(results)
            },
            'insights': [
                f'在文件 {file_path} 中找到 {len(results)} 处匹配: "{search_string}"'
            ],
            'facts': [
                [file_path, 'contains_string', f'"{search_string}":true'],
                [file_path, 'search_string', search_string],
                [file_path, 'match_count', str(len(results))]
            ],
            'memories': [
                f'在文件 {file_path} 中搜索字符串 "{search_string}"，找到 {len(results)} 个匹配项'
            ]
        }
        
    except UnicodeDecodeError:
        return {
            'result': {'error': f'无法解码文件 {file_path}，可能不是文本文件'},
            'insights': ['文件编码错误，可能不是文本文件'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'搜索文件时发生错误: {str(e)}'},
            'insights': [f'搜索文件 {file_path} 时发生错误: {str(e)}'],
            'facts': [],
            'memories': []
        }