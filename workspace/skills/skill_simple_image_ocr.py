"""
自动生成的技能模块
需求: 直接执行OCR操作的简单技能，只接受图像路径作为字符串参数
生成时间: 2026-03-21 13:13:40
"""

# skill_name: simple_image_ocr
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract

def main(args=None):
    """
    执行图像OCR识别，提取文本内容
    参数: image_path - 图像文件路径
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '图像文件路径不存在'},
            'insights': ['OCR操作失败：图像文件不存在'],
            'next_skills': []
        }
    
    # 检查tesseract是否可用
    try:
        pytesseract.get_tesseract_cmd()
    except:
        return {
            'result': {'error': 'tesseract OCR未安装或不可用'},
            'insights': ['OCR操作失败：tesseract未安装'],
            'next_skills': ['skill_system_dependency_install']
        }
    
    try:
        # 使用PIL读取图像
        image = Image.open(image_path)
        
        # 执行OCR识别
        text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # 获取详细信息
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # 过滤掉空行
        extracted_text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
        
        return {
            'result': {
                'text': extracted_text,
                'word_count': len(extracted_text.split()),
                'confidence': calculate_average_confidence(data)
            },
            'insights': [f'从图像中提取到{len(extracted_text.split())}个单词的文本'],
            'memories': [
                {
                    'type': 'ocr_result',
                    'image_path': image_path,
                    'text_length': len(extracted_text),
                    'word_count': len(extracted_text.split())
                }
            ]
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'OCR操作失败：{str(e)}'],
            'next_skills': []
        }

def calculate_average_confidence(data):
    """计算OCR识别的平均置信度"""
    confidences = [int(conf) for conf in data['conf'] if int(conf) != -1]
    if not confidences:
        return 0
    return sum(confidences) / len(confidences)