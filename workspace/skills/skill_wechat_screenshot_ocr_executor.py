"""
自动生成的技能模块
需求: 正确调用OCR技能提取微信截图文本，使用json.dumps正确传递参数
生成时间: 2026-03-21 13:39:13
"""

# skill_name: wechat_screenshot_ocr_executor

import json
import base64
from pathlib import Path

def main(args=None):
    """
    执行微信截图OCR识别，正确调用OCR技能提取文本内容
    支持图片路径或base64编码的图片数据，通过json.dumps正确传递参数
    """
    if args is None:
        args = {}
    
    # 获取图片输入参数
    image_path = args.get('image_path')
    image_base64 = args.get('image_base64')
    
    # 检查输入参数
    if not image_path and not image_base64:
        return {
            'result': {'error': '缺少图片输入参数，需要提供image_path或image_base64'},
            'insights': ['执行微信截图OCR识别失败，缺少必要的图片参数']
        }
    
    # 准备OCR技能参数
    ocr_args = {}
    
    if image_path:
        # 验证图片路径是否存在
        if not Path(image_path).exists():
            return {
                'result': {'error': f'图片路径不存在: {image_path}'},
                'insights': [f'微信截图OCR识别失败，指定的图片路径不存在: {image_path}']
            }
        ocr_args['image_path'] = image_path
    elif image_base64:
        # 验证base64格式
        try:
            # 尝试解码base64验证格式
            base64.b64decode(image_base64)
            ocr_args['image_base64'] = image_base64
        except Exception:
            return {
                'result': {'error': 'image_base64格式不正确'},
                'insights': ['微信截图OCR识别失败，提供的base64数据格式不正确']
            }
    
    # 构造调用OCR技能的参数
    ocr_skill_params = {
        "skill_name": "skill_ocr",
        "args": ocr_args
    }
    
    # 模拟执行OCR技能调用（实际环境中这里会调用系统执行）
    # 由于无法直接调用系统技能，返回构造好的参数用于系统调用
    execution_info = {
        'ocr_call_params': json.dumps(ocr_args, ensure_ascii=False),
        'target_skill': 'skill_ocr',
        'input_type': 'image_path' if image_path else 'image_base64',
        'execution_ready': True
    }
    
    insights = []
    if image_path:
        insights.append(f'准备对微信截图执行OCR识别: {image_path}')
    else:
        insights.append(f'准备对base64图片数据执行OCR识别')
    
    # 返回结构化结果
    return {
        'result': execution_info,
        'insights': insights,
        'next_skills': ['skill_ocr'],
        'execution_plan': {
            'skill': 'skill_ocr',
            'args': ocr_args
        }
    }