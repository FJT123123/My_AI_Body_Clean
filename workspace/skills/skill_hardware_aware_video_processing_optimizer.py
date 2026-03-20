"""
自动生成的技能模块
需求: 硬件感知的视频处理参数验证和自适应调优技能，能够接收视频文件路径，实时评估系统资源约束，并动态生成适合当前硬件条件的视频处理参数
生成时间: 2026-03-19 20:47:44
"""

# skill_name: hardware_aware_video_processing_optimizer

import os
import json
import subprocess
import psutil
import platform
from pathlib import Path

def main(args=None):
    """
    硬件感知的视频处理参数验证和自适应调优技能
    接收视频文件路径，实时评估系统资源约束，并动态生成适合当前硬件条件的视频处理参数
    支持实时系统资源监控和动态调整修复策略优先级和强度
    """
    import json
    
    # 处理不同类型的输入结构
    actual_input = args
    if isinstance(args, dict) and 'input' in args:
        # 从包装结构中提取实际输入
        try:
            actual_input = json.loads(args['input'])
        except (json.JSONDecodeError, TypeError):
            actual_input = args['input'] if isinstance(args['input'], dict) else {}
    
    # 现在处理actual_input
    if isinstance(actual_input, dict):
        args = actual_input
    elif isinstance(actual_input, str):
        # actual_input 是 JSON 字符串
        if actual_input.strip():
            try:
                args = json.loads(actual_input)
            except json.JSONDecodeError:
                # 如果不是有效的JSON， treat as video_path
                args = {'video_path': actual_input}
        else:
            args = {}
    elif actual_input is None:
        args = {}
    else:
        args = {}
    
    # Debug: log args
    print(f"DEBUG: Final args = {args}")
    
    video_path = args.get('video_path', '')
    analyze_video = True
    
    # Debug: print args content
    print(f"DEBUG: args = {args}")
    
    if video_path:
        # 尝试不同的路径解析方式
        paths_to_try = [
            video_path,
            os.path.join(os.getcwd(), video_path),
            os.path.join('/Users/zhufeng/My_AI_Body_副本', video_path)
        ]
        
        actual_path = None
        for path in paths_to_try:
            if os.path.exists(path):
                actual_path = path
                break
        
        if not actual_path:
            return {
                'result': {'error': f'视频文件路径不存在: {video_path}'},
                'insights': ['视频文件路径验证失败'],
                'facts': [],
                'memories': []
            }
        
        video_path = actual_path
    else:
        # 无视频文件模式，使用默认规格进行冲突预测
        analyze_video = False
        default_width = 1920
        default_height = 1080
        default_duration = 60  # 1分钟
        default_codec = 'h264'
    
    # 获取系统资源信息
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    cpu_percent = psutil.cpu_percent(interval=1)
    disk_usage = psutil.disk_usage('/')
    disk_usage_percent = disk_usage.percent / 100.0
    
    # 计算系统负载分数并确定修复策略
    load_score = calculate_system_load_score(cpu_percent/100.0, memory_gb, disk_usage_percent)
    repair_strategy = determine_repair_strategy_priority(load_score)
    
    # 获取GPU信息（如果可用）
    gpu_info = {}
    try:
        # 尝试检测NVIDIA GPU
        nvidia_result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=10)
        if nvidia_result.returncode == 0:
            gpu_info['nvidia'] = nvidia_result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        gpu_info['nvidia'] = 'NVIDIA GPU not available'
    
    if analyze_video:
        # 获取视频文件信息
        try:
            # 使用系统检测到的ffprobe路径
            ffprobe_path = '/opt/homebrew/bin/ffprobe'
            try:
                # 尝试使用which命令找到ffprobe
                which_result = subprocess.run(['which', 'ffprobe'], capture_output=True, text=True)
                if which_result.returncode == 0 and which_result.stdout.strip():
                    ffprobe_path = which_result.stdout.strip()
            except:
                pass
                
            ffprobe_result = subprocess.run([
                ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
            ], capture_output=True, text=True)
            
            if ffprobe_result.returncode == 0:
                video_metadata = json.loads(ffprobe_result.stdout)
                video_stream = None
                audio_stream = None
                
                for stream in video_metadata.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                    elif stream.get('codec_type') == 'audio':
                        audio_stream = stream
                        break
                
                if video_stream:
                    width = int(video_stream.get('width', 0))
                    height = int(video_stream.get('height', 0))
                    duration = float(video_metadata['format'].get('duration', 0))
                    bitrate = int(video_metadata['format'].get('bit_rate', 0))
                    video_codec = video_stream.get('codec_name', 'unknown')
                    
                    # 基于硬件资源和视频特征生成优化参数
                    optimal_params = generate_optimal_params(
                        cpu_count, memory_gb, width, height, duration, bitrate, video_codec, gpu_info
                    )
                    
                    # 预测潜在冲突
                    predicted_conflicts = predict_potential_conflicts(
                        cpu_count, memory_gb, cpu_percent, width, height, duration, video_codec, gpu_info, optimal_params
                    )
                    
                    # 计算健康评分
                    health_score = calculate_health_score(cpu_count, memory_gb, cpu_percent, gpu_info, predicted_conflicts)
                    
                    return {
                        'result': {
                            'video_info': {
                                'width': width,
                                'height': height,
                                'duration': duration,
                                'bitrate': bitrate,
                                'codec': video_codec
                            },
                            'system_info': {
                                'cpu_count': cpu_count,
                                'memory_gb': memory_gb,
                                'cpu_usage': cpu_percent,
                                'disk_usage_percent': disk_usage_percent * 100,
                                'gpu_info': gpu_info
                            },
                            'recommended_params': optimal_params,
                            'repair_strategy': repair_strategy,
                            'load_score': load_score,
                            'predicted_conflicts': predicted_conflicts,
                            'health_score': health_score
                        },
                        'insights': [
                            f'检测到系统CPU核心数: {cpu_count}',
                            f'系统内存: {memory_gb:.2f}GB',
                            f'视频分辨率: {width}x{height}',
                            f'推荐使用参数: {optimal_params["preset"]} 预设，{optimal_params["threads"]} 线程',
                            f'系统健康评分: {health_score}/100',
                            f'检测到 {len(predicted_conflicts)} 个潜在冲突'
                        ],
                        'facts': [
                            ['video_file', 'has_resolution', f'{width}x{height}'],
                            ['system', 'has_cpu_cores', str(cpu_count)],
                            ['system', 'has_memory', f'{memory_gb:.2f}GB'],
                            ['video_processing', 'recommended_threads', str(optimal_params["threads"])],
                            ['system', 'health_score', str(health_score)],
                            ['system', 'predicted_conflicts', str(len(predicted_conflicts))]
                        ],
                        'memories': [
                            f'系统资源配置: {cpu_count}核CPU, {memory_gb:.2f}GB内存',
                            f'视频文件: {width}x{height}分辨率, {duration:.2f}秒时长',
                            f'推荐处理参数: {optimal_params}',
                            f'健康评分: {health_score}/100，冲突数: {len(predicted_conflicts)}'
                        ]
                    }
                else:
                    return {
                        'result': {'error': '无法检测视频流信息'},
                        'insights': ['视频文件中未找到视频流'],
                        'facts': [],
                        'memories': []
                    }
            else:
                return {
                    'result': {'error': 'ffprobe命令执行失败'},
                    'insights': ['视频文件格式可能不支持或ffprobe未安装'],
                    'facts': [],
                    'memories': []
                }
        except subprocess.TimeoutExpired:
            return {
                'result': {'error': 'ffprobe命令执行超时'},
                'insights': ['视频文件可能过大或ffprobe命令异常'],
                'facts': [],
                'memories': []
            }
        except Exception as e:
            return {
                'result': {'error': str(e)},
                'insights': [f'视频分析过程中出现错误: {str(e)}'],
                'facts': [],
                'memories': []
            }
    else:
        # 无视频文件模式 - 使用参数或默认规格进行分析
        input_resolution = args.get('resolution', '1080p')
        duration = args.get('duration', default_duration)
        video_codec = args.get('codec', default_codec)
        hardware_acceleration = args.get('hardware_acceleration', False)
        
        # 解析分辨率
        if input_resolution == '720p':
            width, height = 1280, 720
            resolution_label = '720p'
        elif input_resolution == '1080p':
            width, height = 1920, 1080
            resolution_label = '1080p'
        elif input_resolution == '4K':
            width, height = 3840, 2160
            resolution_label = '4K'
        elif input_resolution == '8K':
            width, height = 7680, 4320
            resolution_label = '8K'
        else:
            # 自定义分辨率格式: "1920x1080"
            try:
                w, h = input_resolution.split('x')
                width, height = int(w), int(h)
                resolution_label = input_resolution
            except:
                width, height = default_width, default_height
                resolution_label = '1080p'
        
        bitrate = 5000000  # 5Mbps for 1080p, adjust based on resolution
        if resolution_label == '4K':
            bitrate = 20000000  # 20Mbps
        elif resolution_label == '8K':
            bitrate = 50000000  # 50Mbps
        elif resolution_label == '720p':
            bitrate = 2500000  # 2.5Mbps
        
        # 基于硬件资源和默认视频特征生成优化参数
        optimal_params = generate_optimal_params(
            cpu_count, memory_gb, width, height, duration, bitrate, video_codec, gpu_info
        )
        
        # 预测潜在冲突
        predicted_conflicts = predict_potential_conflicts(
            cpu_count, memory_gb, cpu_percent, width, height, duration, video_codec, gpu_info, optimal_params
        )
        
        # 计算健康评分
        health_score = calculate_health_score(cpu_count, memory_gb, cpu_percent, gpu_info, predicted_conflicts)
        
        # 检测硬件编解码器
        hardware_codecs = []
        try:
            ffmpeg_encoders_result = subprocess.run(['ffmpeg', '-encoders'], 
                                                  capture_output=True, text=True, timeout=10)
            encoders_output = ffmpeg_encoders_result.stdout
            
            codec_mapping = {
                'h264_videotoolbox': 'H.264 (VideoToolbox)',
                'hevc_videotoolbox': 'HEVC (VideoToolbox)',
                'h264_nvenc': 'H.264 (NVENC)',
                'hevc_nvenc': 'HEVC (NVENC)',
                'h264_qsv': 'H.264 (QuickSync)',
                'hevc_qsv': 'HEVC (QuickSync)'
            }
            
            for codec_key, codec_name in codec_mapping.items():
                if codec_key in encoders_output:
                    hardware_codecs.append(codec_name)
        except:
            pass
        
        return {
            'result': {
                'system_info': {
                    'cpu_count': cpu_count,
                    'memory_gb': memory_gb,
                    'cpu_usage': cpu_percent,
                    'disk_usage_percent': disk_usage_percent * 100,
                    'gpu_info': gpu_info,
                    'hardware_codecs': hardware_codecs
                },
                'video_spec': {
                    'width': width,
                    'height': height,
                    'duration': duration,
                    'codec': video_codec,
                    'bitrate': bitrate,
                    'resolution_label': resolution_label
                },
                'recommended_params': optimal_params,
                'repair_strategy': repair_strategy,
                'load_score': load_score,
                'predicted_conflicts': predicted_conflicts,
                'health_score': health_score
            },
            'insights': [
                f'检测到系统CPU核心数: {cpu_count}',
                f'系统内存: {memory_gb:.2f}GB',
                f'视频规格: {width}x{height}, {duration}秒, {video_codec}',
                f'推荐使用参数: {optimal_params["preset"]} 预设，{optimal_params["threads"]} 线程',
                f'系统健康评分: {health_score}/100',
                f'检测到 {len(predicted_conflicts)} 个潜在冲突',
                f'可用硬件编解码器: {", ".join(hardware_codecs) if hardware_codecs else "无"}'
            ],
            'facts': [
                ['system', 'has_cpu_cores', str(cpu_count)],
                ['system', 'has_memory', f'{memory_gb:.2f}GB'],
                ['system', 'health_score', str(health_score)],
                ['system', 'predicted_conflicts', str(len(predicted_conflicts))],
                ['system', 'hardware_codecs_available', str(len(hardware_codecs))],
                ['video_spec', 'resolution', f'{width}x{height}'],
                ['video_spec', 'duration', str(duration)]
            ],
            'memories': [
                f'系统资源配置: {cpu_count}核CPU, {memory_gb:.2f}GB内存',
                f'视频规格: {width}x{height}, {duration}秒, {video_codec}',
                f'推荐处理参数: {optimal_params}',
                f'健康评分: {health_score}/100，冲突数: {len(predicted_conflicts)}',
                f'硬件编解码器: {", ".join(hardware_codecs) if hardware_codecs else "无"}'
            ]
        }

def generate_optimal_params(cpu_count, memory_gb, width, height, duration, bitrate, video_codec, gpu_info):
    """
    基于硬件资源和视频特征生成优化参数
    """
    # 根据CPU核心数确定使用线程数
    if cpu_count >= 8:
        threads = min(cpu_count - 2, 16)  # 保留2个核心处理其他任务，最多16线程
    elif cpu_count >= 4:
        threads = min(cpu_count - 1, 8)  # 保留1个核心处理其他任务
    else:
        threads = max(1, cpu_count)  # 至少使用1个线程
    
    # 根据视频分辨率和内存大小确定预设
    resolution = width * height
    if memory_gb >= 16 and resolution >= 1920 * 1080:
        preset = 'medium'  # 高性能系统使用中等预设以平衡速度和质量
    elif memory_gb >= 8:
        preset = 'fast'  # 中等性能系统使用快速预设
    else:
        preset = 'ultrafast'  # 低性能系统使用超快预设
    
    # 根据GPU可用性确定是否使用硬件加速
    hwaccel = False
    encoder = 'libx264'
    if 'nvidia' in gpu_info and gpu_info['nvidia'] and 'not available' not in gpu_info['nvidia']:
        hwaccel = True
        encoder = 'h264_nvenc'  # 使用NVIDIA硬件编码器
    
    # 根据视频时长和比特率确定缓冲区大小
    bufsize = max(1000, bitrate // 1000)  # 转换为kbps
    maxrate = max(1500, bufsize * 1.5)
    
    return {
        'threads': threads,
        'preset': preset,
        'hwaccel': hwaccel,
        'encoder': encoder,
        'bufsize': bufsize,
        'maxrate': maxrate,
        'cpu_usage_threshold': 80 if cpu_count > 4 else 70
    }

def predict_potential_conflicts(cpu_count, memory_gb, cpu_percent, width, height, duration, video_codec, gpu_info, optimal_params):
    """预测潜在冲突"""
    conflicts = []
    
    # 内存不足冲突
    resolution = width * height
    estimated_memory_needed_gb = (resolution / (1920 * 1080)) * (duration / 60) * 2  # 简化估算
    if estimated_memory_needed_gb > memory_gb * 0.8:
        conflicts.append({
            'type': 'memory_insufficient',
            'severity': 'high',
            'message': f'预计需要 {estimated_memory_needed_gb:.2f}GB 内存，但系统只有 {memory_gb:.2f}GB',
            'recommendation': '降低分辨率或缩短视频时长'
        })
    
    # CPU负载过高冲突
    if cpu_percent > 80:
        conflicts.append({
            'type': 'high_cpu_load',
            'severity': 'medium',
            'message': f'当前CPU使用率 {cpu_percent}%，可能影响视频处理性能',
            'recommendation': '等待系统负载降低或减少并行任务'
        })
    
    # 硬件加速不可用冲突
    if optimal_params['hwaccel'] and ('nvidia' not in gpu_info or 'not available' in gpu_info.get('nvidia', '')):
        conflicts.append({
            'type': 'hardware_acceleration_unavailable',
            'severity': 'medium',
            'message': '推荐使用硬件加速但GPU不可用',
            'recommendation': '禁用硬件加速或使用软件编码'
        })
    
    # 高分辨率处理冲突
    if resolution >= 3840 * 2160 and cpu_count < 8:  # 4K视频需要至少8核CPU
        conflicts.append({
            'type': 'insufficient_cpu_for_4k',
            'severity': 'high',
            'message': f'4K视频处理需要更多CPU核心，当前只有 {cpu_count} 核',
            'recommendation': '降低分辨率或使用更高效的编解码器'
        })
    
    return conflicts

def calculate_system_load_score(cpu_percent, memory_gb, disk_usage_percent):
    """计算综合系统负载分数 (0.0-1.0)"""
    # 获取总内存GB
    total_memory_gb = psutil.virtual_memory().total / (1024**3)
    memory_percent = (total_memory_gb - memory_gb) / total_memory_gb
    
    # 加权平均，可以根据需要调整权重
    cpu_weight = 0.4
    memory_weight = 0.4
    disk_weight = 0.2
    
    load_score = (
        cpu_percent * cpu_weight +
        memory_percent * memory_weight +
        disk_usage_percent * disk_weight
    )
    
    return min(load_score, 1.0)

def determine_repair_strategy_priority(load_score):
    """根据系统负载分数确定修复策略优先级和强度"""
    if load_score > 0.8:
        # 高负载：降低优先级和强度，减少资源消耗
        return {
            "priority": "low",
            "intensity": "conservative",
            "max_threads": 1,
            "batch_size": 1,
            "quality_target": "acceptable"
        }
    elif load_score > 0.6:
        # 中等负载：保持平衡
        return {
            "priority": "normal",
            "intensity": "balanced",
            "max_threads": 2,
            "batch_size": 2,
            "quality_target": "good"
        }
    else:
        # 低负载：提高优先级和强度，充分利用资源
        return {
            "priority": "high",
            "intensity": "aggressive",
            "max_threads": 4,
            "batch_size": 4,
            "quality_target": "excellent"
        }

def calculate_health_score(cpu_count, memory_gb, cpu_percent, gpu_info, predicted_conflicts):
    """计算健康评分"""
    base_score = 100
    
    # CPU核心数评分
    if cpu_count >= 8:
        cpu_score = 25
    elif cpu_count >= 4:
        cpu_score = 20
    else:
        cpu_score = 10
    
    # 内存评分
    if memory_gb >= 16:
        memory_score = 25
    elif memory_gb >= 8:
        memory_score = 20
    else:
        memory_score = 10
    
    # CPU负载评分
    if cpu_percent < 50:
        load_score = 25
    elif cpu_percent < 80:
        load_score = 15
    else:
        load_score = 5
    
    # GPU可用性评分
    if 'nvidia' in gpu_info and 'not available' not in gpu_info.get('nvidia', ''):
        gpu_score = 25
    else:
        gpu_score = 10
    
    # 冲突惩罚
    conflict_penalty = 0
    for conflict in predicted_conflicts:
        if conflict['severity'] == 'critical':
            conflict_penalty += 30
        elif conflict['severity'] == 'high':
            conflict_penalty += 20
        elif conflict['severity'] == 'medium':
            conflict_penalty += 10
    
    total_score = min(100, cpu_score + memory_score + load_score + gpu_score - conflict_penalty)
    return max(0, total_score)