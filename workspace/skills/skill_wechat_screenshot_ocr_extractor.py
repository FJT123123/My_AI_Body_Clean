"""
自动生成的技能模块
需求: 正确处理run_skill输入格式的OCR技能，从微信截图中提取文本
生成时间: 2026-03-21 13:34:31
"""

# skill_name: wechat_screenshot_ocr_extractor
import os
import base64
import subprocess
import json
from typing import Dict, Any, List

def main(args=None):
    """
    从微信截图中提取文本内容
    支持传入图片路径或base64编码的图片数据，使用OCR技术识别并提取其中的文本内容
    """
    if args is None:
        args = {}
    
    # 获取图片数据
    image_path = args.get('image_path')
    image_base64 = args.get('image_base64')
    
    # 验证输入参数
    if not image_path and not image_base64:
        return {
            'result': {'error': '缺少必要参数，需要提供 image_path 或 image_base64'},
            'insights': ['输入参数验证失败，需要提供图片路径或base64编码'],
            'facts': [('ocr_input', 'required', 'image_path or image_base64')]
        }
    
    # 如果提供了base64编码的图片，先保存为临时文件
    temp_image_path = None
    if image_base64:
        try:
            # 解码base64数据
            image_data = base64.b64decode(image_base64)
            # 生成临时文件
            temp_image_path = '/tmp/temp_wechat_screenshot.png'
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)
            image_path = temp_image_path
        except Exception as e:
            return {
                'result': {'error': f'base64解码失败: {str(e)}'},
                'insights': ['图片base64解码失败'],
                'facts': [('image_processing', 'status', 'decode_failed')]
            }
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        return {
            'result': {'error': f'图片文件不存在: {image_path}'},
            'insights': ['指定的图片文件不存在'],
            'facts': [('image_path', 'validation', 'file_not_found')]
        }
    
    # 检查是否安装了tesseract
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        ocr_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 尝试安装tesseract
        try:
            if os.system('which apt-get > /dev/null 2>&1') == 0:
                # Ubuntu/Debian系统
                os.system('sudo apt-get update && sudo apt-get install -y tesseract-ocr')
            elif os.system('which brew > /dev/null 2>&1') == 0:
                # macOS系统
                os.system('brew install tesseract')
            else:
                return {
                    'result': {'error': '无法安装tesseract，系统不支持的包管理器'},
                    'insights': ['OCR引擎tesseract不可用，且无法自动安装'],
                    'facts': [('ocr_engine', 'status', 'not_available')]
                }
            # 再次检查是否安装成功
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, check=True)
            ocr_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                'result': {'error': 'OCR引擎tesseract不可用'},
                'insights': ['OCR引擎不可用，无法进行文本识别'],
                'facts': [('ocr_engine', 'status', 'not_available')]
            }
    
    # 创建临时输出文件
    temp_output_path = '/tmp/ocr_output'
    
    try:
        # 执行OCR识别
        result = subprocess.run([
            'tesseract', 
            image_path, 
            temp_output_path, 
            '-l', 'chi_sim+eng'  # 支持中文和英文
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'result': {'error': f'OCR识别失败: {result.stderr}'},
                'insights': ['OCR识别过程出现错误'],
                'facts': [('ocr_process', 'status', 'failed')]
            }
        
        # 读取识别结果
        output_txt_path = temp_output_path + '.txt'
        if os.path.exists(output_txt_path):
            with open(output_txt_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read().strip()
        else:
            extracted_text = ""
        
        # 清理临时文件
        if os.path.exists(output_txt_path):
            os.remove(output_txt_path)
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        # 处理识别结果
        if not extracted_text:
            result_data = {'text': '', 'success': False, 'message': '未识别到任何文本内容'}
        else:
            # 清理文本（去除多余的空白字符）
            cleaned_text = '\n'.join([line.strip() for line in extracted_text.split('\n') if line.strip()])
            result_data = {
                'text': cleaned_text,
                'success': True,
                'original_text': extracted_text
            }
        
        return {
            'result': result_data,
            'insights': [f'成功从微信截图中提取出文本内容，识别文本长度: {len(extracted_text)}' if extracted_text else '未识别到任何文本内容'],
            'facts': [('wechat_screenshot', 'text_extraction', 'completed' if extracted_text else 'no_text_found')],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f'OCR技能执行成功，提取了微信截图中的文本内容',
                    'tags': ['ocr', 'wechat', 'text_extraction']
                }
            ]
        }
        
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_output_path + '.txt'):
            os.remove(temp_output_path + '.txt')
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return {
            'result': {'error': f'OCR处理过程中出现异常: {str(e)}'},
            'insights': ['OCR处理过程中出现异常'],
            'facts': [('ocr_process', 'status', 'exception_occurred')]
        }