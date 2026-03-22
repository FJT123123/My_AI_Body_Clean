"""
自动生成的技能模块
需求: 直接调用数字完整性与物理语义双重验证能力，测试test_video.mp4
生成时间: 2026-03-21 14:25:11
"""

# skill_name: video_integrity_physical_semantic_validation
import subprocess
import os
import json
from pathlib import Path

def main(args=None):
    """
    对视频文件进行数字完整性与物理语义双重验证
    该技能检查视频的数字完整性（文件格式、编码参数等）和物理语义完整性（帧率、时长、分辨率等）
    """
    if args is None:
        args = {}
    
    # 获取视频路径参数
    video_path = args.get('video_path', 'test_video.mp4')
    
    # 验证输入文件是否存在
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'无法找到视频文件: {video_path}'],
            'facts': [],
            'memories': []
        }
    
    # 检查 ffmpeg 是否已安装
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        ffmpeg_installed = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_installed = False
        # 尝试安装 ffmpeg
        try:
            subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
            ffmpeg_installed = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['apt-get', 'update'], check=True)
                subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], check=True)
                ffmpeg_installed = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(['yum', 'install', '-y', 'ffmpeg'], check=True)
                    ffmpeg_installed = True
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return {
                        'result': {'error': 'ffmpeg 未安装且无法自动安装'},
                        'insights': ['视频验证需要 ffmpeg 工具，但系统中未找到且无法自动安装'],
                        'facts': [],
                        'memories': []
                    }
    
    if not ffmpeg_installed:
        return {
            'result': {'error': 'ffmpeg 未安装'},
            'insights': ['视频验证需要 ffmpeg 工具，但系统中未找到'],
            'facts': [],
            'memories': []
        }
    
    # 使用 ffprobe 获取视频信息
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        
        # 提取格式信息
        format_info = video_info.get('format', {})
        streams = video_info.get('streams', [])
        
        # 数字完整性检查
        digital_integrity = {
            'file_size': format_info.get('size', 'unknown'),
            'bit_rate': format_info.get('bit_rate', 'unknown'),
            'format_name': format_info.get('format_name', 'unknown'),
            'nb_streams': format_info.get('nb_streams', 'unknown'),
            'duration': format_info.get('duration', 'unknown'),
            'start_time': format_info.get('start_time', 'unknown')
        }
        
        # 物理语义完整性检查
        video_stream = None
        audio_stream = None
        
        for stream in streams:
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        physical_semantic_info = {}
        
        if video_stream:
            physical_semantic_info['video'] = {
                'codec_name': video_stream.get('codec_name', 'unknown'),
                'width': video_stream.get('width', 'unknown'),
                'height': video_stream.get('height', 'unknown'),
                'avg_frame_rate': video_stream.get('avg_frame_rate', 'unknown'),
                'r_frame_rate': video_stream.get('r_frame_rate', 'unknown'),
                'duration': video_stream.get('duration', 'unknown'),
                'bit_rate': video_stream.get('bit_rate', 'unknown'),
                'sample_aspect_ratio': video_stream.get('sample_aspect_ratio', 'unknown'),
                'display_aspect_ratio': video_stream.get('display_aspect_ratio', 'unknown'),
                'pix_fmt': video_stream.get('pix_fmt', 'unknown'),
                'codec_long_name': video_stream.get('codec_long_name', 'unknown')
            }
        
        if audio_stream:
            physical_semantic_info['audio'] = {
                'codec_name': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': audio_stream.get('sample_rate', 'unknown'),
                'channels': audio_stream.get('channels', 'unknown'),
                'channel_layout': audio_stream.get('channel_layout', 'unknown'),
                'duration': audio_stream.get('duration', 'unknown'),
                'bit_rate': audio_stream.get('bit_rate', 'unknown'),
                'codec_long_name': audio_stream.get('codec_long_name', 'unknown')
            }
        
        # 执行帧提取验证
        try:
            test_frame_path = f"test_frame_{os.path.basename(video_path)}.png"
            extract_cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vframes', '1',
                '-f', 'image2',
                test_frame_path
            ]
            subprocess.run(extract_cmd, capture_output=True, check=True)
            
            if os.path.exists(test_frame_path):
                os.remove(test_frame_path)  # 清理临时文件
                frame_extraction_success = True
            else:
                frame_extraction_success = False
        except subprocess.CalledProcessError:
            frame_extraction_success = False
        
        # 执行完整性验证
        digital_integrity_valid = all([
            digital_integrity['file_size'] != 'unknown',
            digital_integrity['format_name'] != 'unknown',
            digital_integrity['duration'] != 'unknown'
        ])
        
        physical_semantic_valid = True
        if video_stream:
            video_checks = [
                physical_semantic_info['video']['width'] != 'unknown',
                physical_semantic_info['video']['height'] != 'unknown',
                physical_semantic_info['video']['avg_frame_rate'] != 'unknown',
                physical_semantic_info['video']['codec_name'] != 'unknown'
            ]
            physical_semantic_valid = physical_semantic_valid and all(video_checks)
        
        if audio_stream:
            audio_checks = [
                physical_semantic_info['audio']['sample_rate'] != 'unknown',
                physical_semantic_info['audio']['channels'] != 'unknown',
                physical_semantic_info['audio']['codec_name'] != 'unknown'
            ]
            physical_semantic_valid = physical_semantic_valid and all(audio_checks)
        
        # 综合验证结果
        overall_valid = digital_integrity_valid and physical_semantic_valid and frame_extraction_success
        
        result = {
            'digital_integrity': digital_integrity,
            'physical_semantic_info': physical_semantic_info,
            'digital_integrity_valid': digital_integrity_valid,
            'physical_semantic_valid': physical_semantic_valid,
            'frame_extraction_success': frame_extraction_success,
            'overall_valid': overall_valid,
            'video_path': video_path
        }
        
        insights = []
        if overall_valid:
            insights.append(f'视频 {video_path} 通过了数字完整性与物理语义双重验证')
        else:
            insights.append(f'视频 {video_path} 未通过完整性验证')
            if not digital_integrity_valid:
                insights.append('数字完整性检查失败')
            if not physical_semantic_valid:
                insights.append('物理语义完整性检查失败')
            if not frame_extraction_success:
                insights.append('帧提取验证失败')
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                [video_path, 'has_digital_integrity_valid', str(digital_integrity_valid)],
                [video_path, 'has_physical_semantic_valid', str(physical_semantic_valid)],
                [video_path, 'has_frame_extraction_success', str(frame_extraction_success)],
                [video_path, 'has_overall_valid', str(overall_valid)]
            ],
            'memories': [
                f"视频完整性验证完成: {video_path}, 数字完整性: {digital_integrity_valid}, 物理语义完整性: {physical_semantic_valid}, 帧提取成功: {frame_extraction_success}"
            ]
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': f'视频分析失败: {str(e)}'},
            'insights': [f'视频 {video_path} 分析过程中出现错误'],
            'facts': [],
            'memories': [f"视频完整性验证失败: {video_path}, 错误: {str(e)}"]
        }
    except json.JSONDecodeError:
        return {
            'result': {'error': '无法解析视频信息'},
            'insights': [f'视频 {video_path} 信息解析失败'],
            'facts': [],
            'memories': [f"视频完整性验证失败: {video_path}, 无法解析视频信息"]
        }
    except Exception as e:
        return {
            'result': {'error': f'验证过程中出现异常: {str(e)}'},
            'insights': [f'视频 {video_path} 验证过程中出现异常'],
            'facts': [],
            'memories': [f"视频完整性验证异常: {video_path}, 错误: {str(e)}"]
        }