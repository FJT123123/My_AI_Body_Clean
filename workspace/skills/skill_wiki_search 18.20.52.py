# skill_name: skill_wiki_search
"""
通过 Wikipedia REST API 搜索指定主题，返回结构化摘要并写入知识三元组。
"""

import requests

def main(args=None):
    """
    搜索 Wikipedia 获取真实结构化知识。
    - args: dict 或 str，dict 时读取 args['topic'] 或 args['input']；
            也接受 __context__ 注入的上下文。
    返回: 包含 insights/facts 键的 dict，自动传播到主系统记忆和知识图谱。
    """
    # ── 解析入参 ──────────────────────────────────────────────
    if isinstance(args, dict):
        topic = (args.get("topic") or args.get("input") or "").strip()
        if not topic:
            ctx = args.get("__context__", {})
            recent = ctx.get("recent_memories", [])
            topic = "artificial intelligence" if not recent else (
                str(recent[0].get("content", "artificial intelligence"))[:40]
            )
    elif isinstance(args, str) and args.strip():
        topic = args.strip()
    else:
        topic = "artificial intelligence"

    # ── 查询 Wikipedia ────────────────────────────────────────
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
    headers = {"User-Agent": "OpenClaw-AI/1.0 (educational project; contact: openclaw@local)"}
    try:
        resp = requests.get(url, timeout=8, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return {
            "ok": False,
            "topic": topic,
            "error": str(e),
            "insights": [f"Wikipedia 查询失败: {topic} — {e}"],
            "facts": [],
            "memories": [
                {
                    "event_type": "tool_error",
                    "content": f"Wikipedia/{topic}: 查询失败 ({e})",
                    "importance": 0.2,
                }
            ],
        }

    title    = data.get("title", topic)
    extract  = data.get("extract", "")
    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
    description = data.get("description", "")

    # 空摘要视为查询失败，不写入高权重记忆
    if not extract:
        return {
            "ok": False,
            "topic": topic,
            "title": title,
            "extract": "",
            "url": page_url,
            "insights": [f"未找到 {topic} 的有效摘要"],
            "facts": [],
            "memories": [
                {
                    "event_type": "tool_error",
                    "content": f"Wikipedia/{title}: 返回空摘要",
                    "importance": 0.2,
                }
            ],
        }

    # ── 构建知识三元组 ─────────────────────────────────────────
    facts = [
        {"subject": title, "relation": "is_a", "object": description or "concept"},
        {"subject": title, "relation": "source_url", "object": page_url},
    ]
    first_sentence = extract.split(". ")[0] if extract else ""
    if first_sentence:
        facts.append({"subject": title, "relation": "defined_as",
                      "object": first_sentence[:200]})

    insights = [
        f"{title}：{extract[:300]}",
    ]

    return {
        "ok": True,
        "topic": topic,
        "title": title,
        "extract": extract[:800],
        "url": page_url,
        "insights": insights,
        "facts": facts,
        "memories": [
            {
                "event_type": "external_knowledge_acquired",
                "content": f"Wikipedia/{title}: {extract[:200]}",
                "importance": 0.75,
            }
        ],
    }
