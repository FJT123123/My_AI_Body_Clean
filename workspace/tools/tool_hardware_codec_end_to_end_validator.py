# tool_name: hardware_codec_end_to_end_validator
from langchain.tools import tool
import subprocess
import json
import os
import tempfile
import shutil
from typing import Dict, Any, List

def detect_hardware_codecs() -> Dict[str, Any]:
    """检测系统支持的硬件编解码器"""
    try:
        # 检测 videotoolbox (macOS)
        result = subprocess.run(['ffmpeg', '-encoders'], 
                              capture_output=True, text=True, check=True)
        encoders = result.stdout
        
        hardware_encoders = []
        if 'h264_videotoolbox' in encoders:
            hardware_encoders.append('h264_videotoolbox')
        if 'hevc_videotoolbox' in encoders:
            hardware_encoders.append('hevc_videotoolbox')
            
        # 检测其他平台的硬件加速
        if 'h264_nvenc' in encoders:
            hardware_encoders.append('h264_nvenc')
        if 'hevc_nvenc' in encoders:
            hardware_encoders.append('hevc_nvenc')
        if 'h264_qsv' in encoders:
            hardware_encoders.append('h264_qsv')
        if 'hevc_qsv' in encoders:
            hardware_encoders.append('hevc_qsv')
            
        return {
            'hardware_encoders': hardware_encoders,
            'success': True
        }
    except Exception as e:
        return {
            'hardware_encoders': [],
            'success': False,
            'error': str(e)
        }

def create_test_video(width: int = 1920, height: int = 1080, duration: int = 5) -> str:
    """创建测试视频"""
    temp_dir = tempfile.mkdtemp()
    test_video = os.path.join(temp_dir, 'test_input.mp4')
    
    cmd = [
        'ffmpeg', '-f', 'lavfi',
        '-i', f'testsrc=size={width}x{height}:duration={duration}:rate=30',
        '-f', 'lavfi',
        '-i', 'sine=frequency=1000:duration=5',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-y', test_video
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return test_video
    except Exception as e:
        raise RuntimeError(f"Failed to create test video: {e}")

def test_hardware_encoding(input_video: str, encoder: str) -> Dict[str, Any]:
    """测试硬件编码器"""
    output_video = input_video.replace('.mp4', f'_encoded_with_{encoder}.mp4')
    
    cmd = [
        'ffmpeg', '-i', input_video,
        '-c:v', encoder,
        '-c:a', 'copy',
        '-y', output_video
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        success = result.returncode == 0
        
        # 验证输出文件
        if success and os.path.exists(output_video):
            # 获取输出文件信息
            info_cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
                       '-show_format', '-show_streams', output_video]
            info_result = subprocess.run(info_cmd, capture_output=True, text=True)
            if info_result.returncode == 0:
                video_info = json.loads(info_result.stdout)
                return {
                    'success': True,
                    'output_file': output_video,
                    'video_info': video_info,
                    'encoder_used': encoder
                }
        
        return {
            'success': False,
            'error': result.stderr if result.stderr else 'Unknown error',
            'encoder_used': encoder
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Encoding timeout',
            'encoder_used': encoder
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'encoder_used': encoder
        }

def cleanup_temp_files(files: List[str]):
    """清理临时文件"""
    for file_path in files:
        try:
            if os.path.exists(file_path):
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
        except Exception:
            pass

@tool
def hardware_codec_end_to_end_validator(input_args: str = "") -> Dict[str, Any]:
    """
    硬件编解码器端到端验证工具
    
    用于实际测试系统探测到的硬件编解码器是否能正常工作。
    该工具将创建测试视频，使用检测到的硬件编解码器进行编码，并验证输出结果。
    
    Args:
        input_args (str): JSON字符串，包含以下可选参数:
            - resolution (str): 测试分辨率，可选 '720p', '1080p', '4K' (默认 '1080p')
            - duration (int): 测试视频持续时间，单位秒 (默认 5)
    
    Returns:
        dict: 包含测试结果、见解、事实和记忆的字典
            - result: 包含检测到的硬件编解码器、编码测试结果和总体成功状态
            - insights: 包含检测结果和测试过程的见解
            - facts: 包含硬件编码器测试结果的事实列表
            - memories: 包含测试过程记忆的列表
    """
    # 解析输入参数
    params = {}
    if input_args:
        try:
            import json as json_lib
            params = json_lib.loads(input_args)
        except:
            pass
    
    test_resolution = params.get('resolution', '1080p')
    resolutions = {
        '720p': (1280, 720),
        '1080p': (1920, 1080),
        '4K': (3840, 2160)
    }
    
    width, height = resolutions.get(test_resolution, (1920, 1080))
    duration = params.get('duration', 5)
    
    results = {
        'detected_hardware_codecs': [],
        'encoding_tests': [],
        'overall_success': False
    }
    
    insights = []
    facts = []
    memories = []
    
    # 检测硬件编解码器
    detection_result = detect_hardware_codecs()
    results['detected_hardware_codecs'] = detection_result['hardware_encoders']
    
    if not detection_result['hardware_encoders']:
        insights.append("未检测到硬件编解码器支持")
        results['overall_success'] = False
        return {
            'result': results,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
    
    insights.append(f"检测到硬件编解码器: {', '.join(detection_result['hardware_encoders'])}")
    
    # 创建测试视频
    try:
        test_video = create_test_video(width, height, duration)
        temp_files = [os.path.dirname(test_video)]
    except Exception as e:
        return {
            'result': {'error': f'Failed to create test video: {e}'},
            'insights': ['无法创建测试视频'],
            'facts': [],
            'memories': []
        }
    
    # 测试每个硬件编码器
    all_success = True
    for encoder in detection_result['hardware_encoders']:
        test_result = test_hardware_encoding(test_video, encoder)
        results['encoding_tests'].append(test_result)
        
        if test_result['success']:
            insights.append(f"硬件编码器 {encoder} 测试成功")
            facts.append([encoder, "hardware_encoding_test", "success"])
            memories.append(f"Hardware codec {encoder} validated successfully")
        else:
            insights.append(f"硬件编码器 {encoder} 测试失败: {test_result.get('error', 'Unknown error')}")
            facts.append([encoder, "hardware_encoding_test", "failed"])
            all_success = False
    
    results['overall_success'] = all_success
    
    # 清理临时文件
    cleanup_temp_files(temp_files)
    
    return {
        'result': results,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }