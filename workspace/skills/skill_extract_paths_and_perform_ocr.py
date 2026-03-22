"""
自动生成的技能模块
需求: 从复杂的输入结构中提取文件路径并执行OCR的技能
生成时间: 2026-03-21 13:33:29
"""

# skill_name: extract_paths_and_perform_ocr

import os
import json
import re
from pathlib import Path
import base64
from typing import List, Dict, Any, Union

def extract_image_paths(input_data: Any) -> List[str]:
    """
    从复杂输入结构中提取所有可能的图像文件路径
    """
    paths = []
    
    def extract_from_obj(obj):
        if isinstance(obj, str):
            # 检查是否是文件路径
            if os.path.exists(obj) and is_image_file(obj):
                paths.append(obj)
            # 检查字符串中是否包含路径
            elif is_valid_path_format(obj):
                expanded_path = os.path.expanduser(obj)
                if os.path.exists(expanded_path) and is_image_file(expanded_path):
                    paths.append(expanded_path)
        elif isinstance(obj, list):
            for item in obj:
                extract_from_obj(item)
        elif isinstance(obj, dict):
            for value in obj.values():
                extract_from_obj(value)
        elif hasattr(obj, '__dict__'):
            for value in obj.__dict__.values():
                extract_from_obj(value)
    
    extract_from_obj(input_data)
    return list(set(paths))  # 去重

def is_image_file(file_path: str) -> bool:
    """
    检查文件是否为图像文件
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    return Path(file_path).suffix.lower() in image_extensions

def is_valid_path_format(path_str: str) -> bool:
    """
    检查字符串是否为有效的路径格式
    """
    # 检查是否包含路径分隔符或常见路径模式
    if os.path.sep in path_str or path_str.startswith(('/', '~', './', '../')):
        return True
    # 检查是否包含常见路径关键词
    path_keywords = ['/', '\\', 'path', 'file', 'image', 'img', 'doc', 'home', 'data', 'temp', 'downloads']
    return any(keyword in path_str.lower() for keyword in path_keywords)

def perform_ocr_on_image(image_path: str) -> str:
    """
    对单个图像文件执行OCR
    """
    try:
        # 尝试导入tesseract OCR
        import pytesseract
        from PIL import Image
        
        # 打开图像并执行OCR
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except ImportError:
        # 如果没有安装tesseract，尝试使用其他方法
        return f"OCR processing failed for {image_path}: pytesseract not installed"
    except Exception as e:
        return f"OCR processing failed for {image_path}: {str(e)}"

def main(args=None):
    """
    从复杂输入结构中提取图像文件路径并执行OCR识别
    输入参数可能包含嵌套的字典、列表或其他复杂结构，需要从中提取图像路径并执行OCR
    """
    if args is None:
        args = {}
    
    input_data = args.get('input_data', args)
    
    # 提取图像路径
    image_paths = extract_image_paths(input_data)
    
    ocr_results = {}
    successful_ocr = 0
    failed_ocr = 0
    
    # 对每个图像文件执行OCR
    for path in image_paths:
        try:
            ocr_text = perform_ocr_on_image(path)
            ocr_results[path] = ocr_text
            if ocr_text and not ocr_text.startswith("OCR processing failed"):
                successful_ocr += 1
            else:
                failed_ocr += 1
        except Exception as e:
            ocr_results[path] = f"Error processing {path}: {str(e)}"
            failed_ocr += 1
    
    insights = []
    if successful_ocr > 0:
        insights.append(f"Successfully performed OCR on {successful_ocr} image files")
    if failed_ocr > 0:
        insights.append(f"OCR failed for {failed_ocr} image files")
    
    if not image_paths:
        insights.append("No image files found in the input data")
    
    result = {
        'extracted_paths': image_paths,
        'ocr_results': ocr_results,
        'summary': {
            'total_paths_found': len(image_paths),
            'successful_ocr': successful_ocr,
            'failed_ocr': failed_ocr
        }
    }
    
    return {
        'result': result,
        'insights': insights,
        'memories': [
            f"Processed {len(image_paths)} image paths with OCR, {successful_ocr} successful, {failed_ocr} failed"
        ]
    }