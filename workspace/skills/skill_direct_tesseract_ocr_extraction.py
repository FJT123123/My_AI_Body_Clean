"""
自动生成的技能模块
需求: 使用tesseract命令行工具直接提取OCR文本的技能
生成时间: 2026-03-21 13:28:23
"""

# skill_name: direct_tesseract_ocr_extraction
import subprocess
import os
import json
from pathlib import Path

def main(args=None):
    """
    使用tesseract命令行工具直接提取OCR文本的技能
    支持传入图像路径，通过tesseract命令行工具提取图像中的文本内容
    可以指定语言参数，默认使用简体中文
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    language = args.get('language', 'chi_sim')
    
    # 验证输入参数
    if not image_path:
        return {
            'result': {'error': '缺少image_path参数'},
            'insights': ['调用OCR技能需要提供图像路径'],
            'next_skills': []
        }
    
    # 检查图像文件是否存在
    if not os.path.exists(image_path):
        return {
            'result': {'error': f'图像文件不存在: {image_path}'},
            'insights': [f'OCR失败：图像文件不存在 - {image_path}'],
            'next_skills': []
        }
    
    # 检查tesseract是否已安装
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        tesseract_version = result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'result': {'error': 'tesseract未安装或未在PATH中'},
            'insights': ['系统中未找到tesseract命令，需要先安装tesseract-ocr'],
            'next_skills': ['skill_system_dependency_installer']
        }
    
    # 执行OCR提取
    try:
        result = subprocess.run(['tesseract', image_path, 'stdout', '-l', language], 
                              capture_output=True, text=True, check=True)
        extracted_text = result.stdout.strip()
        
        # 检查提取结果是否为空
        if not extracted_text:
            insights = ['OCR提取成功但未识别到文本内容']
        else:
            insights = [f'OCR提取成功，识别到{len(extracted_text)}字符的文本内容']
        
        return {
            'result': {
                'text': extracted_text,
                'image_path': image_path,
                'language': language,
                'tesseract_version': tesseract_version
            },
            'insights': insights,
            'memories': [{
                'event_type': 'skill_executed',
                'content': f'OCR提取完成，从图像{image_path}中提取了文本',
                'tags': ['ocr', 'text_extraction']
            }],
            'next_skills': []
        }
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': f'OCR提取失败: {e.stderr}'},
            'insights': [f'OCR执行失败: {e.stderr}'],
            'next_skills': []
        }
    except Exception as e:
        return {
            'result': {'error': f'OCR提取过程中发生错误: {str(e)}'},
            'insights': [f'OCR处理异常: {str(e)}'],
            'next_skills': []
        }