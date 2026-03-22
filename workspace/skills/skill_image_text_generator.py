"""
自动生成的技能模块
需求: 生成带自定义文字和文件名的测试图片。接受参数：output_filename（输出文件名）、text_content（文字内容）、image_size（图像尺寸，默认[800, 600]）。使用Pillow创建白色背景的图像，在中心位置添加黑色文字，并保存到workspace目录。
生成时间: 2026-03-21 11:46:32
"""

# skill_name: image_text_generator
import os
from PIL import Image, ImageDraw, ImageFont

def main(args=None):
    """
    生成带自定义文字和文件名的测试图片
    根据参数创建白色背景的图像，在中心位置添加黑色文字，并保存到workspace目录
    """
    if args is None:
        args = {}
    
    # 获取参数
    output_filename = args.get('output_filename', 'test_image.png')
    text_content = args.get('text_content', 'Default Text')
    image_size = args.get('image_size', [800, 600])
    
    # 确保图像尺寸为元组格式
    if isinstance(image_size, list):
        image_size = tuple(image_size)
    
    # 获取workspace目录路径
    workspace_dir = os.path.join(os.getcwd(), 'workspace')
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    
    # 创建完整路径
    output_path = os.path.join(workspace_dir, output_filename)
    
    # 创建白色背景图像
    img = Image.new('RGB', image_size, color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用默认字体
    try:
        # 在不同系统中查找可用字体
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]
        
        # 尝试使用系统默认字体
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, size=36)
                break
        
        # 如果找不到字体，则使用默认字体
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()
    
    # 获取文字尺寸
    bbox = draw.textbbox((0, 0), text_content, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 计算文字位置（居中）
    x = (image_size[0] - text_width) // 2
    y = (image_size[1] - text_height) // 2
    
    # 添加文字到图像
    draw.text((x, y), text_content, fill='black', font=font)
    
    # 保存图像
    img.save(output_path)
    
    # 检查文件是否成功创建
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        result = {
            'success': True,
            'output_path': output_path,
            'file_size': file_size,
            'image_size': image_size,
            'text_content': text_content
        }
    else:
        result = {
            'success': False,
            'error': 'Failed to create image file'
        }
    
    return {
        'result': result,
        'insights': [f'Generated test image with custom text: {text_content}'],
        'facts': [
            ['image_generator', 'creates', 'test_image'],
            ['test_image', 'has_text_content', text_content],
            ['test_image', 'saved_to', output_path]
        ],
        'memories': [
            {
                'event_type': 'skill_executed',
                'content': f'Generated test image: {output_filename} with text: {text_content}',
                'tags': ['image_generation', 'text_overlay']
            }
        ]
    }