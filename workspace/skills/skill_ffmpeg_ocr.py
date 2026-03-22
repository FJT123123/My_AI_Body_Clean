"""
自动生成的技能模块
需求: 使用ffmpeg创建一个包含文本的简单测试视频，用于验证视频帧抽取和OCR功能。
生成时间: 2026-03-22 02:47:54
"""

# skill_create_test_video_for_ocr
import subprocess
import os
import tempfile
import time
from pathlib import Path

def main(args=None):
    """
    创建一个包含文本的测试视频，用于验证视频帧抽取和OCR功能
    该技能使用ffmpeg创建一个简单的视频，其中包含明显的文本内容，用于后续的OCR识别测试
    """
    if args is None:
        args = {}
    
    # 从参数中获取配置
    text_content = args.get('text_content', 'Test OCR Video')
    output_path = args.get('output_path', None)
    duration = args.get('duration', 10)
    width = args.get('width', 1280)
    height = args.get('height', 720)
    
    # 生成临时输出路径
    if not output_path:
        output_path = os.path.join(tempfile.gettempdir(), f"test_video_ocr_{int(time.time())}.mp4")
    
    # 检查ffmpeg是否可用
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        ffmpeg_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {
            'result': {'error': 'ffmpeg is not available'},
            'insights': ['ffmpeg not found in system PATH'],
            'capabilities': []
        }
    
    # 构建ffmpeg命令
    # 创建一个带文本的测试视频
    cmd = [
        'ffmpeg',
        '-y',  # 覆盖输出文件
        '-f', 'lavfi',
        '-i', f"color=c=white:s={width}x{height}:d={duration}",  # 生成白色背景
        '-vf', f"drawtext=fontfile=arial.ttf:fontsize=48:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2:text='{text_content}'",  # 添加文本
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-t', str(duration),
        output_path
    ]
    
    # 尝试执行命令
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        success = True
    except subprocess.CalledProcessError as e:
        # 如果使用默认字体失败，尝试不指定字体文件
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'lavfi',
            '-i', f"color=c=white:s={width}x{height}:d={duration}",
            '-vf', f"drawtext=fontsize=48:fontcolor=black:x=(w-text_w)/2:y=(h-text_h)/2:text='{text_content}'",
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-t', str(duration),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            success = True
        except subprocess.CalledProcessError as e:
            return {
                'result': {'error': f'ffmpeg command failed: {str(e)}', 'stderr': e.stderr},
                'insights': ['Failed to create test video with text'],
                'capabilities': []
            }
    
    # 验证文件是否创建成功
    if success and os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        return {
            'result': {
                'success': True,
                'video_path': output_path,
                'file_size': file_size,
                'text_content': text_content,
                'duration': duration,
                'resolution': f"{width}x{height}"
            },
            'insights': [
                f"Test video created successfully at {output_path}",
                f"Video contains text: '{text_content}'",
                f"File size: {file_size} bytes"
            ],
            'capabilities': [
                'Video generation with embedded text',
                'Test video creation for OCR validation'
            ],
            'next_skills': ['skill_extract_video_frames', 'skill_ocr']
        }
    else:
        return {
            'result': {'error': 'Video file was not created successfully'},
            'insights': ['Video file creation failed'],
            'capabilities': []
        }