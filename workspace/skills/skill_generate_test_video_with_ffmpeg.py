"""
自动生成的技能模块
需求: 创建一个简单的测试视频文件，用于验证视频处理环境是否正常工作。使用ffmpeg生成一个5秒的测试视频。
生成时间: 2026-03-19 15:00:41
"""

# skill_name: generate_test_video_with_ffmpeg

import subprocess
import os
import sys
from pathlib import Path

def main(args=None):
    """
    使用FFmpeg生成一个简单的测试视频文件，用于验证视频处理环境是否正常工作
    生成5秒的测试视频，包含彩色渐变和音频音调
    """
    args = args or {}
    
    # 获取参数
    output_path = args.get('video_path', 'test_video.mp4')
    duration = args.get('duration', 5)
    width = args.get('width', 640)
    height = args.get('height', 480)
    
    # 验证FFmpeg是否可用
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        ffmpeg_available = True
        ffmpeg_version = result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_available = False
        ffmpeg_version = None
    
    if not ffmpeg_available:
        return {
            'result': {'error': 'FFmpeg not available', 'ffmpeg_version': None},
            'insights': ['FFmpeg是必需的依赖，需要先安装FFmpeg才能生成测试视频'],
            'capabilities': [],
            'next_skills': ['skill_install_ffmpeg_via_brew']
        }
    
    # 构建FFmpeg命令
    # 生成带有移动圆形和音频的测试视频，用于运动语义分析验证
    cmd = [
        'ffmpeg',
        '-y',  # 覆盖输出文件
        '-f', 'lavfi',  # 使用lavfi滤镜生成视频
        '-i', f'testsrc2=s={width}x{height}:d={duration}:r=30,boxblur=1:1',  # 生成包含移动元素的测试视频
        '-f', 'lavfi',
        '-i', f'sine=frequency=440:duration={duration}',  # 生成440Hz音频
        '-c:v', 'libx264',  # 视频编码
        '-c:a', 'aac',  # 音频编码
        '-pix_fmt', 'yuv420p',  # 像素格式
        '-shortest',  # 使用最短输入的长度
        output_path
    ]
    
    try:
        # 执行FFmpeg命令
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 验证文件是否生成成功
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            file_path = Path(output_path)
            
            # 获取视频信息
            probe_cmd = ['ffprobe', '-v', 'quiet', '-show_format', '-show_streams', output_path]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
            
            return {
                'result': {
                    'success': True,
                    'video_path': str(file_path.absolute()),
                    'file_size': file_size,
                    'duration': duration,
                    'dimensions': f"{width}x{height}",
                    'ffmpeg_version': ffmpeg_version
                },
                'insights': [
                    f'成功生成测试视频: {output_path}',
                    f'视频时长: {duration}秒',
                    f'分辨率: {width}x{height}',
                    f'文件大小: {file_size} bytes'
                ],
                'facts': [
                    ['test_video', 'has_path', str(file_path.absolute())],
                    ['test_video', 'has_duration', str(duration)],
                    ['test_video', 'has_resolution', f"{width}x{height}"],
                    ['test_video', 'has_file_size', str(file_size)]
                ],
                'memories': [
                    f'生成测试视频文件: {output_path} (大小: {file_size} bytes, 时长: {duration}秒)'
                ],
                'capabilities': ['video_generation', 'ffmpeg_utilization'],
                'next_skills': []
            }
        else:
            return {
                'result': {'error': '视频文件未生成', 'ffmpeg_output': result.stderr},
                'insights': ['FFmpeg执行完成但未生成预期的视频文件'],
                'capabilities': [],
                'next_skills': []
            }
            
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': 'FFmpeg执行失败', 'command': ' '.join(cmd), 'stderr': e.stderr},
            'insights': [f'FFmpeg命令执行失败: {e.stderr}'],
            'capabilities': [],
            'next_skills': []
        }
    except Exception as e:
        return {
            'result': {'error': f'生成测试视频时发生异常: {str(e)}'},
            'insights': [f'生成测试视频时发生异常: {str(e)}'],
            'capabilities': [],
            'next_skills': []
        }