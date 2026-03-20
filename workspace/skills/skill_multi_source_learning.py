"""
多源学习技能（从旧项目迁移，已升级 Tavily 优先）
降级链：Tavily → Wikipedia → arXiv → DuckDuckGo。
Tavily 为首选（实时网络，覆盖面最广），无 Key 时自动降级。

skill_name: multi_source_learning
"""

import os
import requests
import urllib.parse


def _tavily(topic: str) -> dict:
    """Tavily 实时网络搜索（首选）"""
    api_key = os.environ.get('TAVILY_API_KEY', '')
    if not api_key:
        try:
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))), '.env')
            with open(env_path, encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('TAVILY_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip()
                        break
        except Exception:
            pass
    if not api_key:
        return {'success': False}
    try:
        r = requests.post(
            'https://api.tavily.com/search',
            json={'api_key': api_key, 'query': topic,
                  'max_results': 3, 'include_answer': True},
            timeout=15
        )
        if r.status_code == 200:
            d = r.json()
            answer   = d.get('answer') or ''
            results  = d.get('results', [])
            snippets = ' | '.join(r2.get('content', '')[:200] for r2 in results[:2])
            extract  = answer if answer else snippets
            if extract:
                return {
                    'success': True, 'source': 'tavily',
                    'title':   topic,
                    'extract': extract,
                    'url':     results[0].get('url', '') if results else '',
                }
    except Exception:
        pass
    return {'success': False}


def _wiki(topic: str) -> dict:
    """英文 → 中文 Wikipedia 降级搜索"""
    for lang in ('en', 'zh'):
        try:
            url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                d = r.json()
                return {
                    'success': True, 'source': f'wikipedia_{lang}',
                    'title':   d.get('title', ''),
                    'extract': d.get('extract', ''),
                    'url':     d.get('content_urls', {}).get('desktop', {}).get('page', ''),
                }
        except Exception:
            pass
    return {'success': False}


def _arxiv(topic: str) -> dict:
    """arXiv 学术论文搜索（最多返回摘要）"""
    try:
        q = urllib.parse.quote(topic)
        url = f"http://export.arxiv.org/api/query?search_query=all:{q}&max_results=1"
        r = requests.get(url, timeout=8)
        if r.status_code == 200 and '<entry>' in r.text:
            import re
            title   = (re.search(r'<title>(.*?)</title>', r.text, re.S) or ['', ''])[1].strip()
            summary = (re.search(r'<summary>(.*?)</summary>', r.text, re.S) or ['', ''])[1].strip()
            return {
                'success': True, 'source': 'arxiv',
                'title': title, 'extract': summary[:600],
                'url': '',
            }
    except Exception:
        pass
    return {'success': False}


def _duckduckgo(topic: str) -> dict:
    """DuckDuckGo 即时答案 API（无需 Key）"""
    try:
        q = urllib.parse.quote(topic)
        url = f"https://api.duckduckgo.com/?q={q}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=8,
                         headers={'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/6.0)'})
        if r.status_code == 200:
            d = r.json()
            abstract = d.get('AbstractText', '') or d.get('Answer', '')
            if abstract:
                return {
                    'success': True, 'source': 'duckduckgo',
                    'title':   d.get('Heading', topic),
                    'extract': abstract,
                    'url':     d.get('AbstractURL', ''),
                }
    except Exception:
        pass
    return {'success': False}


def main(args=None):
    """
    多源学习主入口。

    参数:
      topic  : 要学习的主题（必填）
      reason : 学习动机（可选，会存入记忆）
      source : 指定来源 'wiki'/'arxiv'/'ddg'，默认自动降级
    """
    if args is None:
        args = {}

    topic  = args.get('topic', '') or args.get('query', '')
    reason = args.get('reason', '自主探索')
    source = args.get('source', 'auto')

    if not topic:
        return {
            'result': {'error': '请提供 topic 参数'},
            'insights': ['multi_source_learning: 缺少学习主题']
        }

    if source == 'tavily':
        strategies = [_tavily]
    elif source == 'wiki':
        strategies = [_wiki]
    elif source == 'arxiv':
        strategies = [_arxiv]
    elif source == 'ddg':
        strategies = [_duckduckgo]
    else:
        strategies = [_tavily, _wiki, _arxiv, _duckduckgo]

    result_data = {'success': False}
    for fn in strategies:
        result_data = fn(topic)
        if result_data.get('success'):
            break

    if not result_data.get('success'):
        return {
            'result': {'error': f'所有来源均未找到: {topic}'},
            'insights': [f'multi_source_learning: "{topic}" 无结果']
        }

    extract = str(result_data.get('extract', ''))
    return {
        'result': result_data,
        'insights': [
            f"来源={result_data['source']}  主题={result_data.get('title', topic)}",
            extract[:200] + ('...' if len(extract) > 200 else ''),
        ],
        'memories': [{
            'event_type': 'learning',
            'content': f"[{result_data['source']}] {topic}: {extract[:400]}",
            'importance': 0.75,
            'tags': f"learning,{result_data['source']},{topic[:30]}"
        }]
    }
