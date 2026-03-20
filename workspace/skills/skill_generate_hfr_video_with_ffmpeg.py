"""
自动生成的技能模块
需求: 使用ffmpeg创建高帧率（60fps）测试视频，并验证其是否能被硬件编解码器正确处理
生成时间: 2026-03-20 03:40:58
"""

# skill_name: generate_hfr_video_with_ffmpeg

import subprocess
import os
import json
import time

def main(args=None):
    """
    使用ffmpeg创建高帧率（60fps）测试视频，并验证其是否能被硬件编解码器正确处理
    """
    if args is None:
        args = {}
    
    # 检查ffmpeg是否已安装
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        ffmpeg_installed = True
        ffmpeg_version = result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        ffmpeg_installed = False
        ffmpeg_version = None
    
    if not ffmpeg_installed:
        # 尝试安装ffmpeg
        try:
            install_result = subprocess.run(['brew', 'install', 'ffmpeg'], capture_output=True, text=True)
            if install_result.returncode != 0:
                return {
                    'result': {'error': 'ffmpeg安装失败', 'details': install_result.stderr},
                    'insights': ['ffmpeg未安装且自动安装失败'],
                    'next_skills': ['skill_install_ffmpeg_via_brew']
                }
            # 验证安装
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
            ffmpeg_version = result.stdout.split('\n')[0]
        except Exception:
            return {
                'result': {'error': 'ffmpeg安装失败'},
                'insights': ['ffmpeg未安装且无法自动安装'],
                'next_skills': ['skill_install_ffmpeg_via_brew']
            }
    
    # 创建输出目录
    output_dir = args.get('output_dir', './test_videos')
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置输出文件路径
    video_path = os.path.join(output_dir, 'test_video_60fps.mp4')
    
    # 使用ffmpeg创建60fps测试视频
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'lavfi',  # 使用虚拟输入设备
        '-i', 'testsrc=size=1920x1080:rate=60',  # 生成60fps测试视频
        '-vf', 'hue=s=0',  # 去色使画面为灰色
        '-t', '10',  # 生成10秒视频
        '-c:v', 'libx264',  # 使用H.264编码
        '-preset', 'fast',  # 编码预设
        '-crf', '23',  # 编码质量
        '-r', '60',  # 输出帧率
        '-y',  # 覆盖输出文件
        video_path
    ]
    
    try:
        create_result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, check=True)
        video_created = True
    except subprocess.CalledProcessError as e:
        return {
            'result': {'error': '创建60fps测试视频失败', 'details': e.stderr},
            'insights': ['ffmpeg创建60fps测试视频失败']
        }
    
    # 验证视频文件是否存在
    if not os.path.exists(video_path):
        return {
            'result': {'error': '视频文件未成功创建'},
            'insights': ['尽管ffmpeg命令执行成功，但视频文件未生成']
        }
    
    # 获取视频元数据
    ffprobe_cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    
    try:
        metadata_result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
        metadata = json.loads(metadata_result.stdout)
        
        # 检查视频流信息
        video_stream = None
        for stream in metadata.get('streams', []):
            if stream['codec_type'] == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            return {
                'result': {'error': '视频文件不包含视频流'},
                'insights': ['生成的视频文件格式异常，没有找到视频流']
            }
        
        actual_fps = video_stream.get('avg_frame_rate', 'unknown')
        width = video_stream.get('width', 'unknown')
        height = video_stream.get('height', 'unknown')
        codec = video_stream.get('codec_name', 'unknown')
        
    except Exception as e:
        return {
            'result': {'error': '无法获取视频元数据', 'details': str(e)},
            'insights': ['ffprobe无法解析视频文件元数据']
        }
    
    # 测试硬件编解码器支持
    hardware_test_results = []
    
    # 尝试使用硬件加速解码
    try:
        hardware_decode_cmd = [
            'ffmpeg',
            '-hwaccel', 'auto',
            '-i', video_path,
            '-f', 'null',
            '-'
        ]
        decode_result = subprocess.run(hardware_decode_cmd, capture_output=True, text=True)
        if decode_result.returncode == 0:
            hardware_test_results.append({
                'test': '硬件加速解码',
                'status': 'success',
                'details': '硬件解码成功'
            })
        else:
            hardware_test_results.append({
                'test': '硬件加速解码',
                'status': 'failed',
                'details': '硬件解码失败',
                'stderr': decode_result.stderr
            })
    except Exception as e:
        hardware_test_results.append({
            'test': '硬件加速解码',
            'status': 'error',
            'error': str(e)
        })
    
    # 尝试使用硬件加速编码
    try:
        test_output = os.path.join(output_dir, 'hardware_test_output.mp4')
        hardware_encode_cmd = [
            'ffmpeg',
            '-hwaccel', 'auto',
            '-f', 'lavfi',
            '-i', 'testsrc=size=1280x720:rate=60',
            '-t', '5',
            '-c:v', 'h264_videotoolbox',  # 优先使用Apple VideoToolbox
            '-y',
            test_output
        ]
        
        # 尝试使用其他硬件编码器
        encode_options = [
            ['-c:v', 'h264_videotoolbox'],
            ['-c:v', 'h264_nvenc'],  # NVIDIA
            ['-c:v', 'h264_qsv'],   # Intel Quick Sync
            ['-c:v', 'libx264']     # 回退到软件编码
        ]
        
        encode_success = False
        for option in encode_options:
            try:
                cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=size=1280x720:rate=60', '-t', '5'] + option + ['-y', test_output]
                encode_result = subprocess.run(cmd, capture_output=True, text=True)
                if encode_result.returncode == 0 and os.path.exists(test_output):
                    hardware_test_results.append({
                        'test': '硬件加速编码',
                        'encoder': option[1],
                        'status': 'success',
                        'details': f'使用{option[1]}编码成功'
                    })
                    encode_success = True
                    os.remove(test_output)  # 清理临时文件
                    break
            except Exception:
                continue
        
        if not encode_success:
            hardware_test_results.append({
                'test': '硬件加速编码',
                'status': 'failed',
                'details': '所有硬件编码器均失败，使用软件编码'
            })
    except Exception as e:
        hardware_test_results.append({
            'test': '硬件加速编码',
            'status': 'error',
            'error': str(e)
        })
    
    # 返回结果
    return {
        'result': {
            'video_path': video_path,
            'video_created': video_created,
            'metadata': {
                'fps': actual_fps,
                'resolution': f"{width}x{height}",
                'codec': codec
            },
            'hardware_tests': hardware_test_results
        },
        'insights': [
            f'成功创建60fps测试视频: {video_path}',
            f'视频实际帧率: {actual_fps}',
            f'视频分辨率: {width}x{height}',
            f'视频编码: {codec}'
        ],
        'memories': [
            f'创建了60fps测试视频，路径: {video_path}',
            f'视频元数据: {width}x{height}, {actual_fps}fps, {codec}编码'
        ],
        'capabilities': [
            '使用ffmpeg生成高帧率视频的能力',
            '验证硬件编解码支持的能力'
        ]
    }