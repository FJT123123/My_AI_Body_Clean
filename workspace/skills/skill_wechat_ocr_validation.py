"""
自动生成的技能模块
需求: 执行微信端到端验证的OCR提取，正确处理参数传递
生成时间: 2026-03-21 13:38:47
"""

# skill_name: wechat_ocr_validation
import base64
import json
import os
import subprocess
from PIL import Image
import io
import re

def main(args=None):
    """
    执行微信端到端验证的OCR提取，正确处理参数传递
    该技能专门用于处理微信截图中的文本内容提取，支持多种输入格式
    """
    if args is None:
        args = {}
    
    # 获取输入参数
    image_input = args.get('image_input', None)
    image_base64 = args.get('image_base64', None)
    image_path = args.get('image_path', None)
    context = args.get('__context__', {})
    
    # 确定实际的图像数据
    image_data = None
    
    if image_input:
        # 优先使用image_input
        if isinstance(image_input, str):
            if image_input.startswith('data:image'):
                # 是base64数据
                image_data = image_input
            elif os.path.exists(image_input):
                # 是文件路径
                with open(image_input, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
            else:
                # 可能是base64字符串
                try:
                    # 尝试解码base64
                    base64.b64decode(image_input)
                    image_data = image_input
                except:
                    return {'result': {'error': 'image_input格式不正确'}, 'insights': ['image_input参数格式错误']}
    elif image_base64:
        image_data = image_base64
    elif image_path and os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
    
    if not image_data:
        return {'result': {'error': '未提供有效的图像数据'}, 'insights': ['缺少有效的图像输入参数']}
    
    # 如果base64数据包含data:image前缀，需要去掉
    if image_data.startswith('data:image'):
        image_data = image_data.split(',', 1)[1]
    
    # 解码base64图像数据
    try:
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        return {'result': {'error': f'图像数据解码失败: {str(e)}'}, 'insights': ['图像数据格式错误']}
    
    # 尝试使用tesseract进行OCR
    try:
        # 检查tesseract是否安装
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            return {'result': {'error': 'tesseract未安装'}, 'insights': ['需要先安装tesseract OCR引擎']}
        
        # 保存图像到临时文件
        temp_path = '/tmp/wechat_ocr_temp.png'
        image.save(temp_path)
        
        # 执行OCR
        ocr_result = subprocess.run(['tesseract', temp_path, 'stdout'], capture_output=True, text=True)
        
        if ocr_result.returncode != 0:
            return {'result': {'error': f'OCR执行失败: {ocr_result.stderr}'}, 'insights': ['OCR处理失败']}
        
        extracted_text = ocr_result.stdout.strip()
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        # 进行微信特定内容的识别和结构化
        structured_content = extract_wechat_content(extracted_text)
        
        result_data = {
            'extracted_text': extracted_text,
            'structured_content': structured_content,
            'original_image_size': image.size,
            'text_length': len(extracted_text)
        }
        
        # 生成洞察
        insights = []
        if '微信' in extracted_text or 'WeChat' in extracted_text:
            insights.append('检测到微信相关文本')
        if len(extracted_text) > 0:
            insights.append(f'从图像中提取到{len(extracted_text)}个字符的文本')
        
        return {
            'result': result_data,
            'insights': insights,
            'memories': [f'从微信截图中提取文本: {extracted_text[:100]}...'],
            'facts': [['wechat_image', 'has_extracted_text', extracted_text[:50] if extracted_text else '']]
        }
        
    except FileNotFoundError:
        # 如果tesseract未找到，尝试使用其他方法
        return {'result': {'error': 'tesseract未找到'}, 'insights': ['OCR引擎未安装或不可用']}
    except Exception as e:
        return {'result': {'error': f'OCR处理异常: {str(e)}'}, 'insights': ['OCR处理过程中发生异常']}

def extract_wechat_content(text):
    """
    从OCR提取的文本中识别微信特定内容
    """
    # 定义微信相关内容的模式
    patterns = {
        'chats': r'[\u4e00-\u9fa5a-zA-Z0-9_\-]{1,20}:\s*.*?(?=\n|$)',
        'usernames': r'@[\u4e00-\u9fa5a-zA-Z0-9_\-]+',
        'emojis': r'[^\u0000-\u007F]{1,2}',
        'timestamps': r'\d{1,2}:\d{2}(?:\s*[AP]M)?',
        'phone_numbers': r'1[3-9]\d{9}',
        'wechat_ids': r'[a-zA-Z]{1}[\w\-]{5,19}'
    }
    
    extracted = {}
    
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            extracted[key] = matches
    
    # 识别对话结构
    lines = text.split('\n')
    chats = []
    current_user = None
    current_message = []
    
    for line in lines:
        # 检查是否是用户消息格式
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                user, message = parts[0].strip(), parts[1].strip()
                if len(user) <= 20 and (user.replace('_', '').replace('-', '').isalnum() or 
                                        any(c in user for c in ['@', '微信', 'WeChat'])):
                    # 如果有当前用户的消息，保存它
                    if current_user and current_message:
                        chats.append({
                            'user': current_user,
                            'message': ' '.join(current_message)
                        })
                    current_user = user
                    current_message = [message] if message else []
                else:
                    current_message.append(line)
            else:
                current_message.append(line)
        else:
            current_message.append(line)
    
    # 保存最后一条消息
    if current_user and current_message:
        chats.append({
            'user': current_user,
            'message': ' '.join(current_message)
        })
    
    if chats:
        extracted['chat_structure'] = chats
    
    return extracted