"""
多源学习技能（修复版）
依次尝试 Wikipedia → arXiv → DuckDuckGo，无需任何 API Key。

skill_name: multi_source_learning_fixed
"""

import requests
import urllib.parse
import json


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


def main(input_args=""):
    """
    多源学习主入口。

    参数:
      input_args: JSON字符串，包含以下字段：
        - topic: 要学习的主题（必填）
        - reason: 学习动机（可选，会存入记忆）
        - source: 指定来源 'wiki'/'arxiv'/'ddg'，默认自动降级
    """
    # 解析输入参数
    if not input_args:
        return {
            'result': {'error': '请提供 input_args 参数'},
            'insights': ['multi_source_learning: 缺少输入参数']
        }
    
    try:
        # 尝试解析为JSON
        args = json.loads(input_args)
    except json.JSONDecodeError:
        # 如果不是JSON，尝试作为查询字符串解析
        import urllib.parse
        if '&' in input_args:
            args = {}
            for pair in input_args.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    args[key] = urllib.parse.unquote(value)
        else:
            # 如果只是简单字符串，当作topic
            args = {'topic': input_args}

    topic = args.get('topic', '') or args.get('query', '')
    reason = args.get('reason', '自主探索')
    source = args.get('source', 'auto')

    if not topic:
        return {
            'result': {'error': '请提供 topic 参数'},
            'insights': ['multi_source_learning: 缺少学习主题']
        }

    if source == 'wiki':
        strategies = [_wiki]
    elif source == 'arxiv':
        strategies = [_arxiv]
    elif source == 'ddg':
        strategies = [_duckduckgo]
    else:
        strategies = [_wiki, _arxiv, _duckduckgo]

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