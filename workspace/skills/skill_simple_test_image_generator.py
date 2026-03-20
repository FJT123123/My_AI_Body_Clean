"""
简单的测试图片生成器
创建一个高对比度的测试图片，确保文字能被OCR识别
"""

# skill_name: simple_test_image_generator

from PIL import Image, ImageDraw
import os

def main(args=None):
    if args is None:
        args = {}
    
    # 获取工作目录
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', './workspace')
    
    # 确保workspace目录存在
    os.makedirs(workspace_path, exist_ok=True)
    
    # 创建图像 - 黑底白字以确保高对比度
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(0, 0, 0))  # 黑色背景
    draw = ImageDraw.Draw(image)
    
    # 使用非常大的字体绘制文字（使用默认字体但放大）
    # 在PIL中，可以通过重复绘制来模拟粗体效果
    text1 = "OPENCLAW"
    text2 = "VISION TEST"
    
    # 绘制主文字 - 白色，大尺寸
    for i in range(-2, 3):
        for j in range(-2, 3):
            draw.text((150 + i, 150 + j), text1, fill=(255, 255, 255))
            draw.text((150 + i, 250 + j), text2, fill=(255, 255, 255))
    
    # 保存图像
    image_path = os.path.join(workspace_path, 'test_image.png')
    image.save(image_path)
    
    result = {
        'image_path': image_path,
        'success': True,
        'message': f'高对比度测试图片已保存到 {image_path}'
    }
    
    return {
        'result': result,
        'insights': [f'成功生成高对比度测试图片，保存路径: {image_path}'],
        'memories': [{
            'event_type': 'skill_executed',
            'content': f'生成了一张高对比度测试图片，文件路径为 {image_path}',
            'importance': 0.7
        }]
    }