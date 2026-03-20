"""
iFlow 视觉感知技能
使用 iFlow/SiliconFlow 的 Qwen-VL 视觉大模型真正"看懂"图片
比 ResNet50 分类强一个数量级——可以自由问答、OCR、场景理解、物体描述

生成时间: 2026-03-12（从旧项目 iflow_vision_adapter.py 提炼）
"""

# skill_name: iflow_vision_analyzer

import base64
import os
import requests

def main(args=None):
    """
    用 Qwen-VL 大模型分析图片。

    args 参数说明（以下三选一）：
      - image_path   : 本地图片文件路径
      - image_url    : 图片 URL
      - image_base64 : base64 编码的图片数据

    可选参数：
      - prompt       : 分析问题，默认"请详细描述这张图片的内容"
      - mode         : "describe"（描述）/ "objects"（列物体）/ "ocr"（提文字）
                       / "scene"（场景理解）/ "custom"（自定义 prompt）
    """
    if args is None:
        args = {}

    # ── 读取环境配置 ──────────────────────────────────────────────────
    api_key  = os.getenv("IFLOW_API_KEY") or args.get("api_key", "")
    base_url = os.getenv("IFLOW_BASE_URL", "https://apis.iflow.cn/v1")
    model    = os.getenv("VISION_MODEL", "qwen-vl-max")

    if not api_key:
        # 尝试从 .env 文件直接读取（兼容没有加载 dotenv 的场景）
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        env_path = os.path.normpath(env_path)
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("IFLOW_API_KEY="):
                        api_key = line.split("=", 1)[1].strip()
                    elif line.startswith("IFLOW_BASE_URL="):
                        base_url = line.split("=", 1)[1].strip()
                    elif line.startswith("VISION_MODEL="):
                        model = line.split("=", 1)[1].strip()

    if not api_key:
        return {
            "result": {"error": "未找到 IFLOW_API_KEY，请在 .env 中配置"},
            "insights": ["缺少 API Key，无法调用 Qwen-VL 视觉模型"]
        }

    # ── 构建图片内容 ──────────────────────────────────────────────────
    image_path   = args.get("image_path", "")
    image_url    = args.get("image_url", "")
    image_base64 = args.get("image_base64", "")
    mode         = args.get("mode", "describe")
    custom_prompt = args.get("prompt", "")

    mode_prompts = {
        "describe": "请详细描述这张图片的内容，包括主体、背景、颜色、构图等细节。",
        "objects":  "请详细列出图片中包含的所有物体，对每个物体给出名称、描述和大概位置。",
        "ocr":      "请识别并提取图片中的所有文字内容，保持原始格式，标注语言类型。",
        "scene":    "请详细描述图片的场景、背景和环境，分析可能的时间、地点、情境和人物活动。",
        "custom":   custom_prompt or "请描述这张图片。",
    }
    prompt = mode_prompts.get(mode, mode_prompts["describe"])

    # 构建 image_url 字段
    if image_path:
        if not os.path.exists(image_path):
            return {
                "result": {"error": f"文件不存在: {image_path}"},
                "insights": [f"图片路径无效: {image_path}"]
            }
        with open(image_path, "rb") as f:
            raw = f.read()
        ext = os.path.splitext(image_path)[1].lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(ext, "jpeg")
        b64 = base64.b64encode(raw).decode("ascii")
        img_url_value = f"data:image/{mime};base64,{b64}"
    elif image_url:
        img_url_value = image_url
    elif image_base64:
        img_url_value = f"data:image/jpeg;base64,{image_base64}"
    else:
        return {
            "result": {"error": "请提供 image_path / image_url / image_base64 之一"},
            "insights": ["缺少图片输入参数"]
        }

    # ── 调用 API ──────────────────────────────────────────────────────
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text",      "text": prompt},
                {"type": "image_url", "image_url": {"url": img_url_value}},
            ]
        }],
        "max_tokens": 1500,
        "temperature": 0.5,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = requests.post(
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            description = data["choices"][0]["message"]["content"]
            return {
                "result": {
                    "description": description,
                    "model": model,
                    "mode": mode,
                    "prompt": prompt,
                },
                "insights": [
                    f"[{mode}] Qwen-VL 分析完成",
                    description[:200] + ("..." if len(description) > 200 else ""),
                ],
                "memories": [{
                    "event_type": "learning",
                    "content": f"视觉分析[{mode}]: {description[:300]}",
                    "importance": 0.8,
                    "tags": f"vision,{mode},qwen-vl"
                }]
            }
        else:
            return {
                "result": {"error": f"API 返回 {resp.status_code}", "body": resp.text[:500]},
                "insights": [f"Qwen-VL API 调用失败: {resp.status_code}"]
            }
    except Exception as e:
        return {
            "result": {"error": str(e)},
            "insights": [f"Qwen-VL 调用异常: {e}"]
        }
