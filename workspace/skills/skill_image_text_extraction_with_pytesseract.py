"""
自动生成的技能模块
需求: 从图像中提取文本内容：使用pytesseract进行OCR识别，提取图像中的文字信息
生成时间: 2026-03-12 15:46:21
"""

# skill_name: image_text_extraction_with_pytesseract
import base64
import json
import os
from io import BytesIO
from PIL import Image
import pytesseract

def main(args=None):
    """
    从图像中提取文本内容：使用pytesseract进行OCR识别，提取图像中的文字信息
    支持从图像文件路径、base64编码图像数据或PIL图像对象中提取文本
    """
    if args is None:
        args = {}
    
    # 获取图像数据
    image_data = args.get('image_data')
    image_path = args.get('image_path')
    image_base64 = args.get('image_base64')
    
    if not any([image_data, image_path, image_base64]):
        return {
            'result': {'error': '缺少图像数据，需要提供image_data、image_path或image_base64参数之一'},
            'insights': ['OCR识别需要图像数据作为输入']
        }
    
    # 准备图像对象
    image = None
    
    if image_path and os.path.exists(image_path):
        try:
            image = Image.open(image_path)
        except Exception as e:
            return {
                'result': {'error': f'无法打开图像文件: {str(e)}'},
                'insights': [f'图像文件读取失败: {str(e)}']
            }
    elif image_base64:
        try:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
        except Exception as e:
            return {
                'result': {'error': f'无法解码base64图像数据: {str(e)}'},
                'insights': [f'base64图像数据解码失败: {str(e)}']
            }
    elif image_data:
        try:
            if isinstance(image_data, str) and os.path.exists(image_data):
                image = Image.open(image_data)
            elif isinstance(image_data, Image.Image):
                image = image_data
            elif isinstance(image_data, bytes):
                image = Image.open(BytesIO(image_data))
            else:
                return {
                    'result': {'error': '不支持的图像数据格式'},
                    'insights': ['图像数据格式不正确']
                }
        except Exception as e:
            return {
                'result': {'error': f'无法处理图像数据: {str(e)}'},
                'insights': [f'图像数据处理失败: {str(e)}']
            }
    
    if image is None:
        return {
            'result': {'error': '无法获取有效图像对象'},
            'insights': ['图像处理过程中出现错误']
        }
    
    try:
        # 执行OCR识别
        extracted_text = pytesseract.image_to_string(image)
        
        # 清理文本：移除多余的空白字符
        extracted_text = extracted_text.strip()
        
        # 获取详细的OCR数据（包括文本位置等信息）
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # 过滤掉空的文本行
        filtered_data = {
            k: [v[i] for i in range(len(v)) if v[i] is not None and str(v[i]).strip() != '']
            for k, v in ocr_data.items()
        }
        
        result = {
            'extracted_text': extracted_text,
            'raw_ocr_data': ocr_data,
            'filtered_ocr_data': filtered_data,
            'text_length': len(extracted_text),
            'detected_languages': pytesseract.get_languages(config='')
        }
        
        insights = [
            f'OCR识别完成，提取到文本长度: {len(extracted_text)} 字符',
            f'检测到的语言: {", ".join(result["detected_languages"])}'
        ]
        
        # 如果提取到文本，将其作为记忆记录
        memories = []
        if extracted_text.strip():
            memories.append({
                'event_type': 'learning',
                'content': json.dumps({
                    'task': 'OCR text extraction',
                    'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text,
                    'image_info': {
                        'width': image.width,
                        'height': image.height,
                        'mode': image.mode
                    }
                }),
                'importance': 0.6,
                'tags': 'ocr,text_extraction,image'
            })
        
        return {
            'result': result,
            'insights': insights,
            'memories': memories if memories else None
        }
        
    except Exception as e:
        return {
            'result': {'error': f'OCR识别过程中发生错误: {str(e)}'},
            'insights': [f'OCR识别失败: {str(e)}']
        }