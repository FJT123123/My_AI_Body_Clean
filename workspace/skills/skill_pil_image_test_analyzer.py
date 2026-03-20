"""
自动生成的技能模块
需求: 创建一个简单的PIL测试技能，尝试打开test_image.png并返回基本信息
生成时间: 2026-03-12 16:24:09
"""

# skill_name: pil_image_test_analyzer
def main(args=None):
    """
    创建一个简单的PIL测试技能，尝试打开test_image.png并返回基本信息
    该技能用于测试PIL库是否正常工作以及检查图像文件基本属性
    """
    import os
    from PIL import Image
    
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    test_image_path = context.get('test_image_path', 'test_image.png')
    
    # 检查图像文件是否存在
    if not os.path.exists(test_image_path):
        return {
            'result': {'error': f'图像文件 {test_image_path} 不存在'},
            'insights': [f'无法找到测试图像文件: {test_image_path}']
        }
    
    try:
        # 尝试打开图像
        with Image.open(test_image_path) as img:
            # 获取图像基本信息
            image_info = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height
            }
            
            # 尝试获取额外信息
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                if exif:
                    image_info['exif'] = str(exif)[:200] + '...' if len(str(exif)) > 200 else str(exif)
            
            return {
                'result': image_info,
                'insights': [f'成功读取图像文件: {test_image_path}', f'图像格式: {img.format}', f'图像尺寸: {img.size}'],
                'memories': [{
                    'event_type': 'skill_executed',
                    'content': f'PIL图像测试成功，文件: {test_image_path}, 尺寸: {img.size}',
                    'importance': 0.5
                }]
            }
    
    except Exception as e:
        return {
            'result': {'error': f'打开图像时发生错误: {str(e)}'},
            'insights': [f'PIL图像处理失败: {str(e)}']
        }