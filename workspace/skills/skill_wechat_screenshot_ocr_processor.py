"""
自动生成的技能模块
需求: 处理最新的微信截图并提取OCR文本的技能，自动查找最新截图文件
生成时间: 2026-03-21 13:29:39
"""

# skill_name: wechat_screenshot_ocr_processor
import os
import glob
import subprocess
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

def main(args=None):
    """
    自动查找最新的微信截图文件并提取OCR文本
    
    参数:
    - image_path: 可选，指定图片路径
    - wechat_screenshot_dir: 可选，微信截图目录，默认为用户图片文件夹
    """
    if args is None:
        args = {}
    
    # 获取参数
    image_path = args.get('image_path', None)
    wechat_screenshot_dir = args.get('wechat_screenshot_dir', None)
    
    # 如果没有指定图片路径，自动查找最新的微信截图
    if not image_path:
        if not wechat_screenshot_dir:
            # 尝试查找常见的微信截图位置
            user_home = os.path.expanduser("~")
            possible_paths = [
                os.path.join(user_home, "Pictures", "WeChat"),
                os.path.join(user_home, "Documents", "WeChat Files"),
                os.path.join(user_home, "Pictures"),
                os.path.join(user_home, "Downloads")
            ]
            
            # 查找可能的截图文件
            screenshot_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    # 查找包含截图关键词的图片文件
                    patterns = [
                        os.path.join(path, "*screen*.*"),
                        os.path.join(path, "*截圖*.*"),
                        os.path.join(path, "*截图*.*"),
                        os.path.join(path, "*WeChat*.*"),
                        os.path.join(path, "*微信*.*")
                    ]
                    
                    for pattern in patterns:
                        files = glob.glob(pattern)
                        if files:
                            # 找到最新的文件
                            latest_file = max(files, key=os.path.getctime)
                            if latest_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                                screenshot_path = latest_file
                                break
                if screenshot_path:
                    break
        
        if screenshot_path:
            image_path = screenshot_path
        else:
            # 如果没找到特定截图，查找最近的图片文件
            image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff']
            all_images = []
            for path in possible_paths:
                if os.path.exists(path):
                    for ext in image_extensions:
                        files = glob.glob(os.path.join(path, ext))
                        all_images.extend(files)
            
            if all_images:
                image_path = max(all_images, key=os.path.getctime)
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '未找到有效的截图文件'},
            'insights': ['无法找到微信截图文件，请检查截图目录或手动指定图片路径'],
            'ocr_text': '',
            'image_path': None
        }
    
    # 检查是否已安装tesseract
    try:
        subprocess.run(['tesseract', '--version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'result': {'error': 'tesseract OCR未安装'},
            'insights': ['需要安装tesseract-ocr才能执行OCR操作'],
            'ocr_text': '',
            'image_path': image_path
        }
    
    # 使用tesseract进行OCR识别
    try:
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            return {
                'result': {'error': '无法读取图像文件'},
                'insights': [f'图像文件可能损坏或不支持: {image_path}'],
                'ocr_text': '',
                'image_path': image_path
            }
        
        # 使用PIL处理图像以确保格式正确
        pil_img = Image.open(image_path)
        
        # 预处理图像以提高OCR准确性
        # 转为灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 保存预处理后的图像用于OCR
        temp_path = image_path + "_temp_ocr.png"
        cv2.imwrite(temp_path, thresh)
        
        # 使用tesseract进行OCR
        ocr_text = pytesseract.image_to_string(Image.open(temp_path), lang='chi_sim+eng')
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 清理OCR文本，移除多余的空行
        ocr_text = re.sub(r'\n\s*\n', '\n', ocr_text).strip()
        
        return {
            'result': {'success': True, 'ocr_text': ocr_text},
            'insights': [f'成功从截图 {os.path.basename(image_path)} 中提取了OCR文本'],
            'ocr_text': ocr_text,
            'image_path': image_path,
            'file_size': os.path.getsize(image_path),
            'file_created': datetime.fromtimestamp(os.path.getctime(image_path)).isoformat()
        }
        
    except Exception as e:
        return {
            'result': {'error': f'OCR处理失败: {str(e)}'},
            'insights': ['OCR处理过程中出现错误'],
            'ocr_text': '',
            'image_path': image_path
        }