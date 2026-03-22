"""
自动生成的技能模块
需求: 直接检查文件是否存在并执行OCR的技能，使用硬编码路径
生成时间: 2026-03-21 13:25:48
"""

# skill_name: file_ocr_scanner
import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
import json

def main(args=None):
    """
    检查指定硬编码路径的文件是否存在，并对图像文件执行OCR识别
    该技能直接处理本地文件系统中的图像，提取其中的文本内容
    """
    # 硬编码检查路径
    image_paths = [
        "/tmp/screenshot.png",
        "/tmp/ocr_image.jpg",
        "/tmp/scan_document.png",
        "/tmp/uploaded_image.png"
    ]
    
    results = []
    ocr_results = []
    
    for image_path in image_paths:
        if os.path.exists(image_path):
            # 检查文件类型
            file_extension = os.path.splitext(image_path)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
                try:
                    # 使用OpenCV读取图像
                    img = cv2.imread(image_path)
                    if img is not None:
                        # 使用PIL进行图像预处理
                        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                        
                        # 执行OCR识别
                        text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')
                        text = text.strip()
                        
                        ocr_result = {
                            'image_path': image_path,
                            'ocr_text': text,
                            'text_length': len(text),
                            'status': 'success'
                        }
                        ocr_results.append(ocr_result)
                        
                        results.append({
                            'path': image_path,
                            'exists': True,
                            'type': 'image',
                            'ocr_text': text
                        })
                    else:
                        results.append({
                            'path': image_path,
                            'exists': True,
                            'type': 'image',
                            'error': 'Failed to read image'
                        })
                except Exception as e:
                    results.append({
                        'path': image_path,
                        'exists': True,
                        'type': 'image',
                        'error': str(e)
                    })
            else:
                results.append({
                    'path': image_path,
                    'exists': True,
                    'type': 'non_image'
                })
        else:
            results.append({
                'path': image_path,
                'exists': False
            })
    
    # 检查是否安装了tesseract
    try:
        import pytesseract
        tesseract_version = pytesseract.get_tesseract_version()
        tesseract_available = True
    except:
        tesseract_available = False
        tesseract_version = "Not available"
    
    return {
        'result': {
            'file_checks': results,
            'ocr_results': ocr_results,
            'tesseract_available': tesseract_available,
            'tesseract_version': str(tesseract_version)
        },
        'insights': [
            f'检查了 {len(image_paths)} 个硬编码路径',
            f'找到 {len([r for r in results if r["exists"]])} 个存在的文件',
            f'执行了 {len(ocr_results)} 次OCR识别'
        ],
        'facts': [
            ['tesseract_ocr', 'available', str(tesseract_available)],
            ['checked_files_count', 'total', str(len(image_paths))]
        ]
    }