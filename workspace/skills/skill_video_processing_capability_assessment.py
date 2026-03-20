"""
自动生成的技能模块
需求: 实时评估系统视频处理能力的技能，包括硬件检测、编解码性能测试、可用参数范围评估，并输出结构化结果用于参数契约验证
生成时间: 2026-03-19 20:24:52
"""

# skill_name: video_processing_capability_assessment

import subprocess
import os
import json
import platform
import time
import hashlib
from typing import Dict, List, Any

# 缓存文件路径
DEPENDENCY_CACHE_FILE = os.path.join(os.path.dirname(__file__), '../dependency_cache.json')

# 尝试导入Metal编解码器支持探测能力
try:
    from capabilities.metal_video_codec_support_capability import detect_metal_video_codec_support
    METAL_CAPABILITY_AVAILABLE = True
except ImportError:
    METAL_CAPABILITY_AVAILABLE = False


def get_gpu_info():
    """获取GPU信息"""
    gpu_info = {'vendor': None, 'model': None, 'cuda_support': False, 'opencl_support': False}
    
    # 尝试检测NVIDIA GPU
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            gpu_info['vendor'] = 'NVIDIA'
            gpu_info['model'] = result.stdout.strip().split('\n')[0].split(',')[0]
            gpu_info['cuda_support'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 尝试检测AMD GPU
    try:
        result = subprocess.run(['clinfo'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if 'AMD' in result.stdout:
                gpu_info['vendor'] = 'AMD'
                gpu_info['opencl_support'] = True
        # 尝试获取AMD GPU型号
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Device Type' in line and 'GPU' in line:
                gpu_info['model'] = 'AMD GPU'
                break
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 尝试检测Intel GPU
    try:
        result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if 'Intel' in result.stdout and 'VGA' in result.stdout:
                gpu_info['vendor'] = 'Intel'
                gpu_info['opencl_support'] = True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return gpu_info


def get_cpu_info():
    """获取CPU信息"""
    cpu_info = {
        'architecture': platform.machine(),
        'cores': os.cpu_count(),
        'processor': platform.processor()
    }
    return cpu_info


def test_video_codec_performance():
    """测试视频编解码性能"""
    # 创建临时测试视频
    test_video_result = {'encoding_performance': {}, 'decoding_performance': {}}
    
    try:
        # 生成10秒测试视频
        subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=1920x1080:rate=30', 
                        '-t', '10', '-c:v', 'libx264', '-preset', 'fast', 'temp_test.mp4'], 
                       capture_output=True, timeout=30)
        
        # 测试不同编码器的性能
        codecs = [
            ('libx264', {'preset': 'fast', 'crf': '23'}),
            ('libx265', {'preset': 'fast', 'crf': '28'}),
            ('libvpx-vp9', {'crf': '30', 'b:v': '0'}),
            ('libaom-av1', {'cpu-used': '2', 'crf': '30'})
        ]
        
        for codec, params in codecs:
            try:
                start_time = time.time()
                cmd = ['ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=1920x1080:rate=30', 
                       '-t', '5', '-c:v', codec]
                for param, value in params.items():
                    cmd.extend(['-' + param, value])
                cmd.append(f'temp_{codec}.mp4')
                
                subprocess.run(cmd, capture_output=True, timeout=45)
                end_time = time.time()
                
                test_video_result['encoding_performance'][codec] = {
                    'encoding_time': round(end_time - start_time, 2),
                    'success': True
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                test_video_result['encoding_performance'][codec] = {
                    'encoding_time': None,
                    'success': False
                }
        
        # 测试解码性能
        for codec in ['h264', 'hevc', 'vp9', 'av1']:
            try:
                start_time = time.time()
                result = subprocess.run(['ffmpeg', '-i', 'temp_test.mp4', '-f', 'null', '-'], 
                                      capture_output=True, timeout=30)
                end_time = time.time()
                
                test_video_result['decoding_performance'][codec] = {
                    'decoding_time': round(end_time - start_time, 2),
                    'success': result.returncode == 0
                }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                test_video_result['decoding_performance'][codec] = {
                    'decoding_time': None,
                    'success': False
                }
        
        # 清理临时文件
        for f in os.listdir('.'):
            if f.startswith('temp_') and f.endswith(('.mp4', '.mkv')):
                os.remove(f)
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # 如果ffmpeg不可用，跳过测试
        pass
    
    return test_video_result


def get_available_video_params():
    """获取可用视频参数范围"""
    available_params = {
        'resolution_support': [],
        'framerate_support': [],
        'codec_support': [],
        'hardware_acceleration': []
    }
    
    try:
        # 检查硬件加速支持
        hw_accels = ['cuda', 'opencl', 'vaapi', 'vdpau', 'dxva2', 'qsv', 'videotoolbox']
        for accel in hw_accels:
            try:
                result = subprocess.run(['ffmpeg', '-hwaccels'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and accel in result.stdout:
                    available_params['hardware_acceleration'].append(accel)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        # 检查编解码器支持（包括Apple Silicon硬件加速编解码器）
        codecs = ['h264', 'hevc', 'vp8', 'vp9', 'av1', 'mpeg4', 'prores']
        hardware_codecs = ['h264_videotoolbox', 'hevc_videotoolbox']
        
        # 检查软件编解码器
        try:
            encoders_result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, timeout=10)
            if encoders_result.returncode == 0:
                for codec in codecs:
                    if codec in encoders_result.stdout:
                        available_params['codec_support'].append(codec)
                
                # 特别检查Apple Silicon硬件加速编解码器
                for hw_codec in hardware_codecs:
                    if hw_codec in encoders_result.stdout:
                        available_params['codec_support'].append(hw_codec)
                        # 如果检测到videotoolbox编解码器，确保videotoolbox在硬件加速列表中
                        if 'videotoolbox' not in available_params['hardware_acceleration']:
                            available_params['hardware_acceleration'].append('videotoolbox')
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    
    except Exception:
        # 如果检测失败，使用空列表
        pass
    
    # 根据CPU核心数估算分辨率支持
    cpu_cores = os.cpu_count()
    if cpu_cores:
        if cpu_cores >= 8:
            available_params['resolution_support'] = ['4K', '1080p', '720p', '480p']
        elif cpu_cores >= 4:
            available_params['resolution_support'] = ['1080p', '720p', '480p']
        else:
            available_params['resolution_support'] = ['720p', '480p']
    
    # 帧率支持
    if cpu_cores:
        if cpu_cores >= 8:
            available_params['framerate_support'] = [30, 60, 120]
        elif cpu_cores >= 4:
            available_params['framerate_support'] = [30, 60]
        else:
            available_params['framerate_support'] = [30]
    
    return available_params


def _load_cache():
    """加载依赖缓存"""
    try:
        if os.path.exists(DEPENDENCY_CACHE_FILE):
            with open(DEPENDENCY_CACHE_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {'dependencies': {}, 'last_updated': None}

def _save_cache(cache_data):
    """保存依赖缓存"""
    try:
        os.makedirs(os.path.dirname(DEPENDENCY_CACHE_FILE), exist_ok=True)
        with open(DEPENDENCY_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except IOError:
        pass  # 缓存失败不影响主要功能

def _get_cache_key():
    """生成缓存键"""
    system_info = f"{platform.system()}:{platform.machine()}:{platform.platform()}"
    return hashlib.md5(system_info.encode()).hexdigest()

def _is_cache_valid(cache_entry, max_age_seconds=3600):
    """检查缓存是否有效（默认1小时）"""
    if not cache_entry or 'timestamp' not in cache_entry:
        return False
    
    import datetime
    timestamp = datetime.datetime.fromisoformat(cache_entry['timestamp'])
    return datetime.datetime.now() - timestamp < datetime.timedelta(seconds=max_age_seconds)

def main(args=None):
    """
    实时评估系统视频处理能力的技能，包括硬件检测、编解码性能测试、可用参数范围评估，并输出结构化结果用于参数契约验证
    
    返回包含系统视频处理能力的详细信息，包括硬件配置、编解码性能、支持参数范围等
    """
    args = args or {}
    
    # 检查缓存
    force_refresh = args.get('force_refresh', False)
    if not force_refresh:
        cache = _load_cache()
        cache_key = _get_cache_key()
        if cache_key in cache.get('dependencies', {}):
            cache_entry = cache['dependencies'][cache_key]
            if _is_cache_valid(cache_entry):
                # 返回缓存结果
                return {
                    'result': cache_entry['result'],
                    'insights': cache_entry.get('insights', []),
                    'facts': cache_entry.get('facts', []),
                    'capabilities': cache_entry.get('capabilities', []),
                    'next_skills': cache_entry.get('next_skills', [])
                }
    
    # 获取系统信息
    system_info = {
        'os': platform.system(),
        'platform': platform.platform(),
        'cpu': get_cpu_info(),
        'gpu': get_gpu_info()
    }
    
    # 测试视频编解码性能
    performance_result = test_video_codec_performance()
    
    # 获取可用参数
    available_params = get_available_video_params()
    
    # 综合评估结果
    capability_assessment = {
        'system_info': system_info,
        'encoding_performance': performance_result['encoding_performance'],
        'decoding_performance': performance_result['decoding_performance'],
        'available_params': available_params,
        'timestamp': time.time(),
        'assessment_summary': {
            'gpu_acceleration_available': (
                system_info['gpu']['cuda_support'] or 
                system_info['gpu']['opencl_support'] or
                bool(available_params['hardware_acceleration'])
            ),
            'hardware_encoders': len(available_params['hardware_acceleration']),
            'supported_codecs': len(available_params['codec_support']),
            'max_resolution': available_params['resolution_support'][0] if available_params['resolution_support'] else 'Unknown'
        }
    }
    
    # 如果在Apple Silicon平台上且Metal能力模块可用，进行更详细的Metal编解码器探测
    if (platform.system() == "Darwin" and platform.machine() == "arm64" and 
        METAL_CAPABILITY_AVAILABLE):
        metal_support = detect_metal_video_codec_support()
        capability_assessment['metal_video_codec_support'] = metal_support
        
        # 更新硬件加速信息
        if metal_support.get('metal_codecs'):
            # 确保videotoolbox在硬件加速列表中
            if 'videotoolbox' not in available_params['hardware_acceleration']:
                available_params['hardware_acceleration'].append('videotoolbox')
            
            # 添加Metal编解码器到支持的编解码器列表
            for codec in metal_support['metal_codecs']:
                if codec not in available_params['codec_support']:
                    available_params['codec_support'].append(codec)
            
            # 更新评估摘要
            capability_assessment['assessment_summary']['gpu_acceleration_available'] = True
            capability_assessment['assessment_summary']['hardware_encoders'] = len(available_params['hardware_acceleration'])
            capability_assessment['assessment_summary']['supported_codecs'] = len(available_params['codec_support'])
    
    # 分析结果
    insights = []
    if system_info['gpu']['cuda_support']:
        insights.append(f"系统检测到NVIDIA GPU: {system_info['gpu']['model']}，支持CUDA加速")
    if available_params['hardware_acceleration']:
        insights.append(f"系统支持硬件加速: {', '.join(available_params['hardware_acceleration'])}")
    if available_params['codec_support']:
        insights.append(f"系统支持的编码器: {', '.join(available_params['codec_support'])}")
    
    # 添加Apple Silicon Metal编解码器支持的洞察
    if (platform.system() == "Darwin" and platform.machine() == "arm64" and 
        capability_assessment.get('metal_video_codec_support')):
        metal_info = capability_assessment['metal_video_codec_support']
        if metal_info.get('metal_codecs'):
            insights.append(f"Apple Silicon Metal编解码器支持: {', '.join(metal_info['metal_codecs'])}")
        else:
            insights.append("Apple Silicon Metal编解码器: 未检测到支持的编解码器")
    
    # 生成能力描述
    capabilities = [
        f"视频处理能力: {capability_assessment['assessment_summary']['max_resolution']} @ {available_params['framerate_support'][-1] if available_params['framerate_support'] else 30}fps",
        f"硬件加速: {'支持' if capability_assessment['assessment_summary']['gpu_acceleration_available'] else '不支持'}",
        f"可用编码器: {len(available_params['codec_support'])} 种",
        f"硬件加速支持: {len(available_params['hardware_acceleration'])} 种"
    ]
    
    # 添加Apple Silicon特定的能力描述
    if (platform.system() == "Darwin" and platform.machine() == "arm64" and 
        capability_assessment.get('metal_video_codec_support')):
        metal_info = capability_assessment['metal_video_codec_support']
        metal_codecs_count = len(metal_info.get('metal_codecs', []))
        capabilities.append(f"Apple Silicon Metal编解码器支持: {metal_codecs_count} 种")
    
    # 生成知识三元组
    facts = [
        ["system_video_capability", "has_cpu_cores", str(system_info['cpu']['cores'])],
        ["system_video_capability", "has_gpu_vendor", system_info['gpu']['vendor'] or 'None'],
        ["system_video_capability", "supports_hardware_acceleration", str(bool(available_params['hardware_acceleration']))],
        ["system_video_capability", "max_resolution_support", capability_assessment['assessment_summary']['max_resolution']]
    ]
    
    # 生成后续建议
    next_skills = []
    if not available_params['hardware_acceleration']:
        next_skills.append('install_video_acceleration_libraries')
    
    # 清理临时文件
    try:
        for f in os.listdir('.'):
            if f.startswith('temp_') and f.endswith(('.mp4', '.mkv')):
                os.remove(f)
    except:
        pass
    
    # 保存到缓存
    cache = _load_cache()
    cache_key = _get_cache_key()
    cache_entry = {
        'result': capability_assessment,
        'insights': insights,
        'facts': facts,
        'capabilities': capabilities,
        'next_skills': next_skills,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    if 'dependencies' not in cache:
        cache['dependencies'] = {}
    cache['dependencies'][cache_key] = cache_entry
    cache['last_updated'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    _save_cache(cache)
    
    return {
        'result': capability_assessment,
        'insights': insights,
        'facts': facts,
        'capabilities': capabilities,
        'next_skills': next_skills
    }