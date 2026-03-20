"""
自动生成的技能模块
需求: 时序OCR工作流：从视频中按指定时间间隔或帧率抽取帧，然后对每个帧执行OCR文本识别，最后将结果按时间序列组织并保存。输入参数包括video_path（视频文件路径）、output_dir（输出目录）、interval（抽取时间间隔，默认1秒）、fps（目标帧率）和ocr_language（OCR语言，默认eng）。该技能应返回包含时间戳和对应文本内容的结果列表，以及处理状态和元数据。
生成时间: 2026-03-19 23:58:57
"""

# skill_name: temporal_ocr_video_workflow

import os
import subprocess
import json
import time
from datetime import datetime
import cv2
import pytesseract
from PIL import Image
import numpy as np

def main(args=None):
    """
    从视频中按指定时间间隔或帧率抽取帧，然后对每个帧执行OCR文本识别，
    最后将结果按时间序列组织并保存。
    
    参数:
    - video_path: 视频文件路径
    - output_dir: 输出目录
    - interval: 抽取时间间隔，默认1秒
    - fps: 目标帧率
    - ocr_language: OCR语言，默认eng
    """
    import json
    import os
    
    # 调试：打印接收到的args
    print(f"DEBUG: Received args: {args}")
    print(f"DEBUG: Type of args: {type(args)}")
    
    # 解析实际参数
    actual_args = {}
    if isinstance(args, dict) and 'input' in args:
        try:
            # input 是 JSON 字符串
            actual_args = json.loads(args['input'])
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，使用空字典
            actual_args = {}
    elif isinstance(args, str):
        try:
            actual_args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            actual_args = {}
    elif isinstance(args, dict):
        actual_args = args
    else:
        actual_args = {}
    
    # 获取参数
    video_path = actual_args.get('video_path')
    output_dir = actual_args.get('output_dir', './output')
    interval = actual_args.get('interval', 1)  # 默认1秒
    fps = actual_args.get('fps')
    ocr_language = actual_args.get('ocr_language', 'eng')
    
    if not video_path:
        return {
            'result': {'error': 'video_path is required'},
            'insights': ['缺少视频路径参数'],
            'status': 'failed'
        }
    
    if not os.path.exists(video_path):
        return {
            'result': {'error': 'video_path does not exist'},
            'insights': [f'视频文件不存在: {video_path}'],
            'status': 'failed'
        }
    
    # 检查依赖是否安装
    try:
        import cv2
        import pytesseract
    except ImportError as e:
        return {
            'result': {'error': f'缺少依赖: {str(e)}'},
            'insights': ['缺少必要的OCR或视频处理依赖'],
            'status': 'failed'
        }
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取视频信息
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        return {
            'result': {'error': '无法打开视频文件'},
            'insights': [f'视频文件无法打开: {video_path}'],
            'status': 'failed'
        }
    
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps_video = video_capture.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps_video
    
    # 计算需要提取的帧数
    if fps is not None:
        # 使用指定的帧率
        frame_interval = int(fps_video / fps)
    else:
        # 使用时间间隔
        frame_interval = int(fps_video * interval)
    
    if frame_interval <= 0:
        frame_interval = 1
    
    # 存储OCR结果
    ocr_results = []
    extracted_frames_count = 0
    
    # 提取帧并进行OCR
    frame_idx = 0
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
            
        # 检查是否需要提取当前帧
        if frame_idx % frame_interval == 0:
            # 保存帧到临时文件
            frame_filename = os.path.join(output_dir, f"frame_{frame_idx:06d}.jpg")
            cv2.imwrite(frame_filename, frame)
            
            # 对当前帧进行OCR
            try:
                pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                ocr_text = pytesseract.image_to_string(pil_image, lang=ocr_language)
                
                # 计算当前时间戳
                current_time = frame_idx / fps_video
                
                # 添加到结果列表
                ocr_results.append({
                    'timestamp': current_time,
                    'frame_index': frame_idx,
                    'frame_path': frame_filename,
                    'text': ocr_text.strip()
                })
                
                extracted_frames_count += 1
            except Exception as e:
                print(f"OCR处理出错: {e}")
        
        frame_idx += 1
    
    video_capture.release()
    
    # 保存结果到JSON文件
    results_file = os.path.join(output_dir, 'ocr_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(ocr_results, f, ensure_ascii=False, indent=2)
    
    # 生成处理报告
    processing_report = {
        'video_path': video_path,
        'output_dir': output_dir,
        'total_frames': total_frames,
        'video_fps': fps_video,
        'video_duration': duration,
        'frame_interval_used': frame_interval,
        'extracted_frames_count': extracted_frames_count,
        'ocr_language': ocr_language,
        'results_file': results_file,
        'results_count': len(ocr_results)
    }
    
    # 检查是否有OCR结果
    ocr_texts = [result['text'] for result in ocr_results if result['text'].strip()]
    
    insights = [
        f"处理完成: {video_path}",
        f"视频时长: {duration:.2f}秒",
        f"提取了 {extracted_frames_count} 个帧进行OCR",
        f"OCR结果保存到: {results_file}"
    ]
    
    if not ocr_texts:
        insights.append("警告: 没有提取到任何文本内容")
    else:
        insights.append(f"共提取到 {len(ocr_texts)} 个包含文本的帧")
    
    return {
        'result': {
            'processing_report': processing_report,
            'ocr_results': ocr_results,
            'status': 'success'
        },
        'insights': insights,
        'facts': [
            ['video_processing', 'has_duration', f"{duration:.2f}seconds"],
            ['video_processing', 'extracted_frames_count', str(extracted_frames_count)],
            ['ocr_results', 'total_count', str(len(ocr_results))]
        ],
        'status': 'success'
    }