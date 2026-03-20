"""
Tavily 网络搜索技能
使用 Tavily Search API——专为 AI Agent 设计的实时网络搜索，
覆盖新闻、学术、技术文档，返回可直接阅读的摘要片段。

skill_name: tavily_search
"""

import os
import requests


def _load_api_key() -> str:
    key = os.environ.get('TAVILY_API_KEY', '')
    if not key:
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))), '.env')
            with open(env_path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('TAVILY_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        break
        except Exception:
            pass
    return key


def main(args=None):
    """
    Tavily 实时网络搜索。

    参数:
      query       : 搜索关键词或问题（必填）
      max_results : 返回结果数量，默认 5，最大 10
      search_depth: 'basic'（快速）或 'advanced'（深度，更慢更全，默认 basic）
      topic       : 'general'（默认）或 'news'（新闻模式）
    """
    if args is None:
        args = {}

    query        = args.get('query', '') or args.get('topic', '') or args.get('keyword', '')
    max_results  = min(int(args.get('max_results', 5)), 10)
    search_depth = args.get('search_depth', 'basic')
    topic        = args.get('topic_mode', 'general')   # 避免和 query 别名冲突

    if not query:
        return {
            'result': {'error': '请提供 query 参数'},
            'insights': ['tavily_search: 缺少搜索关键词']
        }

    api_key = _load_api_key()
    if not api_key:
        return {
            'result': {'error': 'TAVILY_API_KEY 未配置'},
            'insights': ['tavily_search: 未找到 API Key']
        }

    try:
        resp = requests.post(
            'https://api.tavily.com/search',
            json={
                'api_key':      api_key,
                'query':        query,
                'max_results':  max_results,
                'search_depth': search_depth,
                'topic':        topic,
                'include_answer': True,
            },
            timeout=20
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout:
        return {'result': {'error': 'Tavily 请求超时'}, 'insights': ['tavily_search: 超时']}
    except Exception as e:
        return {'result': {'error': str(e)}, 'insights': [f'tavily_search 请求失败: {e}']}

    results = data.get('results', [])
    answer  = data.get('answer') or ''

    # 整理摘要
    snippets = []
    for r in results:
        title   = r.get('title', '')
        url     = r.get('url', '')
        content = r.get('content', '')[:300]
        snippets.append(f"[{title}] {content}  ({url})")

    combined = '\n'.join(snippets)
    summary  = (answer or (snippets[0] if snippets else '无结果'))[:400]

    return {
        'result': {
            'query':    query,
            'answer':   answer,
            'results':  [{'title': r.get('title'), 'url': r.get('url'),
                          'content': r.get('content', '')[:400]} for r in results],
            'count':    len(results),
        },
        'insights': [
            f"Tavily搜索[{query}] 返回 {len(results)} 条结果",
            summary[:200],
        ],
        'memories': [{
            'event_type': 'external_knowledge_acquired',
            'content':    f"[Tavily] {query}: {combined[:500]}",
            'importance': 0.75,
            'tags':       f"search,tavily,{query[:30]}"
        }]
    }
