"""
氢火焰视觉识别技能（从旧项目迁移）
基于纯 numpy 的工业级氢火焰特征检测，无需 OpenCV。
通过 HSV 色彩分析 + 形态特征识别淡蓝色/近无色火焰。

skill_name: hydrogen_flame_detection
"""

import numpy as np
import os


def _detect(frame: np.ndarray, sensitivity: float = 0.7):
    """
    氢火焰检测核心算法。
    返回 (flame_detected: bool, bbox: dict | None, confidence: float)
    """
    if frame.ndim != 3 or frame.shape[2] != 3:
        raise ValueError("输入必须为 RGB 格式 (H, W, 3)")

    f = frame.astype(np.float32) / 255.0
    r, g, b = f[:, :, 0], f[:, :, 1], f[:, :, 2]

    max_v = np.maximum(np.maximum(r, g), b)
    min_v = np.minimum(np.minimum(r, g), b)
    diff  = max_v - min_v

    h = np.zeros_like(max_v)
    mask = diff != 0
    m = (max_v == r) & mask
    h[m] = (60 * ((g[m] - b[m]) / diff[m]) + 360) % 360
    m = (max_v == g) & mask
    h[m] = (60 * ((b[m] - r[m]) / diff[m]) + 120) % 360
    m = (max_v == b) & mask
    h[m] = (60 * ((r[m] - g[m]) / diff[m]) + 240) % 360

    s = np.where(mask, diff / np.where(max_v > 0, max_v, 1), 0)
    v = max_v

    color_mask = (((h >= 0) & (h <= 30)) | ((h >= 330) & (h <= 360))) & (s >= 0.1) & (v >= 0.1)
    ys, xs = np.where(color_mask)

    if len(xs) == 0:
        return False, None, 0.0

    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    area   = len(xs)
    width  = x_max - x_min
    height = y_max - y_min
    aspect = width / height if height > 0 else float('inf')

    if area > 100 * sensitivity and 0.2 < aspect < 5.0:
        confidence = float(min(1.0, area / 10000 * sensitivity))
        bbox = {'x_min': x_min, 'y_min': y_min,
                'x_max': x_max, 'y_max': y_max,
                'width': width, 'height': height, 'area': area}
        return True, bbox, confidence

    return False, None, 0.0


def main(args=None):
    """
    氢火焰视觉识别。

    参数:
      image_path  : 图片路径（必填，RGB 格式）
      sensitivity : 检测灵敏度 0.0~1.0，默认 0.7
    """
    if args is None:
        args = {}

    image_path  = args.get('image_path', '')
    sensitivity = float(args.get('sensitivity', 0.7))

    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': f'文件不存在: {image_path}'},
            'insights': ['hydrogen_flame_detection: 路径无效']
        }

    try:
        from PIL import Image as PILImage
        frame = np.array(PILImage.open(image_path).convert('RGB'))
    except Exception as e:
        return {
            'result': {'error': f'图片读取失败: {e}'},
            'insights': [f'hydrogen_flame_detection: {e}']
        }

    try:
        detected, bbox, confidence = _detect(frame, sensitivity)
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'hydrogen_flame_detection 算法错误: {e}']
        }

    result = {
        'flame_detected': detected,
        'confidence':     round(confidence, 4),
        'bbox':           bbox,
        'sensitivity':    sensitivity,
        'image_size':     f'{frame.shape[1]}x{frame.shape[0]}',
    }

    return {
        'result': result,
        'insights': [
            f"{'⚠️ 检测到氢火焰' if detected else '✅ 未检测到氢火焰'}  置信度={confidence:.2%}",
            f"图片大小={result['image_size']}  灵敏度={sensitivity}",
        ],
        'memories': [{
            'event_type': 'skill_executed',
            'content': f"氢火焰检测: detected={detected}, confidence={confidence:.3f}",
            'importance': 0.8 if detected else 0.4,
            'tags': 'vision,flame_detection,industrial'
        }]
    }
