"""
图片质量评估技能模块
需求: 评估图像质量：分析图像的清晰度、噪点、对比度、亮度等质量指标，并给出综合质量评分
"""

# skill_name: image_quality_assessor
import cv2
import numpy as np
import os
from PIL import Image

def main(args=None):
    """
    评估图像质量
    
    参数:
    - args: 包含图像路径的参数字典，格式为 {'image_path': 'path/to/image.jpg'}
    
    返回:
    - dict: 包含质量评估结果的字典
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '图像路径不存在'},
            'insights': ['质量评估失败：指定路径不存在']
        }
    
    try:
        # 读取图像
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. 清晰度评估（使用Laplacian方差）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 2. 噪点评估（使用局部方差）
        kernel_size = min(5, min(height, width) // 10)
        if kernel_size % 2 == 0:
            kernel_size += 1
        local_mean = cv2.blur(gray.astype(np.float64), (kernel_size, kernel_size))
        local_var = cv2.blur((gray.astype(np.float64) - local_mean) ** 2, (kernel_size, kernel_size))
        noise_level = np.mean(local_var)
        
        # 3. 对比度评估
        contrast = gray.std()
        
        # 4. 亮度评估
        brightness = gray.mean()
        
        # 5. 色彩饱和度（如果是彩色图像）
        saturation = 0
        if len(img.shape) == 3 and img.shape[2] == 3:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            saturation = hsv[:, :, 1].mean()
        
        # 6. 锐度评估
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sharpness = np.mean(sobel_magnitude)
        
        # 归一化各项指标（简化版）
        # 清晰度分数（0-10）
        clarity_score = min(laplacian_var / 100, 10)
        
        # 噪点分数（越低越好，所以用10减去归一化值）
        noise_score = max(0, 10 - min(noise_level / 100, 10))
        
        # 对比度分数（0-10）
        contrast_score = min(contrast / 25.5, 10)
        
        # 亮度分数（理想值在100-150之间）
        brightness_score = 10 - abs(brightness - 127.5) / 12.75
        
        # 饱和度分数（0-10）
        saturation_score = min(saturation / 25.5, 10) if saturation > 0 else 0
        
        # 锐度分数（0-10）
        sharpness_score = min(sharpness / 10, 10)
        
        # 综合质量评分
        quality_score = (clarity_score + noise_score + contrast_score + 
                        brightness_score + saturation_score + sharpness_score) / 6
        
        # 质量等级
        if quality_score >= 8:
            quality_level = "excellent"
        elif quality_score >= 6:
            quality_level = "good"
        elif quality_score >= 4:
            quality_level = "fair"
        elif quality_score >= 2:
            quality_level = "poor"
        else:
            quality_level = "very_poor"
        
        result = {
            'image_path': image_path,
            'dimensions': {'width': width, 'height': height},
            'quality_score': float(quality_score),
            'quality_level': quality_level,
            'detailed_scores': {
                'clarity': float(clarity_score),
                'noise': float(noise_score),
                'contrast': float(contrast_score),
                'brightness': float(brightness_score),
                'saturation': float(saturation_score),
                'sharpness': float(sharpness_score)
            },
            'raw_metrics': {
                'laplacian_variance': float(laplacian_var),
                'noise_level': float(noise_level),
                'contrast_value': float(contrast),
                'brightness_value': float(brightness),
                'saturation_value': float(saturation),
                'sharpness_value': float(sharpness)
            },
            'assessment_method': 'multi_metric_quality_analysis'
        }
        
        insights = [
            f"图像综合质量评分: {quality_score:.2f}/10.00 ({quality_level})",
            f"清晰度: {clarity_score:.2f}, 噪点控制: {noise_score:.2f}",
            f"对比度: {contrast_score:.2f}, 亮度: {brightness_score:.2f}"
        ]
        
        if saturation > 0:
            insights.append(f"色彩饱和度: {saturation_score:.2f}")
        
        if quality_level == "excellent":
            insights.append("图像质量优秀，适合高要求的应用场景")
        elif quality_level == "good":
            insights.append("图像质量良好，适合大多数应用场景")
        elif quality_level == "fair":
            insights.append("图像质量一般，可能需要后期处理")
        else:
            insights.append("图像质量较差，建议重新拍摄或获取更高质量的源文件")
        
        return {
            'result': result,
            'insights': insights
        }
    
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'质量评估失败：{str(e)}']
        }