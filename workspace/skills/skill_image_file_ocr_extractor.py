"""
自动生成的技能模块
需求: 使用提供的文件路径执行OCR的技能
生成时间: 2026-03-21 13:26:25
"""

# skill_name: image_file_ocr_extractor
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, Any, List, Optional

def main(args=None) -> Dict[str, Any]:
    """
    使用OCR技术从图像文件中提取文本内容
    
    参数:
        args: 包含以下键的字典
            - image_path: 图像文件路径
            - language: 识别语言 (可选，默认为 'chi_sim+eng')
            - preprocess: 是否预处理图像 (可选，默认为 True)
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path')
    if not image_path:
        return {'result': {'error': '缺少image_path参数'}, 'insights': ['OCR需要提供图像文件路径']}
    
    if not os.path.exists(image_path):
        return {'result': {'error': f'图像文件不存在: {image_path}'}, 'insights': ['指定的图像文件路径无效']}
    
    # 检查图像文件类型
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in valid_extensions:
        return {'result': {'error': f'不支持的图像格式: {file_ext}'}, 'insights': [f'支持的格式: {valid_extensions}']}
    
    language = args.get('language', 'chi_sim+eng')
    preprocess = args.get('preprocess', True)
    
    try:
        # 读取图像
        image = cv2.imread(image_path)
        if image is None:
            return {'result': {'error': '无法读取图像文件'}, 'insights': ['图像文件可能已损坏或格式不支持']}
        
        # 图像预处理
        processed_image = image
        if preprocess:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 阈值处理
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 去噪
            denoised = cv2.medianBlur(thresh, 3)
            
            # 调整图像大小
            height, width = denoised.shape
            if width < 100 or height < 100:
                # 放大图像以提高OCR识别率
                scale_factor = max(100 / width, 100 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                denoised = cv2.resize(denoised, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            processed_image = denoised
        
        # 使用pytesseract进行OCR识别
        # 设置OCR配置参数
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:,.<>?/~` '
        
        # 执行OCR识别
        text = pytesseract.image_to_string(processed_image, lang=language, config=custom_config)
        
        # 获取详细识别信息
        data = pytesseract.image_to_data(processed_image, lang=language, output_type=pytesseract.Output.DICT)
        
        # 过滤有效文本
        extracted_texts = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 30:  # 置信度大于30的文本
                text_item = {
                    'text': data['text'][i],
                    'confidence': data['conf'][i],
                    'bbox': {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                }
                if text_item['text'].strip():
                    extracted_texts.append(text_item)
        
        # 纯文本结果
        clean_text = text.strip()
        
        result = {
            'original_path': image_path,
            'extracted_text': clean_text,
            'detailed_results': extracted_texts,
            'total_characters': len(clean_text),
            'text_lines': len([line for line in clean_text.split('\n') if line.strip() > 0])
        }
        
        insights = [f'成功从图像中提取出 {len(extracted_texts)} 个文本元素', 
                   f'提取文本总字符数: {len(clean_text)}',
                   f'文本行数: {result["text_lines"]}']
        
        return {'result': result, 'insights': insights, 'facts': []}
        
    except Exception as e:
        error_msg = f'OCR处理失败: {str(e)}'
        return {'result': {'error': error_msg}, 'insights': ['OCR处理过程中出现异常']}