"""
图片风格分析技能模块
需求: 分析图像的艺术风格和视觉特征：识别图像是否为照片、绘画、素描、卡通等，并提取色彩分布和纹理特征
"""

# skill_name: image_style_analyzer
import cv2
import numpy as np
import os
from PIL import Image
from skimage.feature import greycomatrix, greycoprops

def main(args=None):
    """
    分析图像的艺术风格和视觉特征
    
    参数:
    - args: 包含图像路径的参数字典，格式为 {'image_path': 'path/to/image.jpg'}
    
    返回:
    - dict: 包含风格分析结果的字典
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '图像路径不存在'},
            'insights': ['风格分析失败：指定路径不存在']
        }
    
    try:
        # 读取图像
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        # 转换为RGB用于分析
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 计算基本统计信息
        mean_color = np.mean(img_rgb, axis=(0, 1))
        std_color = np.std(img_rgb, axis=(0, 1))
        
        # 转换为灰度图进行纹理分析
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 计算GLCM（灰度共生矩阵）特征
        glcm = greycomatrix(gray, distances=[5], angles=[0], levels=256, symmetric=True, normed=True)
        contrast = greycoprops(glcm, 'contrast')[0, 0]
        dissimilarity = greycoprops(glcm, 'dissimilarity')[0, 0]
        homogeneity = greycoprops(glcm, 'homogeneity')[0, 0]
        energy = greycoprops(glcm, 'energy')[0, 0]
        correlation = greycoprops(glcm, 'correlation')[0, 0]
        
        # 简单的风格分类启发式规则
        style_classification = "unknown"
        
        # 基于对比度和纹理复杂度的简单分类
        if contrast < 100 and homogeneity > 0.8:
            style_classification = "drawing_or_sketch"
        elif contrast > 300 and energy < 0.1:
            style_classification = "photograph"
        elif dissimilarity > 5 and correlation < 0.5:
            style_classification = "painting"
        else:
            style_classification = "mixed_or_other"
        
        # 色彩饱和度分析
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation_mean = np.mean(hsv[:, :, 1])
        value_mean = np.mean(hsv[:, :, 2])
        
        # 判断是否为黑白图像
        is_grayscale = std_color[0] < 10 and std_color[1] < 10 and std_color[2] < 10
        
        result = {
            'image_path': image_path,
            'dimensions': {'width': width, 'height': height},
            'mean_color_rgb': [float(mean_color[0]), float(mean_color[1]), float(mean_color[2])],
            'std_color_rgb': [float(std_color[0]), float(std_color[1]), float(std_color[2])],
            'is_grayscale': bool(is_grayscale),
            'saturation_mean': float(saturation_mean),
            'brightness_mean': float(value_mean),
            'texture_features': {
                'contrast': float(contrast),
                'dissimilarity': float(dissimilarity),
                'homogeneity': float(homogeneity),
                'energy': float(energy),
                'correlation': float(correlation)
            },
            'style_classification': style_classification,
            'analysis_method': 'statistical_and_texture_analysis'
        }
        
        insights = [
            f"图像风格初步分类为: {style_classification}",
            f"色彩饱和度: {saturation_mean:.2f}, 亮度: {value_mean:.2f}",
            f"纹理对比度: {contrast:.2f}, 同质性: {homogeneity:.2f}"
        ]
        
        if is_grayscale:
            insights.append("图像为黑白/灰度图像")
        else:
            insights.append("图像为彩色图像")
        
        return {
            'result': result,
            'insights': insights
        }
    
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'风格分析失败：{str(e)}']
        }