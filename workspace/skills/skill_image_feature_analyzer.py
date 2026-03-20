"""
图像特征分析技能（从旧项目迁移）
使用 OpenCV 检测边缘、轮廓和基本特征，比 PIL 更底层、更精确。

skill_name: image_feature_analyzer
"""

import cv2
import numpy as np
import os


def main(args=None):
    """
    图像特征分析：边缘检测 + 轮廓提取 + 强度统计。

    参数:
      image_path  : 图片路径（必填）
      blur_kernel : 高斯模糊核大小，默认 5
      canny_low   : Canny 低阈值，默认 50
      canny_high  : Canny 高阈值，默认 150
    """
    if args is None:
        args = {}

    image_path  = args.get('image_path', '')
    blur_kernel = args.get('blur_kernel', 5)
    canny_low   = args.get('canny_low', 50)
    canny_high  = args.get('canny_high', 150)

    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': f'图片路径不存在: {image_path}'},
            'insights': ['image_feature_analyzer: 路径无效']
        }

    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f'cv2 无法读取图片: {image_path}')

        gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (blur_kernel, blur_kernel), 0)
        edges   = cv2.Canny(blurred, canny_low, canny_high)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour_areas      = [cv2.contourArea(c) for c in contours]
        contour_perimeters = [cv2.arcLength(c, True) for c in contours]
        filtered_contours  = [c for c, a in zip(contours, contour_areas) if a > 100]

        result = {
            'image_shape':          list(image.shape),
            'edge_pixel_count':     int(np.sum(edges > 0)),
            'total_contours':       len(contours),
            'filtered_contours':    len(filtered_contours),
            'mean_intensity':       round(float(np.mean(gray)), 2),
            'std_intensity':        round(float(np.std(gray)), 2),
            'max_contour_area':     round(float(max(contour_areas)), 2) if contour_areas else 0,
            'avg_contour_area':     round(float(np.mean(contour_areas)), 2) if contour_areas else 0,
            'max_contour_perimeter':round(float(max(contour_perimeters)), 2) if contour_perimeters else 0,
        }

        return {
            'result': result,
            'insights': [
                f"检测到 {len(filtered_contours)} 个显著轮廓，边缘像素 {result['edge_pixel_count']}",
                f"平均灰度强度 {result['mean_intensity']}，标准差 {result['std_intensity']}",
            ],
            'memories': [{
                'event_type': 'skill_executed',
                'content': f"image_feature_analyzer: {result['filtered_contours']} 轮廓, 边缘像素={result['edge_pixel_count']}",
                'importance': 0.6
            }]
        }

    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'image_feature_analyzer 失败: {e}']
        }
