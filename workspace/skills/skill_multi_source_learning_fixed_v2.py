"""
多源学习技能（修复版v2）
依次尝试 Wikipedia → arXiv → DuckDuckGo，无需任何 API Key。

skill_name: multi_source_learning_fixed_v2
"""

import requests
import urllib.parse


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
      args: dict 或 str，dict 时读取 args['topic'] 或 args['input']；
            也接受 __context__ 注入的上下文。
    返回: 包含 insights/facts 键的 dict，自动传播到主系统记忆和知识图谱。
    """
    # ── 解析入参 ──────────────────────────────────────────────
    if isinstance(args, dict):
        topic = (args.get("topic") or args.get("input") or "").strip()
        reason = args.get("reason", "自主探索")
        source = args.get("source", "auto")
        if not topic:
            ctx = args.get("__context__", {})
            recent = ctx.get("recent_memories", [])
            topic = "predictive coding" if not recent else (
                str(recent[0].get("content", "predictive coding"))[:40]
            )
    elif isinstance(args, str) and args.strip():
        topic = args.strip()
        reason = "自主探索"
        source = "auto"
    else:
        topic = "predictive coding"
        reason = "自主探索"
        source = "auto"

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
            'ok': False,
            'topic': topic,
            'error': f'所有来源均未找到: {topic}',
            'insights': [f'multi_source_learning: "{topic}" 无结果'],
            'memories': [
                {
                    'event_type': 'tool_error',
                    'content': f'multi_source_learning/{topic}: 所有来源均未找到',
                    'importance': 0.2,
                }
            ]
        }

    extract = str(result_data.get('extract', ''))
    return {
        'ok': True,
        'topic': topic,
        'title': result_data.get('title', topic),
        'extract': extract[:800],
        'url': result_data.get('url', ''),
        'source': result_data['source'],
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