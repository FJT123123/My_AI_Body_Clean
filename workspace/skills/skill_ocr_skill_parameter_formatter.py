"""
自动生成的技能模块
需求: 使用正确的参数格式调用OCR技能的技能
生成时间: 2026-03-21 13:24:56
"""

# skill_name: ocr_skill_parameter_formatter

def main(args=None):
    """
    正确格式化OCR技能参数调用器
    根据传入的图像数据和配置参数，生成正确的参数格式来调用OCR技能
    支持图像路径、base64编码、字节流等多种输入格式
    """
    if args is None:
        args = {}
    
    # 获取输入参数
    image_input = args.get('image_input')
    image_format = args.get('image_format', 'auto')  # 'path', 'base64', 'bytes', 'auto'
    ocr_engine = args.get('ocr_engine', 'default')  # 可指定特定OCR引擎
    config_params = args.get('config_params', {})
    
    # 构建参数格式
    formatted_params = {
        'image_input': image_input,
        'image_format': image_format,
        'ocr_engine': ocr_engine,
        'config_params': config_params
    }
    
    # 根据不同输入格式进行参数验证
    if image_format == 'path' or (image_format == 'auto' and isinstance(image_input, str) and not image_input.startswith('data:image')):
        # 验证图像路径
        if isinstance(image_input, str):
            import os
            if not os.path.exists(image_input):
                return {
                    'result': {'error': '图像路径不存在', 'formatted_params': formatted_params},
                    'insights': ['输入的图像路径不存在，无法进行OCR处理'],
                    'next_skills': []
                }
        else:
            return {
                'result': {'error': '图像路径格式错误', 'formatted_params': formatted_params},
                'insights': ['图像路径应为字符串格式'],
                'next_skills': []
            }
    
    elif image_format == 'base64' or (image_format == 'auto' and isinstance(image_input, str) and image_input.startswith('data:image')):
        # 验证base64格式
        if isinstance(image_input, str):
            # 简单验证base64格式
            if not image_input.startswith('data:image'):
                return {
                    'result': {'error': 'Base64图像格式不正确', 'formatted_params': formatted_params},
                    'insights': ['Base64图像数据应以"data:image"开头'],
                    'next_skills': []
                }
        else:
            return {
                'result': {'error': 'Base64图像格式错误', 'formatted_params': formatted_params},
                'insights': ['Base64图像应为字符串格式'],
                'next_skills': []
            }
    
    elif image_format == 'bytes' or (image_format == 'auto' and isinstance(image_input, bytes)):
        # 验证字节流格式
        if not isinstance(image_input, bytes):
            return {
                'result': {'error': '字节流图像格式错误', 'formatted_params': formatted_params},
                'insights': ['字节流图像应为bytes类型'],
                'next_skills': []
            }
    
    # 格式化成功，准备调用OCR技能
    result = {
        'formatted_params': formatted_params,
        'status': 'success',
        'message': '参数格式化成功，可调用相应OCR技能'
    }
    
    # 建议后续技能
    next_skills = []
    if ocr_engine == 'default':
        # 使用默认OCR技能
        next_skills.append({
            'skill_name': 'skill_image_ocr_text_extraction',
            'args': {'image_path': image_input if image_format == 'path' else None,
                    'image_base64': image_input if image_format in ['base64', 'auto'] and isinstance(image_input, str) else None}
        })
    else:
        # 根据指定引擎选择技能
        next_skills.append({
            'skill_name': f'skill_{ocr_engine}_ocr',
            'args': formatted_params
        })
    
    return {
        'result': result,
        'insights': ['已成功格式化OCR参数，可根据不同输入格式正确调用OCR技能'],
        'facts': [
            ['OCR参数格式化', '处理', image_format],
            ['OCR参数格式化', '使用引擎', ocr_engine]
        ],
        'next_skills': next_skills
    }