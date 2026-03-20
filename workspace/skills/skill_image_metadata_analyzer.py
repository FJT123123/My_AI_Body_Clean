"""
自动生成的技能模块
需求: 分析图像基本信息：读取图像文件，获取尺寸、格式、色彩空间等元数据，并进行基础质量评估
生成时间: 2026-03-12 15:43:17
"""

# skill_name: image_metadata_analyzer
import os
from PIL import Image

def main(args=None):
    """
    分析图像基本信息：读取图像文件，获取尺寸、格式、色彩空间等元数据，并进行基础质量评估
    
    参数:
    - args: 包含图像路径的参数字典，格式为 {'image_path': 'path/to/image.jpg'}
    
    返回:
    - dict: 包含图像元数据和质量评估结果的字典
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '图像路径不存在'},
            'insights': ['图像分析失败：指定路径不存在']
        }
    
    try:
        with Image.open(image_path) as img:
            # 获取图像基本元数据
            width, height = img.size
            format = img.format
            mode = img.mode
            channels = len(mode) if mode else 0
            
            # 计算图像分辨率（DPI），如果有的话
            dpi = img.info.get('dpi', None)
            
            # 计算图像文件大小
            file_size = os.path.getsize(image_path)
            
            # 基础质量评估指标
            total_pixels = width * height
            aspect_ratio = width / height if height != 0 else float('inf')
            
            # 简单的清晰度评估（基于像素总数和分辨率）
            clarity_score = min(total_pixels / 1000000, 10)  # 标准化到0-10分
            
            # 格式质量评估
            quality_indicators = {
                'lossless': format in ['PNG', 'TIFF', 'BMP'],
                'high_compression': format in ['JPEG'],
                'web_optimized': format in ['JPEG', 'PNG', 'GIF', 'WEBP']
            }
            
            metadata = {
                'path': image_path,
                'width': width,
                'height': height,
                'format': format,
                'mode': mode,
                'channels': channels,
                'dpi': dpi,
                'file_size_bytes': file_size,
                'total_pixels': total_pixels,
                'aspect_ratio': round(aspect_ratio, 3),
                'clarity_score': round(clarity_score, 2)
            }
            
            metadata.update(quality_indicators)
            
            # 根据分析结果生成洞察
            insights = [
                f"图像尺寸为 {width}x{height}，格式为 {format}",
                f"图像总像素数为 {total_pixels:,}，清晰度评分为 {clarity_score:.2f}/10.00"
            ]
            
            if quality_indicators['lossless']:
                insights.append("图像采用无损压缩格式，质量较高")
            elif quality_indicators['high_compression']:
                insights.append("图像采用高压缩格式（如JPEG），可能存在质量损失")
            
            if quality_indicators['web_optimized']:
                insights.append("图像格式适合网络使用")
            
            return {
                'result': metadata,
                'insights': insights
            }
    
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'图像分析失败：{str(e)}']
        }