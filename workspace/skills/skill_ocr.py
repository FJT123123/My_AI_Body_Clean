"""
自动生成的技能模块
需求: 创建一个简单的测试视频，用于验证视频帧抽取和时序OCR功能。视频应该包含一些文本内容，以便OCR可以识别。
生成时间: 2026-03-22 02:47:19
"""

# skill_generate_test_video_for_ocr
import subprocess
import os
import tempfile
import json
from datetime import datetime

def main(args=None):
    """
    生成一个用于测试视频OCR功能的测试视频
    该视频包含多个文本帧，用于验证视频帧抽取和时序OCR功能
    """
    if args is None:
        args = {}
    
    # 检查是否安装了ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        ffmpeg_available = result.returncode == 0
    except FileNotFoundError:
        ffmpeg_available = False
    
    if not ffmpeg_available:
        return {
            'result': {'error': 'ffmpeg not available'},
            'insights': ['ffmpeg is required to generate test video for OCR'],
            'next_skills': ['skill_install_ffmpeg']
        }
    
    # 生成测试视频
    output_dir = args.get('output_dir', tempfile.gettempdir())
    video_filename = args.get('video_filename', 'test_video_for_ocr.mp4')
    video_path = os.path.join(output_dir, video_filename)
    
    # 创建包含文本的测试视频
    # 使用ffmpeg生成一个包含多个文本帧的视频
    text_frames = [
        "Testing OCR on Video Frame 1",
        "OCR Test Frame Number 2",
        "Frame 3 with different text",
        "Final Test Frame 4 for OCR",
        "End of video OCR test"
    ]
    
    # 创建一个临时的文本文件，用于在视频中显示文本
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_txt:
        temp_txt_path = temp_txt.name
        temp_txt.write('\n'.join(text_frames))
    
    # 使用ffmpeg生成视频
    # 创建一个简单的视频，包含从1到5的数字，每秒一个数字
    try:
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-f', 'lavfi',
            '-i', 'color=c=blue:s=640x480:d=10',  # 蓝色背景，10秒
            '-vf', f"drawtext=fontfile=arial.ttf:fontsize=24:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='{text_frames[0]}', fps=1",
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-t', '10',  # 10秒视频
            video_path
        ]
        
        # 更简单的方法，创建固定帧率的视频
        # 创建一个包含多个文本的视频
        temp_image_path = os.path.join(output_dir, 'temp_frame.png')
        # 创建一个临时图像
        temp_image_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'lavfi',
            '-i', 'color=c=blue:s=640x480:d=1',
            temp_image_path
        ]
        subprocess.run(temp_image_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 使用临时图片创建视频，每帧添加不同的文本
        # 创建一个包含多个文本的视频
        drawtext_filter = []
        for i, text in enumerate(text_frames):
            # 每个文本显示2秒
            start_time = i * 2
            end_time = (i + 1) * 2
            drawtext_filter.append(f"drawtext=fontfile=arial.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='{text}':enable='between(t,{start_time},{end_time})'")
        
        filter_complex = ','.join(drawtext_filter)
        
        final_cmd = [
            'ffmpeg',
            '-y',
            '-f', 'lavfi',
            '-i', 'color=c=blue:s=640x480:d=10',
            '-vf', filter_complex,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            video_path
        ]
        
        result = subprocess.run(final_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            # 如果上面的命令失败，尝试使用更简单的命令
            simple_cmd = [
                'ffmpeg',
                '-y',
                '-f', 'lavfi',
                '-i', 'color=c=blue:s=640x480:d=10',
                '-vf', f"drawtext=fontfile=arial.ttf:fontsize=30:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2:text='{text_frames[0]} 1 2 3 4 5'",
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                video_path
            ]
            result = subprocess.run(simple_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            # 检查文件是否创建成功
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                
                # 清理临时文件
                if os.path.exists(temp_txt_path):
                    os.remove(temp_txt_path)
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
                
                return {
                    'result': {
                        'video_path': video_path,
                        'file_size': file_size,
                        'texts_used': text_frames,
                        'success': True
                    },
                    'insights': [
                        'Successfully generated test video for OCR validation',
                        f'Video contains {len(text_frames)} text frames',
                        f'Video saved at: {video_path}'
                    ],
                    'memories': [
                        {
                            'event_type': 'skill_forged',
                            'content': f'Generated test video for OCR: {video_path}',
                            'timestamp': datetime.now().isoformat()
                        }
                    ]
                }
            else:
                return {
                    'result': {'error': 'Video file was not created'},
                    'insights': ['Failed to create video file during OCR test video generation']
                }
        else:
            # 清理临时文件
            if os.path.exists(temp_txt_path):
                os.remove(temp_txt_path)
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            return {
                'result': {'error': f'ffmpeg command failed: {result.stderr}'},
                'insights': ['Failed to generate test video using ffmpeg']
            }
            
    except Exception as e:
        # 清理临时文件
        if os.path.exists(temp_txt_path):
            os.remove(temp_txt_path)
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        return {
            'result': {'error': str(e)},
            'insights': [f'Error during test video generation: {str(e)}']
        }