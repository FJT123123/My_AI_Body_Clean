"""
自动生成的技能模块
需求: 在指定文件中搜索特定文本内容，并返回匹配的行号和内容
生成时间: 2026-03-21 19:52:33
"""

# skill_name: file_content_search

def main(args=None):
    """
    在指定文件中搜索特定文本内容，并返回匹配的行号和内容
    
    参数:
    - file_path: 要搜索的文件路径
    - search_text: 要搜索的文本内容
    - case_sensitive: 是否区分大小写，默认为False（不区分）
    - return_line_numbers: 是否返回行号，默认为True
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path', '')
    search_text = args.get('search_text', '')
    case_sensitive = args.get('case_sensitive', False)
    return_line_numbers = args.get('return_line_numbers', True)
    
    if not file_path or not search_text:
        return {
            'result': {'error': 'file_path 和 search_text 参数不能为空'},
            'insights': ['缺少必要的搜索参数'],
            'facts': [],
            'memories': []
        }
    
    if not isinstance(file_path, str) or not isinstance(search_text, str):
        return {
            'result': {'error': 'file_path 和 search_text 必须是字符串类型'},
            'insights': ['参数类型错误'],
            'facts': [],
            'memories': []
        }
    
    if not case_sensitive:
        search_text = search_text.lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return {
            'result': {'error': f'文件 {file_path} 不存在'},
            'insights': [f'搜索文件 {file_path} 不存在'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'无法读取文件 {file_path}: {str(e)}'},
            'insights': [f'读取文件 {file_path} 时出错: {str(e)}'],
            'facts': [],
            'memories': []
        }
    
    matches = []
    for line_num, line in enumerate(lines, 1):
        search_line = line if case_sensitive else line.lower()
        if search_text in search_line:
            if return_line_numbers:
                matches.append({
                    'line_number': line_num,
                    'content': line.rstrip('\n')
                })
            else:
                matches.append(line.rstrip('\n'))
    
    return {
        'result': {
            'file_path': file_path,
            'search_text': args.get('search_text', ''),
            'matches': matches,
            'total_matches': len(matches)
        },
        'insights': [f'在文件 {file_path} 中找到 {len(matches)} 个匹配项'],
        'facts': [
            [file_path, 'contains_matches', f'{len(matches)} occurrences of "{search_text}"']
        ],
        'memories': [
            f'搜索文件 {file_path} 中的文本 "{search_text}"，找到 {len(matches)} 个匹配项'
        ]
    }