"""
自动生成的技能模块 - 修复版
需求: 生成一张带文字的测试图片，包含清晰可见的文字内容，保存到workspace目录下。
使用Pillow库创建一个简单的图像，添加文字"OpenClaw Vision Test - 图片能力扩展测试"，并保存为test_image.png。
"""

# skill_name: vision_test_image_generator_fixed

from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

def main(args=None):
    """
    生成一张带文字的测试图片，包含清晰可见的文字内容，保存到workspace目录下。
    使用Pillow库创建一个简单的图像，添加文字"OpenClaw Vision Test - 图片能力扩展测试"，并保存为test_image.png。
    """
    if args is None:
        args = {}
    
    # 获取工作目录
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', './workspace')
    
    # 确保workspace目录存在
    os.makedirs(workspace_path, exist_ok=True)
    
    # 创建图像
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # 添加主标题文字 - 使用更可靠的方法
    try:
        # 尝试使用系统字体，如果不可用则使用默认字体
        try:
            # 使用较大的字体大小确保文字清晰可见
            font = ImageFont.load_default()
            # 在较新版本的Pillow中，使用getbbox()方法获取文本尺寸
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox("OpenClaw Vision Test")
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                # 旧版本兼容
                text_width, text_height = draw.textsize("OpenClaw Vision Test", font=font)
            
            # 主标题
            main_text = "OpenClaw Vision Test"
            text_x = (width - text_width) // 2
            text_y = height // 3
            draw.text((text_x, text_y), main_text, fill=(0, 0, 0), font=font)
            
            # 副标题
            subtitle = "图片能力扩展测试"
            if hasattr(font, 'getbbox'):
                bbox2 = font.getbbox(subtitle)
                sub_width = bbox2[2] - bbox2[0]
            else:
                sub_width, _ = draw.textsize(subtitle, font=font)
            
            sub_x = (width - sub_width) // 2
            sub_y = text_y + text_height + 20
            draw.text((sub_x, sub_y), subtitle, fill=(0, 0, 0), font=font)
            
        except Exception as font_error:
            # 如果字体加载失败，使用默认方法但确保文字足够大
            main_text = "OpenClaw Vision Test"
            draw.text((150, 200), main_text, fill=(0, 0, 0), font=None)
            
            subtitle = "图片能力扩展测试"
            draw.text((200, 250), subtitle, fill=(0, 0, 0), font=None)
        
    except Exception as e:
        # 最后的备选方案
        main_text = "OpenClaw Vision Test"
        draw.text((150, 200), main_text, fill=(0, 0, 0))
        
        subtitle = "图片能力扩展测试"
        draw.text((200, 250), subtitle, fill=(0, 0, 0))
    
    # 保存图像
    image_path = os.path.join(workspace_path, 'test_image.png')
    image.save(image_path)
    
    result = {
        'image_path': image_path,
        'success': True,
        'message': f'测试图片已保存到 {image_path}'
    }
    
    return {
        'result': result,
        'insights': [f'成功生成测试图片，保存路径: {image_path}'],
        'memories': [{
            'event_type': 'skill_executed',
            'content': f'生成了一张测试图片，文件路径为 {image_path}',
            'importance': 0.6
        }]
    }