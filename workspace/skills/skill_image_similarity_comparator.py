"""
自动生成的技能模块
需求: 视觉验证测试技能：接受两个图像路径作为JSON字符串参数，比较它们的相似度。正确处理字符串和字典参数。
生成时间: 2026-03-21 11:53:44
"""

# skill_name: image_similarity_comparator
import json
import os
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.transform import resize
import cv2

def main(args=None):
    """
    视觉验证测试技能：接受两个图像路径作为JSON字符串参数，比较它们的相似度。
    
    参数:
    - args: 包含图像路径参数的字典或JSON字符串
    
    返回:
    - 包含相似度计算结果和洞察信息的字典
    """
    if args is None:
        args = {}
    
    # 处理输入参数
    image_paths = args if isinstance(args, dict) else {}
    
    # 尝试从JSON字符串解析参数
    if not image_paths and isinstance(args, str):
        try:
            image_paths = json.loads(args)
        except json.JSONDecodeError:
            return {
                'result': {'error': 'Invalid JSON string provided'},
                'insights': ['Failed to parse input as JSON'],
                'capabilities': ['image_comparison']
            }
    
    # 检查是否提供了图像路径
    if 'image1_path' not in image_paths or 'image2_path' not in image_paths:
        return {
            'result': {'error': 'image1_path and image2_path are required'},
            'insights': ['Missing required image paths in input'],
            'capabilities': ['image_comparison']
        }
    
    image1_path = image_paths['image1_path']
    image2_path = image_paths['image2_path']
    
    # 检查图像文件是否存在
    if not os.path.exists(image1_path):
        return {
            'result': {'error': f'Image file does not exist: {image1_path}'},
            'insights': [f'Image file missing: {image1_path}'],
            'capabilities': ['image_comparison']
        }
    
    if not os.path.exists(image2_path):
        return {
            'result': {'error': f'Image file does not exist: {image2_path}'},
            'insights': [f'Image file missing: {image2_path}'],
            'capabilities': ['image_comparison']
        }
    
    try:
        # 使用PIL加载图像
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)
        
        # 转换为numpy数组
        img1_np = np.array(img1)
        img2_np = np.array(img2)
        
        # 确保图像尺寸一致
        if img1_np.shape != img2_np.shape:
            # 调整较小图像的尺寸以匹配较大图像
            height1, width1 = img1_np.shape[:2]
            height2, width2 = img2_np.shape[:2]
            target_height = min(height1, height2)
            target_width = min(width1, width2)
            
            img1_resized = cv2.resize(img1_np, (target_width, target_height))
            img2_resized = cv2.resize(img2_np, (target_width, target_height))
        else:
            img1_resized = img1_np
            img2_resized = img2_np
        
        # 确保图像为灰度图用于SSIM计算
        if len(img1_resized.shape) == 3:
            img1_gray = cv2.cvtColor(img1_resized, cv2.COLOR_RGB2GRAY)
        else:
            img1_gray = img1_resized
        
        if len(img2_resized.shape) == 3:
            img2_gray = cv2.cvtColor(img2_resized, cv2.COLOR_RGB2GRAY)
        else:
            img2_gray = img2_resized
        
        # 计算结构相似性指数
        ssim_score = ssim(img1_gray, img2_gray)
        
        # 计算均方误差（MSE）
        mse = np.mean((img1_gray - img2_gray) ** 2)
        
        # 计算PSNR（峰值信噪比）
        if mse == 0:
            psnr = float('inf')
        else:
            pixel_max = 255.0
            psnr = 20 * np.log10(pixel_max / np.sqrt(mse))
        
        # 计算归一化交叉相关系数（NCC）
        img1_norm = (img1_gray - np.mean(img1_gray)) / (np.std(img1_gray) * len(img1_gray.flat))
        img2_norm = (img2_gray - np.mean(img2_gray)) / (np.std(img2_gray))
        ncc = np.corrcoef(img1_norm.flat, img2_norm.flat)[0, 1]
        
        # 计算结果
        similarity_result = {
            'image1_path': image1_path,
            'image2_path': image2_path,
            'ssim_score': float(ssim_score),
            'mse': float(mse),
            'psnr': float(psnr) if psnr != float('inf') else 'inf',
            'ncc': float(ncc),
            'image1_shape': img1_np.shape,
            'image2_shape': img2_np.shape
        }
        
        # 根据SSIM分数判断相似度
        similarity_level = 'very_similar' if ssim_score > 0.9 else \
                          'similar' if ssim_score > 0.7 else \
                          'moderately_similar' if ssim_score > 0.5 else \
                          'dissimilar'
        
        insights = [
            f"Images compared with SSIM score: {ssim_score:.4f}",
            f"Similarity level: {similarity_level}",
            f"Mean Square Error: {mse:.4f}",
            f"Normalized Cross Correlation: {ncc:.4f}"
        ]
        
        return {
            'result': similarity_result,
            'insights': insights,
            'capabilities': ['image_comparison', 'visual_verification', 'similarity_analysis'],
            'facts': [
                [f"ImageComparison({image1_path}, {image2_path})", "ssim_score", str(ssim_score)],
                [f"ImageComparison({image1_path}, {image2_path})", "similarity_level", similarity_level]
            ]
        }
    
    except Exception as e:
        return {
            'result': {'error': f'Error processing images: {str(e)}'},
            'insights': [f'Image processing error: {str(e)}'],
            'capabilities': ['image_comparison']
        }