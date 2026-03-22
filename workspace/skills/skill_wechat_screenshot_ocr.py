"""
自动生成的技能模块
需求: 直接读取微信截图文件并执行OCR的技能，使用硬编码路径
生成时间: 2026-03-21 13:23:56
"""

# skill_name: wechat_screenshot_ocr
import os
import json
from PIL import Image
import pytesseract
import re

def main(args=None):
    """
    直接读取微信截图文件并执行OCR的技能，使用硬编码路径
    该技能会查找微信截图文件并执行文字识别，返回识别结果
    """
    # 检查OCR工具是否可用
    try:
        pytesseract.get_tesseract_version()
    except:
        return {
            'result': {'error': 'tesseract OCR未安装或不可用'},
            'insights': ['需要先安装tesseract OCR引擎'],
            'next_skills': ['skill_system_dependency_installer']
        }
    
    # 硬编码微信截图路径
    possible_paths = [
        os.path.expanduser("~/Pictures/WeChat\\ Files/"),  # Windows
        os.path.expanduser("~/Documents/WeChat\\ Files/"),  # Windows
        os.path.expanduser("~/Desktop/"),  # 通用桌面路径
        os.path.expanduser("~/Downloads/"),  # 通用下载路径
        os.path.expanduser("~/Documents/"),  # 通用文档路径
    ]
    
    # 尝试查找微信截图文件
    wechat_screenshot_files = []
    for path in possible_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if re.search(r"微信截图|WeChat.*截图|screenshot.*wechat|wechat.*screenshot", file, re.IGNORECASE) and \
                   file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    wechat_screenshot_files.append(os.path.join(path, file))
    
    # 如果没有找到微信截图，尝试查找最近的图片文件
    if not wechat_screenshot_files:
        for path in possible_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        # 检查文件名是否与微信相关
                        if 'wechat' in file.lower() or '微信' in file:
                            wechat_screenshot_files.append(os.path.join(path, file))
    
    # 如果仍然没有找到，尝试找最近的截图
    if not wechat_screenshot_files:
        for path in possible_paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        if 'screen' in file.lower() or '截图' in file:
                            wechat_screenshot_files.append(os.path.join(path, file))
    
    if not wechat_screenshot_files:
        return {
            'result': {'error': '未找到微信截图文件'},
            'insights': ['在常用路径中未找到微信截图文件'],
            'next_skills': ['skill_file_finder']
        }
    
    # 对找到的截图文件执行OCR
    ocr_results = []
    for img_path in wechat_screenshot_files:
        try:
            # 打开图片
            img = Image.open(img_path)
            
            # 执行OCR
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            
            # 清理文本
            text = text.strip()
            
            ocr_results.append({
                'image_path': img_path,
                'ocr_text': text,
                'text_length': len(text)
            })
            
        except Exception as e:
            ocr_results.append({
                'image_path': img_path,
                'error': str(e),
                'text_length': 0
            })
    
    # 提取所有识别到的文本
    all_text = ""
    for result in ocr_results:
        if 'ocr_text' in result:
            all_text += result['ocr_text'] + "\n"
    
    # 返回结果
    return {
        'result': {
            'ocr_results': ocr_results,
            'total_files_processed': len(ocr_results),
            'total_text_extracted': len(all_text)
        },
        'insights': [
            f'成功处理了 {len(ocr_results)} 个微信截图文件',
            f'总共提取了 {len(all_text)} 个字符'
        ],
        'memories': [
            f"OCR识别了微信截图，提取了 {len(ocr_results)} 个文件的文字内容"
        ]
    }