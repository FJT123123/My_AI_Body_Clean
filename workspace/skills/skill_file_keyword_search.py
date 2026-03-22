"""
自动生成的技能模块
需求: 在指定文件中搜索包含特定关键词的行，并返回行号和内容
生成时间: 2026-03-21 19:53:11
"""

# skill_name: file_keyword_search

def main(args=None):
    """
    在指定文件中搜索包含特定关键词的行，并返回行号和内容
    
    参数:
    - file_path: 要搜索的文件路径
    - keyword: 要搜索的关键词
    - case_sensitive: 是否区分大小写，默认为False
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path')
    keyword = args.get('keyword')
    case_sensitive = args.get('case_sensitive', False)
    
    if not file_path or not keyword:
        return {
            'result': {'error': 'file_path和keyword参数不能为空'},
            'insights': ['缺少必需参数'],
            'facts': [],
            'memories': []
        }
    
    if not isinstance(file_path, str) or not isinstance(keyword, str):
        return {
            'result': {'error': 'file_path和keyword必须是字符串'},
            'insights': ['参数类型错误'],
            'facts': [],
            'memories': []
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return {
            'result': {'error': f'文件不存在: {file_path}'},
            'insights': [f'文件 {file_path} 不存在'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'读取文件失败: {str(e)}'},
            'insights': [f'读取文件 {file_path} 失败: {str(e)}'],
            'facts': [],
            'memories': []
        }
    
    # 根据是否区分大小写设置搜索
    search_keyword = keyword if case_sensitive else keyword.lower()
    
    results = []
    for line_num, line in enumerate(lines, 1):
        content = line.rstrip('\n\r')
        search_content = content if case_sensitive else content.lower()
        
        if search_keyword in search_content:
            results.append({
                'line_number': line_num,
                'content': content
            })
    
    return {
        'result': {
            'file_path': file_path,
            'keyword': keyword,
            'case_sensitive': case_sensitive,
            'matches': results,
            'total_matches': len(results)
        },
        'insights': [f'在文件 {file_path} 中找到 {len(results)} 个匹配项'],
        'facts': [
            ['file', 'path', file_path],
            ['search', 'keyword', keyword],
            ['search', 'match_count', str(len(results))]
        ],
        'memories': [f'搜索文件 {file_path} 中的关键词 "{keyword}"，找到 {len(results)} 个匹配项']
    }