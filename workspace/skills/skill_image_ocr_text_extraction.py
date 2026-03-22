"""
自动生成的技能模块
需求: 直接使用pytesseract从图像中提取文本，不依赖其他技能调用
生成时间: 2026-03-21 13:12:56
"""

# skill_name: image_ocr_text_extraction
import pytesseract
from PIL import Image
import base64
import os
import tempfile
import subprocess

def main(args=None):
    """
    使用pytesseract从图像中提取文本内容
    
    参数:
    - image_path: 图像文件路径
    - image_base64: base64编码的图像数据
    - language: 识别语言，默认为'chi_sim+eng'（中文+英文）
    
    返回:
    - result: 包含提取的文本内容
    - insights: 关于OCR结果的洞察
    - capabilities: OCR能力信息
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', None)
    image_base64 = args.get('image_base64', None)
    language = args.get('language', 'chi_sim+eng')
    
    # 检查并安装tesseract
    try:
        import pytesseract
        tesseract_version = subprocess.check_output(['tesseract', '--version'], 
                                                  stderr=subprocess.STDOUT, 
                                                  universal_newlines=True)
    except (ImportError, subprocess.CalledProcessError):
        # 尝试安装tesseract
        try:
            # 检查系统类型
            import platform
            system = platform.system().lower()
            
            if system == 'linux':
                subprocess.run(['sudo', 'apt-get', 'update'], check=False)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'], check=False)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr-chi-sim'], check=False)
            elif system == 'darwin':  # macOS
                subprocess.run(['brew', 'install', 'tesseract'], check=False)
                subprocess.run(['brew', 'install', 'tesseract-lang'], check=False)
        except:
            pass  # 如果安装失败，继续尝试
    
    # 处理图像输入
    image = None
    if image_path and os.path.exists(image_path):
        image = Image.open(image_path)
    elif image_base64:
        # 解码base64图像
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
    else:
        return {
            'result': {'error': '未提供有效的图像路径或base64数据'},
            'insights': ['OCR操作失败，缺少图像输入'],
            'capabilities': []
        }
    
    # 执行OCR
    try:
        extracted_text = pytesseract.image_to_string(image, lang=language)
        
        # 清理提取的文本
        extracted_text = extracted_text.strip()
        
        insights = []
        if extracted_text:
            insights.append(f'成功从图像中提取到文本，共{len(extracted_text)}个字符')
            if len(extracted_text) > 100:
                insights.append('提取的文本内容较长，可能包含详细信息')
        else:
            insights.append('OCR未从图像中提取到任何文本内容')
        
        return {
            'result': {
                'extracted_text': extracted_text,
                'language_used': language
            },
            'insights': insights,
            'capabilities': ['OCR文本识别', '多语言支持', '图像文字提取']
        }
    except Exception as e:
        return {
            'result': {'error': f'OCR处理失败: {str(e)}'},
            'insights': ['OCR文本提取失败'],
            'capabilities': []
        }