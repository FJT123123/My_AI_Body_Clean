"""
自动生成的技能模块
需求: 正确处理run_skill输入格式的OCR技能，从input字段提取JSON并执行OCR
生成时间: 2026-03-21 13:35:09
"""

# skill_name: ocr_from_run_skill_input
import base64
import json
import os
from PIL import Image
from io import BytesIO
import pytesseract

def main(args=None):
    """
    从run_skill输入格式中提取OCR内容，处理输入字段中的JSON数据并执行OCR识别
    支持image_base64、image_path等多种输入格式
    """
    if args is None:
        args = {}
    
    # 提取输入数据
    input_data = args.get('input', {})
    
    # 如果input是字符串，尝试解析为JSON
    if isinstance(input_data, str):
        try:
            input_data = json.loads(input_data)
        except json.JSONDecodeError:
            return {
                'result': {'error': 'input不是有效的JSON格式'},
                'insights': ['输入格式错误，无法解析JSON'],
                'ocr_result': None
            }
    
    # 检查是否包含image_base64字段
    if 'image_base64' in input_data:
        image_base64 = input_data['image_base64']
        try:
            # 解码base64图像
            image_data = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_data))
            
            # 执行OCR
            ocr_result = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            return {
                'result': {'ocr_text': ocr_result.strip()},
                'insights': ['OCR识别完成'],
                'ocr_result': ocr_result.strip()
            }
        except Exception as e:
            return {
                'result': {'error': f'处理image_base64时出错: {str(e)}'},
                'insights': [f'图像处理失败: {str(e)}'],
                'ocr_result': None
            }
    
    # 检查是否包含image_path字段
    elif 'image_path' in input_data:
        image_path = input_data['image_path']
        if not os.path.exists(image_path):
            return {
                'result': {'error': f'图像文件不存在: {image_path}'},
                'insights': ['指定的图像路径不存在'],
                'ocr_result': None
            }
        
        try:
            # 使用pytesseract执行OCR
            image = Image.open(image_path)
            ocr_result = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            return {
                'result': {'ocr_text': ocr_result.strip()},
                'insights': ['OCR识别完成'],
                'ocr_result': ocr_result.strip()
            }
        except Exception as e:
            return {
                'result': {'error': f'处理image_path时出错: {str(e)}'},
                'insights': [f'图像处理失败: {str(e)}'],
                'ocr_result': None
            }
    
    # 检查是否包含raw_image字段（直接的PIL Image对象）
    elif 'raw_image' in input_data:
        image = input_data['raw_image']
        try:
            ocr_result = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            return {
                'result': {'ocr_text': ocr_result.strip()},
                'insights': ['OCR识别完成'],
                'ocr_result': ocr_result.strip()
            }
        except Exception as e:
            return {
                'result': {'error': f'处理raw_image时出错: {str(e)}'},
                'insights': [f'图像处理失败: {str(e)}'],
                'ocr_result': None
            }
    
    else:
        return {
            'result': {'error': '输入中未找到支持的图像字段(image_base64, image_path, raw_image)'},
            'insights': ['输入格式不支持，缺少必要的图像字段'],
            'ocr_result': None
        }