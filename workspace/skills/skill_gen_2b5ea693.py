"""
自动生成的技能模块
需求: 创建一个简单的测试视频，使用正确的参数传递方式。
生成时间: 2026-03-22 02:48:46
"""

# skill_generate_simple_test_video
import subprocess
import os
import sys
from typing import Dict, Any

def main(args=None) -> Dict[str, Any]:
    """
    创建一个简单的测试视频文件，使用ffmpeg生成测试视频
    输入参数应包含：duration（视频时长，秒），output_path（输出路径）
    """
    if args is None:
        args = {}
    
    duration = args.get('duration', 10)
    output_path = args.get('output_path', 'test_video.mp4')
    
    # 检查ffmpeg是否可用
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        ffmpeg_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_available = False
    
    if not ffmpeg_available:
        return {
            'result': {'error': 'ffmpeg not available'},
            'insights': ['ffmpeg command not found'],
            'capabilities': [],
            'next_skills': ['skill_install_ffmpeg']
        }
    
    # 生成测试视频
    try:
        cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-f', 'lavfi',  # 使用lavfi滤镜
            '-i', f'testsrc=size=1920x1080:rate=1',  # 生成测试源
            '-vf', 'drawtext=text="Test Video":fontsize=30:fontcolor=white:x=100:y=100',  # 添加文字
            '-t', str(duration),  # 持续时间
            '-c:v', 'libx264',  # 视频编码
            '-pix_fmt', 'yuv420p',  # 像素格式
            '-preset', 'fast',  # 编码预设
            output_path  # 输出文件
        ]
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              check=True)
        
        # 验证文件是否成功创建
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            return {
                'result': {
                    'success': True,
                    'output_path': output_path,
                    'file_size': file_size
                },
                'insights': [f'成功生成测试视频，大小为 {file_size} 字节'],
                'facts': [
                    ['test_video', 'has_path', output_path],
                    ['test_video', 'has_duration', str(duration)],
                    ['test_video', 'has_size', str(file_size)]
                ],
                'memories': [
                    {
                        'event_type': 'skill_forged',
                        'content': f'创建了测试视频 {output_path}，时长 {duration}秒',
                        'importance': 0.5,
                        'timestamp': None,
                        'tags': ['video', 'test']
                    }
                ],
                'capabilities': ['video_generation'],
                'next_skills': []
            }
        else:
            return {
                'result': {'error': 'Video file was not created'},
                'insights': ['ffmpeg命令执行但未生成输出文件'],
                'next_skills': ['skill_check_ffmpeg_installation']
            }
    
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': f'ffmpeg command failed: {e.stderr}'},
            'insights': ['ffmpeg命令执行失败'],
            'next_skills': ['skill_check_ffmpeg_installation']
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': ['生成视频时发生未知错误'],
            'next_skills': []
        }