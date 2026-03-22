"""
自动生成的技能模块
需求: 从屏幕截图中提取文本内容的技能，使用真实的OCR技术
生成时间: 2026-03-21 13:01:57
"""

# skill_name: screen_ocr_text_extraction
import subprocess
import os
import sys
import tempfile
from PIL import Image
import pytesseract
from typing import Dict, Any, Optional

def check_tesseract_installed() -> bool:
    """检查系统是否已安装tesseract"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                               capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except subprocess.TimeoutExpired:
        return False

def install_tesseract():
    """尝试安装tesseract OCR引擎"""
    system = os.uname().sysname.lower() if os.name != 'nt' else 'windows'
    
    if system == 'darwin':  # macOS
        try:
            subprocess.run(['brew', 'install', 'tesseract'], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    elif system == 'linux':
        try:
            # 尝试使用apt
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # 尝试使用yum
                subprocess.run(['sudo', 'yum', 'install', '-y', 'tesseract'], check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
    elif system == 'windows':
        # Windows环境下需要手动安装，这里提供指导信息
        print("Windows系统需要手动安装Tesseract-OCR:")
        print("1. 下载安装包: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. 添加到系统PATH环境变量")
        return False
    
    return False

def validate_tesseract() -> bool:
    """验证tesseract是否可以正常工作"""
    try:
        # 创建一个简单的测试图像
        test_img = Image.new('RGB', (100, 50), color='white')
        result = pytesseract.image_to_string(test_img)
        return True
    except Exception:
        return False

def main(args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    从屏幕截图中提取文本内容的技能
    
    该技能使用OCR技术从屏幕截图中提取文本内容。
    支持PNG、JPG等常见图像格式的截图文件。
    """
    if args is None:
        args = {}
    
    # 获取截图路径
    image_path = args.get('image_path', '')
    if not image_path:
        return {
            'result': {'error': '缺少image_path参数'},
            'insights': ['需要提供截图文件路径'],
            'next_skills': ['skill_system_command_executor']
        }
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        return {
            'result': {'error': f'截图文件不存在: {image_path}'},
            'insights': ['指定的截图文件路径无效'],
            'next_skills': ['skill_system_command_executor']
        }
    
    # 检查tesseract是否已安装
    if not check_tesseract_installed():
        install_success = install_tesseract()
        if not install_success:
            return {
                'result': {'error': '无法安装tesseract OCR引擎'},
                'insights': ['OCR引擎未安装，需要手动安装tesseract'],
                'next_skills': ['skill_system_command_executor']
            }
    
    # 验证tesseract功能
    if not validate_tesseract():
        return {
            'result': {'error': 'tesseract OCR引擎验证失败'},
            'insights': ['OCR引擎安装但无法正常工作'],
            'next_skills': ['skill_system_command_executor']
        }
    
    try:
        # 打开图像文件
        image = Image.open(image_path)
        
        # 使用pytesseract进行OCR识别
        extracted_text = pytesseract.image_to_string(image)
        
        # 获取详细信息
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        # 统计识别信息
        n_boxes = len(data['text'])
        valid_boxes = [i for i in range(n_boxes) if int(data['conf'][i]) > 0]
        
        result = {
            'extracted_text': extracted_text.strip(),
            'image_path': image_path,
            'total_text_elements': n_boxes,
            'valid_text_elements': len(valid_boxes),
            'confidence_scores': [int(data['conf'][i]) for i in valid_boxes]
        }
        
        insights = []
        if result['extracted_text']:
            insights.append(f'成功从截图中提取到文本内容，共{len(result["extracted_text"])}个字符')
        if result['valid_text_elements'] > 0:
            avg_confidence = sum(result['confidence_scores']) / len(result['confidence_scores'])
            insights.append(f'平均识别置信度: {avg_confidence:.2f}%')
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                ['屏幕截图', '包含文本内容', str(len(result['extracted_text']) > 0)],
                ['OCR识别', '置信度', f"{sum(result['confidence_scores']) / len(result['confidence_scores']) if result['confidence_scores'] else 0:.2f}%"]
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': f'OCR处理失败: {str(e)}'},
            'insights': ['OCR处理过程中发生错误'],
            'next_skills': ['skill_system_command_executor']
        }