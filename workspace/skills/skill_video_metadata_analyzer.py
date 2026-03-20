"""
自动生成的技能模块
需求: 使用ffprobe分析视频文件的元数据，包括时长、分辨率、编码格式、帧率等信息。输入参数为video_path（视频文件路径），返回详细的视频元数据信息。
生成时间: 2026-03-19 17:14:02
"""

# skill_name: video_metadata_analyzer

import json
import subprocess
import os
from typing import Dict, Any

def main(input_args=None):
    """
    使用ffprobe分析视频文件的元数据，包括时长、分辨率、编码格式、帧率等信息
    
    参数:
        input_args: 可能是包含'input'键的字典，或者是直接的参数
    返回:
        包含视频元数据信息的字典
    """
    import json
    
    # 处理不同类型的输入结构
    actual_input = input_args
    if isinstance(input_args, dict) and 'input' in input_args:
        # 从包装结构中提取实际输入
        try:
            actual_input = json.loads(input_args['input'])
        except (json.JSONDecodeError, TypeError):
            actual_input = input_args['input'] if isinstance(input_args['input'], dict) else {}
    
    # 现在处理actual_input
    video_path = ''
    if isinstance(actual_input, dict):
        video_path = actual_input.get('video_path', '')
    elif isinstance(actual_input, str):
        try:
            # 尝试解析为JSON
            parsed_input = json.loads(actual_input)
            if isinstance(parsed_input, dict):
                video_path = parsed_input.get('video_path', '')
            else:
                video_path = actual_input
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，将整个字符串视为视频路径
            video_path = actual_input.strip()
    elif actual_input is None:
        pass
    else:
        return {
            'result': {'error': '无效的输入参数格式'},
            'insights': ['输入参数格式不支持'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    if not video_path:
        return {
            'result': {'error': '未提供视频文件路径'},
            'insights': ['缺少video_path参数'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': ['指定的视频文件路径不存在'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    
    try:
        # 使用ffprobe获取视频元数据
        result = subprocess.run([
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            '-show_streams', 
            video_path
        ], capture_output=True, text=True, check=True)
        
        metadata = json.loads(result.stdout)
        
        # 提取视频流信息
        video_stream = None
        audio_stream = None
        
        for stream in metadata.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        # 提取音频流信息
        for stream in metadata.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        # 构建视频元数据结果
        video_info = {
            'format': metadata.get('format', {}),
            'video_stream': video_stream,
            'audio_stream': audio_stream
        }
        
        # 提取关键信息
        result_data = {
            'file_path': video_path,
            'duration': float(metadata['format'].get('duration', 0)),
            'size_bytes': int(metadata['format'].get('size', 0)),
            'format_name': metadata['format'].get('format_name', ''),
            'bit_rate': int(metadata['format'].get('bit_rate', 0)),
            'video': {
                'codec_name': video_stream.get('codec_name', '') if video_stream else 'N/A',
                'width': int(video_stream.get('width', 0)) if video_stream else 0,
                'height': int(video_stream.get('height', 0)) if video_stream else 0,
                'r_frame_rate': video_stream.get('r_frame_rate', 'N/A') if video_stream else 'N/A',
                'avg_frame_rate': video_stream.get('avg_frame_rate', 'N/A') if video_stream else 'N/A',
                'bit_rate': video_stream.get('bit_rate', 'N/A') if video_stream else 'N/A',
                'pix_fmt': video_stream.get('pix_fmt', 'N/A') if video_stream else 'N/A'
            },
            'audio': {
                'codec_name': audio_stream.get('codec_name', 'N/A') if audio_stream else 'N/A',
                'sample_rate': int(audio_stream.get('sample_rate', 0)) if audio_stream else 0,
                'channels': int(audio_stream.get('channels', 0)) if audio_stream else 0,
                'bit_rate': audio_stream.get('bit_rate', 'N/A') if audio_stream else 'N/A'
            }
        }
        
        # 构建返回数据
        return {
            'result': result_data,
            'insights': [
                f'视频时长: {result_data["duration"]:.2f}秒',
                f'分辨率: {result_data["video"]["width"]}x{result_data["video"]["height"]}',
                f'视频编码: {result_data["video"]["codec_name"]}',
                f'音频编码: {result_data["audio"]["codec_name"]}'
            ],
            'facts': [
                ['video_file', 'has_duration', f'{result_data["duration"]:.2f} seconds'],
                ['video_file', 'has_resolution', f'{result_data["video"]["width"]}x{result_data["video"]["height"]}'],
                ['video_file', 'has_video_codec', result_data["video"]["codec_name"]],
                ['video_file', 'has_audio_codec', result_data["audio"]["codec_name"]]
            ],
            'memories': [
                f'分析视频文件: {video_path}, 时长: {result_data["duration"]:.2f}秒, 分辨率: {result_data["video"]["width"]}x{result_data["video"]["height"]}'
            ],
            'capabilities': [],
            'next_skills': []
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': f'ffprobe执行失败: {e.stderr}'},
            'insights': ['ffprobe命令执行失败，可能需要安装ffmpeg'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    except json.JSONDecodeError:
        return {
            'result': {'error': '解析ffprobe输出失败'},
            'insights': ['ffprobe输出格式异常'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }
    except Exception as e:
        return {
            'result': {'error': f'分析视频文件时发生错误: {str(e)}'},
            'insights': [f'视频分析过程中出现异常: {str(e)}'],
            'facts': [],
            'memories': [],
            'capabilities': [],
            'next_skills': []
        }