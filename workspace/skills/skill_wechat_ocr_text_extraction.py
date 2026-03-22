"""
自动生成的技能模块
需求: 直接执行微信端到端验证并提取OCR文本的技能，使用正确的参数处理
生成时间: 2026-03-21 13:22:00
"""

# skill_name: wechat_ocr_text_extraction
import os
import base64
import json
from typing import Dict, Any, Optional

def main(args=None):
    """
    执行微信端到端验证并提取OCR文本
    支持从图片路径或base64编码的图片数据提取文本内容
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    image_base64 = args.get('image_base64', '')
    
    # 验证输入参数
    if not image_path and not image_base64:
        return {
            'result': {
                'error': '必须提供image_path或image_base64参数之一'
            },
            'insights': ['参数验证失败：缺少必要参数'],
            'facts': [('wechat_ocr', 'requires', 'image_data')],
            'memories': []
        }
    
    # 如果提供了image_base64，将其保存为临时文件
    temp_image_path = None
    if image_base64:
        try:
            # 解码base64数据
            image_data = base64.b64decode(image_base64)
            # 创建临时文件
            temp_image_path = '/tmp/temp_wechat_ocr_image.jpg'
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)
            image_path = temp_image_path
        except Exception as e:
            return {
                'result': {
                    'error': f'处理base64图片数据失败: {str(e)}'
                },
                'insights': [f'base64解码失败: {str(e)}'],
                'facts': [('wechat_ocr', 'base64_decode_error', str(e))],
                'memories': []
            }
    
    # 检查图片文件是否存在
    if not os.path.exists(image_path):
        return {
            'result': {
                'error': f'图片文件不存在: {image_path}'
            },
            'insights': [f'图片文件不存在: {image_path}'],
            'facts': [('wechat_ocr', 'image_not_found', image_path)],
            'memories': []
        }
    
    # 检查是否安装了必要的依赖
    tesseract_installed = False
    try:
        import pytesseract
        tesseract_installed = True
    except ImportError:
        # 尝试安装tesseract
        try:
            import subprocess
            result = subprocess.run(['pip', 'install', 'pytesseract'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                import pytesseract
                tesseract_installed = True
            else:
                return {
                    'result': {
                        'error': '无法安装pytesseract依赖'
                    },
                    'insights': ['依赖安装失败'],
                    'facts': [('wechat_ocr', 'dependency_installation', 'failed')],
                    'memories': []
                }
        except Exception:
            pass
    
    # 尝试安装Pillow
    pillow_installed = False
    try:
        from PIL import Image
        pillow_installed = True
    except ImportError:
        try:
            import subprocess
            result = subprocess.run(['pip', 'install', 'Pillow'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                from PIL import Image
                pillow_installed = True
            else:
                return {
                    'result': {
                        'error': '无法安装Pillow依赖'
                    },
                    'insights': ['依赖安装失败'],
                    'facts': [('wechat_ocr', 'dependency_installation', 'failed')],
                    'memories': []
                }
        except Exception:
            pass
    
    if not tesseract_installed or not pillow_installed:
        return {
            'result': {
                'error': '必要的依赖未安装：pytesseract或Pillow'
            },
            'insights': ['依赖缺失'],
            'facts': [('wechat_ocr', 'missing_dependencies', 'pytesseract_or_pillow')],
            'memories': []
        }
    
    # 检查Tesseract命令是否可用
    import subprocess
    tesseract_cmd = 'tesseract --version'
    result = subprocess.run(tesseract_cmd, shell=True, 
                           capture_output=True, text=True)
    if result.returncode != 0:
        return {
            'result': {
                'error': 'Tesseract OCR未安装或不可用'
            },
            'insights': ['Tesseract OCR未安装'],
            'facts': [('wechat_ocr', 'tesseract_status', 'not_available')],
            'memories': []
        }
    
    # 执行OCR提取
    try:
        # 使用Pillow打开图片
        img = Image.open(image_path)
        
        # 使用pytesseract进行OCR
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        
        # 清理提取的文本
        cleaned_text = text.strip()
        
        # 保存临时文件（如果存在）
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return {
            'result': {
                'ocr_text': cleaned_text,
                'extracted_text_length': len(cleaned_text),
                'image_path': args.get('image_path', ''),
                'success': True
            },
            'insights': ['OCR文本提取成功', f'提取文本长度: {len(cleaned_text)}'],
            'facts': [
                ('wechat_ocr', 'extracted_text_length', len(cleaned_text)),
                ('wechat_ocr', 'success', 'true')
            ],
            'memories': [
                f'OCR提取成功: 从图片 {image_path} 提取了 {len(cleaned_text)} 个字符的文本'
            ]
        }
        
    except Exception as e:
        # 清理临时文件（如果存在）
        if temp_image_path and os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return {
            'result': {
                'error': f'OCR提取失败: {str(e)}'
            },
            'insights': [f'OCR提取失败: {str(e)}'],
            'facts': [('wechat_ocr', 'extraction_error', str(e))],
            'memories': [f'OCR提取失败: {str(e)}']
        }