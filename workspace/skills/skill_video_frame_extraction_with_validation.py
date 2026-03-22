"""
自动生成的技能模块
需求: 从视频中高效抽取帧，并支持按时间间隔、帧率或特定时间点抽取，同时验证参数契约以确保API调用的稳定性。工具应包含完整的参数验证、错误处理和结果返回机制。
生成时间: 2026-03-22 01:15:48
"""

# skill_name: video_frame_extraction_with_validation
import cv2
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
import re

def validate_video_path(video_path: str) -> bool:
    """验证视频文件路径是否存在且格式正确"""
    if not video_path or not isinstance(video_path, str):
        return False
    if not os.path.exists(video_path):
        return False
    # 检查常见视频格式
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    _, ext = os.path.splitext(video_path.lower())
    return ext in valid_extensions

def validate_extraction_params(params: Dict) -> Dict:
    """验证视频帧提取参数"""
    errors = []
    
    # 验证输出目录
    output_dir = params.get('output_dir')
    if not output_dir or not isinstance(output_dir, str):
        errors.append("输出目录(output_dir)必须是有效字符串")
    elif not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建输出目录: {str(e)}")
    
    # 验证提取模式
    extraction_mode = params.get('extraction_mode', 'interval')
    valid_modes = ['interval', 'fps', 'specific_time', 'frame_indices']
    if extraction_mode not in valid_modes:
        errors.append(f"提取模式必须是以下之一: {valid_modes}")
    
    # 验证提取参数
    if extraction_mode == 'interval':
        interval = params.get('interval_seconds')
        if not isinstance(interval, (int, float)) or interval <= 0:
            errors.append("interval_seconds必须是大于0的数字")
    elif extraction_mode == 'fps':
        target_fps = params.get('target_fps')
        if not isinstance(target_fps, (int, float)) or target_fps <= 0:
            errors.append("target_fps必须是大于0的数字")
    elif extraction_mode == 'specific_time':
        time_points = params.get('time_points')
        if not isinstance(time_points, list) or not time_points:
            errors.append("time_points必须是非空列表")
        else:
            for t in time_points:
                if not isinstance(t, (int, float)) or t < 0:
                    errors.append(f"时间点 {t} 必须是非负数")
    elif extraction_mode == 'frame_indices':
        frame_indices = params.get('frame_indices')
        if not isinstance(frame_indices, list) or not frame_indices:
            errors.append("frame_indices必须是非空列表")
        else:
            for idx in frame_indices:
                if not isinstance(idx, int) or idx < 0:
                    errors.append(f"帧索引 {idx} 必须是非负整数")
    
    # 验证其他参数
    if 'max_frames' in params:
        max_frames = params['max_frames']
        if not isinstance(max_frames, int) or max_frames <= 0:
            errors.append("max_frames必须是大于0的整数")
    
    return {'valid': len(errors) == 0, 'errors': errors}

def extract_frames_by_interval(video_path: str, output_dir: str, interval_seconds: float, 
                              max_frames: Optional[int] = None) -> Dict:
    """按时间间隔提取帧"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'success': False, 'error': '无法打开视频文件'}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval_frames = int(fps * interval_seconds)
    
    extracted_frames = []
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % interval_frames == 0:
            timestamp = frame_count / fps
            filename = f"frame_{timestamp:.2f}s.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            extracted_frames.append({
                'filename': filename,
                'timestamp': timestamp,
                'frame_index': frame_count
            })
            extracted_count += 1
            
            if max_frames and extracted_count >= max_frames:
                break
        
        frame_count += 1
    
    cap.release()
    return {
        'success': True,
        'extracted_frames': extracted_frames,
        'total_extracted': len(extracted_frames),
        'interval_seconds': interval_seconds
    }

def extract_frames_by_fps(video_path: str, output_dir: str, target_fps: float, 
                         max_frames: Optional[int] = None) -> Dict:
    """按目标FPS提取帧"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'success': False, 'error': '无法打开视频文件'}
    
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 计算帧间隔
    frame_interval = int(source_fps / target_fps)
    if frame_interval < 1:
        frame_interval = 1
    
    extracted_frames = []
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % frame_interval == 0:
            timestamp = frame_count / source_fps
            filename = f"frame_{timestamp:.2f}s.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            extracted_frames.append({
                'filename': filename,
                'timestamp': timestamp,
                'frame_index': frame_count
            })
            extracted_count += 1
            
            if max_frames and extracted_count >= max_frames:
                break
        
        frame_count += 1
    
    cap.release()
    return {
        'success': True,
        'extracted_frames': extracted_frames,
        'total_extracted': len(extracted_frames),
        'target_fps': target_fps,
        'source_fps': source_fps
    }

def extract_frames_at_specific_times(video_path: str, output_dir: str, time_points: List[float], 
                                   max_frames: Optional[int] = None) -> Dict:
    """在特定时间点提取帧"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'success': False, 'error': '无法打开视频文件'}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    extracted_frames = []
    extracted_count = 0
    
    for time_point in time_points:
        if max_frames and extracted_count >= max_frames:
            break
            
        frame_number = int(time_point * fps)
        if frame_number >= total_frames:
            continue  # 时间点超出视频长度
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        
        if ret:
            filename = f"frame_{time_point:.2f}s.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            extracted_frames.append({
                'filename': filename,
                'timestamp': time_point,
                'frame_index': frame_number
            })
            extracted_count += 1
    
    cap.release()
    return {
        'success': True,
        'extracted_frames': extracted_frames,
        'total_extracted': len(extracted_frames),
        'time_points': time_points
    }

def extract_specific_frames(video_path: str, output_dir: str, frame_indices: List[int], 
                           max_frames: Optional[int] = None) -> Dict:
    """提取特定帧索引的帧"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {'success': False, 'error': '无法打开视频文件'}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    extracted_frames = []
    extracted_count = 0
    
    for frame_idx in frame_indices:
        if max_frames and extracted_count >= max_frames:
            break
            
        if frame_idx >= total_frames:
            continue  # 帧索引超出视频长度
            
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        
        if ret:
            timestamp = frame_idx / fps
            filename = f"frame_{frame_idx:06d}.jpg"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, frame)
            extracted_frames.append({
                'filename': filename,
                'timestamp': timestamp,
                'frame_index': frame_idx
            })
            extracted_count += 1
    
    cap.release()
    return {
        'success': True,
        'extracted_frames': extracted_frames,
        'total_extracted': len(extracted_frames),
        'frame_indices': frame_indices
    }

def main(args=None):
    """
    从视频中高效抽取帧的主函数，支持多种提取模式
    支持按时间间隔、帧率、特定时间点或特定帧索引提取
    包含完整的参数验证、错误处理和结果返回
    """
    if args is None:
        args = {}
    
    video_path = args.get('video_path')
    output_dir = args.get('output_dir', './extracted_frames')
    extraction_mode = args.get('extraction_mode', 'interval')
    max_frames = args.get('max_frames')
    
    # 验证视频路径
    if not validate_video_path(video_path):
        return {
            'result': {'success': False, 'error': '无效的视频文件路径'},
            'insights': ['视频文件路径验证失败'],
            'facts': [('视频路径', '验证', '失败')],
            'memories': []
        }
    
    # 构建参数字典
    params = {
        'video_path': video_path,
        'output_dir': output_dir,
        'extraction_mode': extraction_mode,
        'max_frames': max_frames
    }
    
    # 添加特定模式的参数
    if extraction_mode == 'interval':
        params['interval_seconds'] = args.get('interval_seconds', 1.0)
    elif extraction_mode == 'fps':
        params['target_fps'] = args.get('target_fps', 1.0)
    elif extraction_mode == 'specific_time':
        params['time_points'] = args.get('time_points', [])
    elif extraction_mode == 'frame_indices':
        params['frame_indices'] = args.get('frame_indices', [])
    
    # 验证参数
    validation_result = validate_extraction_params(params)
    if not validation_result['valid']:
        return {
            'result': {'success': False, 'error': '; '.join(validation_result['errors'])},
            'insights': ['参数验证失败'],
            'facts': [('参数验证', '结果', '失败')],
            'memories': []
        }
    
    # 执行帧提取
    try:
        if extraction_mode == 'interval':
            result = extract_frames_by_interval(
                video_path, output_dir, params['interval_seconds'], max_frames
            )
        elif extraction_mode == 'fps':
            result = extract_frames_by_fps(
                video_path, output_dir, params['target_fps'], max_frames
            )
        elif extraction_mode == 'specific_time':
            result = extract_frames_at_specific_times(
                video_path, output_dir, params['time_points'], max_frames
            )
        elif extraction_mode == 'frame_indices':
            result = extract_specific_frames(
                video_path, output_dir, params['frame_indices'], max_frames
            )
        else:
            result = {'success': False, 'error': '未知的提取模式'}
        
        if result['success']:
            insights = [f"成功提取 {result['total_extracted']} 个帧"]
            facts = [
                ('视频帧提取', '数量', result['total_extracted']),
                ('提取模式', '使用', extraction_mode),
                ('输出目录', '位置', output_dir)
            ]
            extracted_files = [frame['filename'] for frame in result['extracted_frames']]
            memories = [
                {
                    'event_type': 'skill_executed',
                    'content': f"视频帧提取完成，提取了 {result['total_extracted']} 个帧",
                    'timestamp': datetime.now().isoformat()
                }
            ]
            
            return {
                'result': result,
                'insights': insights,
                'facts': facts,
                'memories': memories,
                'extracted_files': extracted_files
            }
        else:
            return {
                'result': result,
                'insights': ['视频帧提取失败'],
                'facts': [('视频帧提取', '状态', '失败')],
                'memories': [
                    {
                        'event_type': 'skill_executed',
                        'content': f"视频帧提取失败: {result.get('error', '未知错误')}",
                        'timestamp': datetime.now().isoformat()
                    }
                ]
            }
    
    except Exception as e:
        error_msg = f"视频帧提取过程中发生异常: {str(e)}"
        return {
            'result': {'success': False, 'error': error_msg},
            'insights': ['视频帧提取过程中发生异常'],
            'facts': [('视频帧提取', '异常', str(e))],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': error_msg,
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }