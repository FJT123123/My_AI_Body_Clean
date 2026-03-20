"""
自动生成的技能模块
需求: 生成一张带文字的测试图片，包含随机生成的文字内容，保存到workspace目录下。使用Pillow库创建一个简单的图像，添加文字"OpenClaw Vision Test - 图片能力扩展测试"，并保存为test_image.png。
生成时间: 2026-03-12 16:12:42
"""

# skill_name: vision_test_image_generator

from PIL import Image, ImageDraw, ImageFont
import os
import random
import string

def main(args=None):
    """
    生成一张带文字的测试图片，包含随机生成的文字内容，保存到workspace目录下。
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
    
    # 创建随机文字
    def generate_random_text():
        letters = string.ascii_letters + string.digits + " "
        return ''.join(random.choice(letters) for i in range(20))
    
    # 添加主标题文字
    try:
        # 尝试使用系统字体，如果不可用则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # 主标题
        main_text = "OpenClaw Vision Test - 图片能力扩展测试"
        text_width, text_height = draw.textsize(main_text, font=font)
        text_x = (width - text_width) // 2
        text_y = height // 3
        draw.text((text_x, text_y), main_text, fill=(0, 0, 0), font=font)
        
        # 随机文字
        random_text = generate_random_text()
        random_text_width, random_text_height = draw.textsize(random_text, font=font)
        random_text_x = (width - random_text_width) // 2
        random_text_y = height // 2
        draw.text((random_text_x, random_text_y), random_text, fill=(0, 0, 0), font=font)
        
    except Exception as e:
        # 如果字体加载失败，使用默认方法
        main_text = "OpenClaw Vision Test - 图片能力扩展测试"
        draw.text((150, 200), main_text, fill=(0, 0, 0))
        
        random_text = generate_random_text()
        draw.text((200, 300), random_text, fill=(0, 0, 0))
    
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