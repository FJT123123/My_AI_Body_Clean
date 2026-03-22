"""
自动生成的技能模块
需求: 修复FFmpeg命令参数顺序问题，正确提取视频帧。使用正确的参数顺序：ffmpeg -i input_video -vf fps=fps_value -frames:v max_frames output_pattern
生成时间: 2026-03-21 14:50:10
"""

# skill_name: ffmpeg_frame_extraction_fixer

import subprocess
import os
import json
import re

def main(args=None):
    """
    修复FFmpeg命令参数顺序问题，正确提取视频帧
    使用正确的参数顺序：ffmpeg -i input_video -vf fps=fps_value -frames:v max_frames output_pattern
    """
    if args is None:
        args = {}
    
    # 从参数中获取输入信息
    video_path = args.get('video_path', '')
    output_dir = args.get('output_dir', './frames')
    fps_value = args.get('fps', 1)
    max_frames = args.get('max_frames', 100)
    
    if not video_path:
        return {
            'result': {'error': 'video_path is required'},
            'insights': ['视频路径参数缺失，无法执行帧提取'],
            'facts': [],
            'memories': ['尝试执行FFmpeg帧提取但缺少视频路径参数']
        }
    
    # 检查FFmpeg是否可用
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        ffmpeg_available = True
        ffmpeg_version = result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_available = False
        ffmpeg_version = None
    
    if not ffmpeg_available:
        return {
            'result': {'error': 'FFmpeg is not available on this system'},
            'insights': ['系统中未找到FFmpeg命令，无法执行视频处理'],
            'facts': [('system', 'has_ffmpeg', 'false')],
            'memories': ['FFmpeg未安装，需要先安装FFmpeg才能执行帧提取']
        }
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 构建正确的FFmpeg命令
    output_pattern = os.path.join(output_dir, 'frame_%04d.jpg')
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={fps_value}',
        '-frames:v', str(max_frames),
        '-y',  # 覆盖输出文件
        output_pattern
    ]
    
    # 执行FFmpeg命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        execution_success = True
        stderr_output = result.stderr
    except subprocess.CalledProcessError as e:
        execution_success = False
        stderr_output = e.stderr
        
    # 检查输出目录中生成的帧文件
    if os.path.exists(output_dir):
        frame_files = [f for f in os.listdir(output_dir) if f.startswith('frame_') and f.endswith('.jpg')]
        frame_count = len(frame_files)
    else:
        frame_files = []
        frame_count = 0
    
    # 准备返回结果
    result_data = {
        'video_path': video_path,
        'output_dir': output_dir,
        'fps': fps_value,
        'max_frames': max_frames,
        'frame_count': frame_count,
        'ffmpeg_version': ffmpeg_version,
        'execution_success': execution_success
    }
    
    if not execution_success:
        result_data['error'] = stderr_output
    
    # 生成洞察信息
    insights = []
    if execution_success:
        insights.append(f'成功从视频 {video_path} 提取了 {frame_count} 帧图像')
        insights.append(f'使用了正确的FFmpeg参数顺序：-i input -vf fps={fps_value} -frames:v {max_frames}')
    else:
        insights.append(f'FFmpeg帧提取失败，错误信息：{stderr_output}')
    
    # 生成事实三元组
    facts = [
        ('ffmpeg', 'is_available', 'true' if ffmpeg_available else 'false'),
        ('video_processor', 'uses_ffmpeg_fix', 'true'),
        ('frames_extracted', 'count', str(frame_count))
    ]
    
    # 生成记忆事件
    memories = [
        f'使用FFmpeg从视频 {video_path} 成功提取了 {frame_count} 帧图像',
        f'FFmpeg版本: {ffmpeg_version}',
        f'参数设置: fps={fps_value}, max_frames={max_frames}'
    ]
    
    # 如果成功提取，可能需要后续处理
    next_skills = []
    if execution_success and frame_count > 0:
        next_skills = ['skill_image_analyzer']  # 可以继续分析提取的帧
    
    return {
        'result': result_data,
        'insights': insights,
        'facts': facts,
        'memories': memories,
        'next_skills': next_skills
    }