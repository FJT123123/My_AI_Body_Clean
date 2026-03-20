# tool_name: create_high_framerate_test_video
from langchain.tools import tool
import subprocess
import os
import tempfile
import json

@tool
def create_high_framerate_test_video(input_args: str) -> dict:
    """
    创建高帧率测试视频，用于测试GPU/硬件编解码器在高帧率条件下的处理能力限制
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - framerate (int, optional): 目标帧率，可选30, 60, 120，默认60
            - resolution (str, optional): 视频分辨率，格式为"widthxheight"，默认"1920x1080"
            - duration (int, optional): 视频时长（秒），默认5
            - output_path (str, optional): 输出文件路径，如果为None则自动生成
    
    Returns:
        dict: 包含视频路径和元数据的字典
    """
    try:
        args = json.loads(input_args) if input_args else {}
        framerate = args.get('framerate', 60)
        resolution = args.get('resolution', '1920x1080')
        duration = args.get('duration', 5)
        output_path = args.get('output_path', None)
        
        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), f"high_fps_{framerate}_test.mp4")
        
        # 解析分辨率
        width, height = map(int, resolution.split('x'))
        
        # 使用ffmpeg创建高帧率测试视频
        cmd = [
            'ffmpeg',
            '-y',  # 覆盖输出文件
            '-f', 'lavfi',
            '-i', f'testsrc=duration={duration}:size={width}x{height}:rate={framerate}',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-r', str(framerate),
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'FFmpeg failed: {result.stderr}',
                    'video_path': None
                }
            
            # 获取视频元数据
            metadata_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                           '-show_streams', '-show_format', output_path]
            metadata_result = subprocess.run(metadata_cmd, capture_output=True, text=True)
            
            if metadata_result.returncode == 0:
                metadata = json.loads(metadata_result.stdout)
                return {
                    'success': True,
                    'video_path': output_path,
                    'metadata': metadata,
                    'target_framerate': framerate,
                    'actual_framerate': None,
                    'resolution': resolution,
                    'duration': duration
                }
            else:
                return {
                    'success': True,
                    'video_path': output_path,
                    'metadata': None,
                    'target_framerate': framerate,
                    'resolution': resolution,
                    'duration': duration
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'FFmpeg command timed out',
                'video_path': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'video_path': None
            }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Invalid input_args JSON format',
            'video_path': None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'video_path': None
        }