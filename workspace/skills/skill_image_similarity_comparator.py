"""
图片相似度比较技能模块
需求: 比较两张图像的相似度：计算两张图像在色彩、结构和内容方面的相似度，并返回综合相似度评分
"""

# skill_name: image_similarity_comparator
import cv2
import numpy as np
import os
from PIL import Image

def main(args=None):
    """
    比较两张图像的相似度
    
    参数:
    - args: 包含两张图像路径的参数字典，格式为 {'image_path_1': 'path/to/image1.jpg', 'image_path_2': 'path/to/image2.jpg'}
    
    返回:
    - dict: 包含相似度比较结果的字典
    """
    if args is None:
        args = {}
    
    image_path_1 = args.get('image_path_1', '')
    image_path_2 = args.get('image_path_2', '')
    
    if not image_path_1 or not os.path.exists(image_path_1):
        return {
            'result': {'error': '第一张图像路径不存在'},
            'insights': ['相似度比较失败：第一张图像路径不存在']
        }
    
    if not image_path_2 or not os.path.exists(image_path_2):
        return {
            'result': {'error': '第二张图像路径不存在'},
            'insights': ['相似度比较失败：第二张图像路径不存在']
        }
    
    try:
        # 读取图像
        img1 = cv2.imread(image_path_1)
        img2 = cv2.imread(image_path_2)
        
        # 获取原始尺寸
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]
        
        # 调整到相同尺寸进行比较（使用较小的尺寸）
        min_h = min(h1, h2)
        min_w = min(w1, w2)
        
        img1_resized = cv2.resize(img1, (min_w, min_h))
        img2_resized = cv2.resize(img2, (min_w, min_h))
        
        # 1. 像素级相似度（MSE和SSIM）
        mse = np.mean((img1_resized.astype(np.float64) - img2_resized.astype(np.float64)) ** 2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        # 简化的SSIM计算
        def calculate_ssim(img1, img2):
            C1 = (0.01 * 255)**2
            C2 = (0.03 * 255)**2
            
            img1 = img1.astype(np.float64)
            img2 = img2.astype(np.float64)
            kernel = cv2.getGaussianKernel(11, 1.5)
            window = np.outer(kernel, kernel.transpose())
            
            mu1 = cv2.filter2D(img1, -1, window)[5:-5, 5:-5]
            mu2 = cv2.filter2D(img2, -1, window)[5:-5, 5:-5]
            mu1_sq = mu1**2
            mu2_sq = mu2**2
            mu1_mu2 = mu1 * mu2
            sigma1_sq = cv2.filter2D(img1**2, -1, window)[5:-5, 5:-5] - mu1_sq
            sigma2_sq = cv2.filter2D(img2**2, -1, window)[5:-5, 5:-5] - mu2_sq
            sigma12 = cv2.filter2D(img1 * img2, -1, window)[5:-5, 5:-5] - mu1_mu2
            
            ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
            return ssim_map.mean()
        
        # 计算灰度SSIM
        gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
        ssim_score = calculate_ssim(gray1, gray2)
        
        # 2. 色彩直方图相似度
        hist1 = cv2.calcHist([img1_resized], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
        hist2 = cv2.calcHist([img2_resized], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
        hist_similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # 3. 结构相似度（基于边缘检测）
        edges1 = cv2.Canny(gray1, 100, 200)
        edges2 = cv2.Canny(gray2, 100, 200)
        edge_similarity = np.sum((edges1 & edges2)) / np.sum((edges1 | edges2)) if np.sum((edges1 | edges2)) > 0 else 0
        
        # 综合相似度评分（加权平均）
        # SSIM权重最高，然后是直方图和边缘相似度
        combined_similarity = (ssim_score * 0.5 + 
                              max(0, min(1, hist_similarity)) * 0.3 + 
                              edge_similarity * 0.2)
        
        # 转换为0-10分制
        similarity_score = combined_similarity * 10
        
        # 相似度等级
        if similarity_score >= 8:
            similarity_level = "very_high"
        elif similarity_score >= 6:
            similarity_level = "high"
        elif similarity_score >= 4:
            similarity_level = "moderate"
        elif similarity_score >= 2:
            similarity_level = "low"
        else:
            similarity_level = "very_low"
        
        result = {
            'image_path_1': image_path_1,
            'image_path_2': image_path_2,
            'original_dimensions': {
                'image1': {'width': w1, 'height': h1},
                'image2': {'width': w2, 'height': h2}
            },
            'comparison_dimensions': {'width': min_w, 'height': min_h},
            'similarity_score': float(similarity_score),
            'similarity_level': similarity_level,
            'detailed_metrics': {
                'ssim': float(ssim_score),
                'histogram_correlation': float(max(0, min(1, hist_similarity))),
                'edge_similarity': float(edge_similarity),
                'psnr': float(psnr) if psnr != float('inf') else float('inf'),
                'mse': float(mse)
            },
            'comparison_method': 'multi_metric_similarity_analysis'
        }
        
        insights = [
            f"图像相似度评分: {similarity_score:.2f}/10.00 ({similarity_level})",
            f"结构相似度(SSIM): {ssim_score:.3f}",
            f"色彩直方图相关性: {max(0, min(1, hist_similarity)):.3f}",
            f"边缘结构相似度: {edge_similarity:.3f}"
        ]
        
        if similarity_level == "very_high":
            insights.append("两张图像非常相似，可能是同一图像的不同版本或轻微编辑")
        elif similarity_level == "high":
            insights.append("两张图像高度相似，可能包含相同的主体或场景")
        elif similarity_level == "moderate":
            insights.append("两张图像有一定相似性，但存在明显差异")
        else:
            insights.append("两张图像相似度较低，可能是完全不同的内容")
        
        return {
            'result': result,
            'insights': insights
        }
    
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'相似度比较失败：{str(e)}']
        }