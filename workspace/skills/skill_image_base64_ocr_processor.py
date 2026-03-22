"""
自动生成的技能模块
需求: 直接读取截图文件并使用base64编码传递给OCR的技能
生成时间: 2026-03-21 13:28:46
"""

# skill_name: image_base64_ocr_processor

import base64
import io
import os
from PIL import Image
import pytesseract
from typing import Dict, Optional, Any


def main(args=None) -> Dict[str, Any]:
    """
    直接读取截图文件并使用base64编码传递给OCR的技能
    
    参数:
        args: 包含 'image_base64' 键的字典，值为base64编码的图像数据
    
    返回:
        包含OCR识别结果的字典
    """
    if args is None:
        args = {}
    
    # 获取base64编码的图像数据
    image_base64 = args.get('image_base64')
    if not image_base64:
        return {
            'result': {'error': '缺少image_base64参数'},
            'insights': ['输入参数验证失败'],
            'facts': [('ocr_processor', 'requires', 'image_base64_input')]
        }
    
    try:
        # 解码base64图像数据
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # 执行OCR识别
        ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # 清理OCR结果
        ocr_text = ocr_text.strip()
        
        # 构建结果
        result = {
            'success': True,
            'text': ocr_text,
            'image_size': image.size,
            'image_mode': image.mode
        }
        
        insights = [
            f'成功识别图像，尺寸: {image.size}',
            f'OCR识别出 {len(ocr_text)} 个字符'
        ]
        
        # 如果识别出文本内容，添加相关信息
        if ocr_text:
            insights.append('OCR识别出有效文本内容')
        else:
            insights.append('OCR未识别出文本内容')
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                ('image_ocr', 'has_size', str(image.size)),
                ('image_ocr', 'has_mode', image.mode),
                ('ocr_result', 'contains_text', 'true' if ocr_text else 'false')
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': f'OCR处理失败: {str(e)}'},
            'insights': [f'OCR处理过程中发生异常: {str(e)}'],
            'facts': [
                ('image_ocr', 'processing_status', 'failed'),
                ('image_ocr', 'error_message', str(e))
            ]
        }