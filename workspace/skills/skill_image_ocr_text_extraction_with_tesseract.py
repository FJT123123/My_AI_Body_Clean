"""
自动生成的技能模块
需求: 使用tesseract命令行工具进行OCR识别，从图像中提取文本内容
生成时间: 2026-03-19 21:25:35
"""

# skill_name: image_ocr_text_extraction_with_tesseract

import subprocess
import os
import json
from typing import Dict, Any, Optional

def main(args=None) -> Dict[str, Any]:
    """
    使用tesseract命令行工具进行OCR识别，从图像中提取文本内容
    
    参数:
    - args: 包含以下键的字典
        - image_path: 图像文件路径
        - lang: 语言代码（可选，默认为'eng'）
        - output_format: 输出格式（可选，默认为'txt'）
        - tesseract_path: tesseract命令路径（可选，默认为'tesseract'）
    """
    import json
    
    # 处理实际的参数结构
    actual_input = args
    if isinstance(args, dict) and 'input' in args:
        # 从包装结构中提取实际输入
        try:
            actual_input = json.loads(args['input'])
        except:
            actual_input = args['input'] if isinstance(args['input'], dict) else {}
    
    if actual_input is None:
        actual_input = {}
    
    image_path = actual_input.get('image_path')
    lang = args.get('lang', 'eng')
    output_format = args.get('output_format', 'txt')
    tesseract_path = args.get('tesseract_path', 'tesseract')
    
    if not image_path:
        return {
            'result': {'error': '缺少image_path参数'},
            'insights': ['需要提供图像文件路径'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    # 检查图像文件是否存在
    if not os.path.exists(image_path):
        return {
            'result': {'error': f'图像文件不存在: {image_path}'},
            'insights': [f'图像文件 {image_path} 不存在'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    # 检查tesseract是否可用
    try:
        result = subprocess.run([tesseract_path, '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return {
                'result': {'error': f'tesseract命令不可用: {tesseract_path}'},
                'insights': [f'tesseract命令 {tesseract_path} 无法执行'],
                'facts': [],
                'memories': [],
                'capabilities': [],
                'next_skills': ['skill_system_dependency_installer']
            }
    except FileNotFoundError:
        return {
            'result': {'error': 'tesseract未安装'},
            'insights': ['系统未安装tesseract OCR工具'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': ['skill_system_dependency_installer']
        }
    
    # 执行OCR识别
    try:
        output_file = os.path.splitext(image_path)[0]
        cmd = [tesseract_path, image_path, output_file, '-l', lang, '--oem', '3', '--psm', '6']
        
        if output_format != 'txt':
            cmd.extend([output_format])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'result': {'error': f'OCR识别失败: {result.stderr}'},
                'insights': [f'OCR识别图像 {image_path} 失败'],
                'facts': [],
                'memories': [],
                'capabilities': [],
                'next_skills': []
            }
        
        # 读取识别结果
        output_file_path = f"{output_file}.txt"
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
            
            # 清理临时文件
            os.remove(output_file_path)
            
            return {
                'result': {
                    'extracted_text': extracted_text,
                    'image_path': image_path,
                    'language': lang,
                    'command': ' '.join(cmd)
                },
                'insights': [f'从图像 {image_path} 成功提取文本，共 {len(extracted_text)} 个字符'],
                'facts': [
                    ['图像文件', '包含文本', extracted_text[:50] + '...' if len(extracted_text) > 50 else extracted_text],
                    ['OCR工具', '识别语言', lang]
                ],
                'memories': [
                    f'OCR识别完成: 从 {image_path} 提取了文本内容'
                ],
                'capabilities': ['图像文本识别', 'OCR处理'],
                'next_skills': ['skill_text_analyzer', 'skill_document_processor']
            }
        else:
            # 如果输出文件不存在，尝试直接从标准输出获取结果
            extracted_text = result.stdout.strip()
            return {
                'result': {
                    'extracted_text': extracted_text,
                    'image_path': image_path,
                    'language': lang,
                    'command': ' '.join(cmd)
                },
                'insights': [f'从图像 {image_path} 成功提取文本，共 {len(extracted_text)} 个字符'],
                'facts': [
                    ['图像文件', '包含文本', extracted_text[:50] + '...' if len(extracted_text) > 50 else extracted_text],
                    ['OCR工具', '识别语言', lang]
                ],
                'memories': [
                    f'OCR识别完成: 从 {image_path} 提取了文本内容'
                ],
                'capabilities': ['图像文本识别', 'OCR处理'],
                'next_skills': ['skill_text_analyzer', 'skill_document_processor']
            }
    
    except Exception as e:
        return {
            'result': {'error': f'OCR识别过程中发生错误: {str(e)}'},
            'insights': [f'OCR识别图像 {image_path} 时发生异常'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }