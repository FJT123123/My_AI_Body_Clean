"""
端到端视频物理语义验证工作流
接收视频文件路径和可选的系统能力评估结果，自动提取元数据并进行基于实际硬件能力的物理约束验证

参数契约:
- video_path (str, required): 视频文件路径
- system_capabilities (dict, optional): 系统视频处理能力评估结果

返回值:
- metadata: 原始视频元数据
- validation: 物理约束验证结果（基于实际硬件能力）
- summary: 综合报告
"""
# skill_name: video_physics_validation_workflow

import json
import os
import subprocess
import math

# 导入系统能力集成补丁
from workspace.patches.video_capability_integration_patch import integrate_system_capabilities

# 导入参数契约统一验证能力
try:
    from capabilities.video_parameter_contract_validator_capability import unified_parameter_parser, validate_parameter_contract, generate_parameter_error_info
except ImportError:
    # 备用导入路径
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from capabilities.video_parameter_contract_validator_capability import unified_parameter_parser, validate_parameter_contract, generate_parameter_error_info

def main(input_args=None):
    """
    端到端视频物理语义验证工作流
    
    参数:
        input_args: 包含video_path字段的字典或JSON字符串
        
    返回:
        包含完整验证报告的结构化字典
    """
    # 处理 run_skill 的实际参数包装格式
    if isinstance(input_args, dict) and 'input' in input_args:
        # run_skill 会将输入包装在 'input' 键中
        actual_input_str = input_args['input']
        try:
            actual_input = json.loads(actual_input_str)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，尝试直接使用
            actual_input = actual_input_str if isinstance(actual_input_str, dict) else {}
    else:
        # 直接使用输入
        actual_input = input_args if isinstance(input_args, dict) else {}
    
    # 使用统一参数解析器进行二次验证和标准化
    parse_result = unified_parameter_parser(actual_input)
    
    if parse_result["status"] == "error":
        return {
            'result': {'error': f'参数解析失败: {parse_result.get("error", "未知错误")}'},
            'insights': ['参数解析失败，请检查输入格式'],
            'facts': [],
            'memories': []
        }
    
    actual_input = parse_result["parsed_params"]
    
    # 定义参数契约
    parameter_contract = {
        "required": ["video_path"],
        "optional": ["system_capabilities"],
        "types": {
            "video_path": "string",
            "system_capabilities": "object"
        }
    }
    
    # 验证参数契约
    validation_result = validate_parameter_contract(actual_input, parameter_contract)
    
    if validation_result["status"] != "valid":
        error_info = generate_parameter_error_info(actual_input, parameter_contract)
        return {
            'result': {'error': error_info.get('error_message', '参数验证失败')},
            'insights': [f'参数验证失败: {"; ".join(validation_result.get("errors", ["未知错误"]))}'],
            'facts': [],
            'memories': []
        }
    
    video_path = actual_input.get('video_path', '')
    system_capabilities = actual_input.get('system_capabilities', None)
    
    if not video_path:
        return {
            'result': {'error': '缺少video_path参数'},
            'insights': ['必须提供视频文件路径'],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': ['指定的视频文件路径不存在'],
            'facts': [],
            'memories': []
        }
    
    # 第一步：提取视频元数据
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
        ], capture_output=True, text=True, check=True)
        
        metadata_raw = json.loads(result.stdout)
        
        # 提取视频流信息
        video_stream = None
        audio_stream = None
        
        for stream in metadata_raw.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        for stream in metadata_raw.get('streams', []):
            if stream.get('codec_type') == 'audio':
                audio_stream = stream
                break
        
        metadata = {
            'file_path': video_path,
            'duration': float(metadata_raw['format'].get('duration', 0)),
            'size_bytes': int(metadata_raw['format'].get('size', 0)),
            'format_name': metadata_raw['format'].get('format_name', ''),
            'bit_rate': int(metadata_raw['format'].get('bit_rate', 0)),
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
        
    except Exception as e:
        return {
            'result': {'error': f'元数据分析失败: {str(e)}'},
            'insights': ['无法提取视频元数据'],
            'facts': [],
            'memories': []
        }
    
    # 第二步：物理约束验证（内联实现）
    video_metadata = {
        'duration': metadata['duration'],
        'width': metadata['video']['width'],
        'height': metadata['video']['height'],
        'avg_frame_rate': metadata['video']['avg_frame_rate'],
        'r_frame_rate': metadata['video']['r_frame_rate'],
        'bit_rate': metadata['video']['bit_rate'],
        'codec_name': metadata['video']['codec_name'],
        'pix_fmt': metadata['video']['pix_fmt'],
        'file_size': metadata['size_bytes'],
        'audio_stream': metadata['audio']
    }
    
    # 验证视频参数的物理约束
    insights = []
    violations = []
    
    # 如果提供了系统能力评估结果，动态调整验证约束
    dynamic_constraints = {
        'max_width': 16384,
        'max_height': 16384,
        'supported_codecs': ['h264', 'h265', 'hevc', 'vp8', 'vp9', 'av1', 'mpeg4', 'prores'],
        'max_framerate': 240
    }
    
    if system_capabilities:
        try:
            constraints = integrate_system_capabilities(video_metadata, system_capabilities)
            dynamic_constraints['max_width'], dynamic_constraints['max_height'] = constraints['max_resolution']
            dynamic_constraints['supported_codecs'] = constraints['supported_codecs']
            dynamic_constraints['max_framerate'] = constraints['max_framerate']
            insights.append(f"使用动态硬件约束: 最大分辨率 {dynamic_constraints['max_width']}x{dynamic_constraints['max_height']}, 最大帧率 {dynamic_constraints['max_framerate']}fps")
        except Exception as e:
            insights.append(f"系统能力集成失败: {str(e)}，使用默认约束")
    
    # 检查时间轴约束
    duration = float(video_metadata.get('duration', 0))
    avg_frame_rate_str = video_metadata.get('avg_frame_rate', '0/1')
    
    # 解析帧率（可能是字符串如"30/1"或数字）
    try:
        if isinstance(avg_frame_rate_str, str) and '/' in avg_frame_rate_str:
            numerator, denominator = avg_frame_rate_str.split('/')
            avg_frame_rate = float(numerator) / float(denominator)
        else:
            avg_frame_rate = float(avg_frame_rate_str)
    except (ValueError, ZeroDivisionError):
        avg_frame_rate = 0.0
    
    # 检查空间分辨率约束
    width = int(video_metadata.get('width', 0))
    height = int(video_metadata.get('height', 0))
    if width <= 0 or height <= 0:
        violations.append(f"无效分辨率: {width}x{height}")
    elif width > dynamic_constraints['max_width'] or height > dynamic_constraints['max_height']:
        violations.append(f"分辨率超出系统硬件能力: {width}x{height} (最大支持 {dynamic_constraints['max_width']}x{dynamic_constraints['max_height']})")
    elif width > dynamic_constraints['max_width'] * 0.5 or height > dynamic_constraints['max_height'] * 0.5:
        insights.append(f"高分辨率: {width}x{height} (接近系统极限 {dynamic_constraints['max_width']}x{dynamic_constraints['max_height']})")
    
    # 检查码率约束
    bit_rate = int(video_metadata.get('bit_rate', 0))
    if bit_rate < 0:
        violations.append(f"无效码率: {bit_rate} bps")
    elif bit_rate > 100000000:  # 100Mbps
        violations.append(f"码率过高: {bit_rate} bps (超出常规硬件处理能力)")
    elif bit_rate > 50000000:  # 50Mbps
        insights.append(f"高码率: {bit_rate} bps")
    
    # 检查色彩深度约束
    pixel_format = video_metadata.get('pix_fmt', '')
    if pixel_format:
        if pixel_format in ['yuv420p10le', 'yuv422p10le', 'yuv444p10le', 'yuv420p12le', 'yuv422p12le', 'yuv444p12le']:
            insights.append(f"高色彩深度: {pixel_format} (10-12位色深)")
        elif 'p10' in pixel_format or 'p12' in pixel_format:
            insights.append(f"高色彩深度: {pixel_format}")
    
    # 检查帧率约束
    if avg_frame_rate <= 0:
        violations.append(f"无效帧率: {avg_frame_rate} fps")
    elif avg_frame_rate > dynamic_constraints['max_framerate']:
        violations.append(f"帧率超出系统能力: {avg_frame_rate} fps (最大支持 {dynamic_constraints['max_framerate']} fps)")
    elif avg_frame_rate > dynamic_constraints['max_framerate'] * 0.5:
        insights.append(f"高帧率: {avg_frame_rate} fps (接近系统极限 {dynamic_constraints['max_framerate']} fps)")
    elif avg_frame_rate < 1:
        violations.append(f"帧率过低: {avg_frame_rate} fps (可能导致卡顿)")
    
    # 检查时间码和帧率一致性
    r_frame_rate_str = video_metadata.get('r_frame_rate', '0/1')
    try:
        if isinstance(r_frame_rate_str, str) and '/' in r_frame_rate_str:
            numerator, denominator = r_frame_rate_str.split('/')
            r_frame_rate = float(numerator) / float(denominator)
        else:
            r_frame_rate = float(r_frame_rate_str)
    except (ValueError, ZeroDivisionError):
        r_frame_rate = 0.0
    
    if avg_frame_rate > 0 and r_frame_rate > 0:
        if abs(r_frame_rate - avg_frame_rate) > max(0.1, avg_frame_rate * 0.05):  # 允许5%或0.1fps的误差
            violations.append(f"帧率不一致: r_frame_rate={r_frame_rate_str}, avg_frame_rate={avg_frame_rate_str}")
    
    # 检查编码器参数
    codec_name = video_metadata.get('codec_name', '').lower()
    profile = video_metadata.get('profile', '')
    level = video_metadata.get('level', '')
    
    # 动态硬件解码能力限制（基于实际系统能力）
    if codec_name not in dynamic_constraints['supported_codecs']:
        violations.append(f"编解码器不受系统支持: {codec_name}")
    else:
        # 如果编解码器受支持，使用通用限制
        hardware_limits = {
            'h264': {'max_width': min(8192, dynamic_constraints['max_width']), 'max_height': min(8192, dynamic_constraints['max_height']), 'max_level': 5.2},
            'h265': {'max_width': min(8192, dynamic_constraints['max_width']), 'max_height': min(8192, dynamic_constraints['max_height']), 'max_level': 6.2},
            'hevc': {'max_width': min(8192, dynamic_constraints['max_width']), 'max_height': min(8192, dynamic_constraints['max_height']), 'max_level': 6.2},
            'vp9': {'max_width': min(16384, dynamic_constraints['max_width']), 'max_height': min(16384, dynamic_constraints['max_height'])},
            'av1': {'max_width': min(16384, dynamic_constraints['max_width']), 'max_height': min(16384, dynamic_constraints['max_height'])}
        }
        
        if codec_name in hardware_limits:
            limits = hardware_limits[codec_name]
            if width > limits['max_width'] or height > limits['max_height']:
                violations.append(f"分辨率超出{codec_name.upper()}硬件解码能力: {width}x{height} (系统限制: {limits['max_width']}x{limits['max_height']})")
            
            if 'max_level' in limits and level:
                try:
                    # 处理level格式如 "5.1" -> 5.1, "51" -> 5.1
                    if '.' in str(level):
                        level_num = float(level)
                    else:
                        level_num = float(level) / 10.0
                    if level_num > limits['max_level']:
                        violations.append(f"级别超出{codec_name.upper()}硬件解码能力: level {level} (最大支持{limits['max_level']})")
                except (ValueError, TypeError):
                    pass  # 无法解析level，跳过检查
    
    # 检查音频参数（如果存在）
    audio_stream = video_metadata.get('audio_stream', {})
    if audio_stream:
        sample_rate = int(audio_stream.get('sample_rate', 0))
        channels = int(audio_stream.get('channels', 0))
        audio_codec = audio_stream.get('codec_name', '')
        
        if sample_rate <= 0:
            violations.append(f"无效音频采样率: {sample_rate} Hz")
        elif sample_rate > 192000:
            violations.append(f"音频采样率过高: {sample_rate} Hz (超出常规设备)")
        elif sample_rate > 96000:
            insights.append(f"高音频采样率: {sample_rate} Hz")
        
        if channels <= 0:
            violations.append(f"无效音频通道数: {channels}")
        elif channels > 8:
            insights.append(f"多声道音频: {channels} channels")
        elif channels == 1:
            insights.append("单声道音频")
    
    # 验证结果汇总
    is_valid = len(violations) == 0
    validation_results = {
        'is_valid': is_valid,
        'violations': violations,
        'insights': insights,
        'total_violations': len(violations),
        'total_insights': len(insights),
        'physical_constraints_checked': [
            'time_axis', 'spatial_resolution', 'bitrate', 'color_depth', 
            'frame_rate', 'codec_compatibility', 'audio_parameters'
        ]
    }
    
    # 生成建议
    suggestions = []
    if not is_valid:
        suggestions.append("视频参数不符合物理约束，需要修复或调整")
        if any("分辨率" in v for v in violations):
            suggestions.append("降低分辨率至硬件支持范围内")
        if any("帧率" in v for v in violations):
            suggestions.append("调整帧率至合理范围 (1-240 fps)")
        if any("码率" in v for v in violations):
            suggestions.append("降低码率以减少文件大小和处理负载")
        if any("无效" in v for v in violations):
            suggestions.append("修复无效参数值")
    else:
        suggestions.append("视频参数符合物理约束和硬件能力边界")
        if insights:
            suggestions.append("注意性能影响：某些参数可能导致高资源消耗")
    
    validation_result = {
        'validation_results': validation_results,
        'suggestions': suggestions,
        'original_metadata': video_metadata
    }
    
    # 构建综合报告
    summary = {
        'is_valid': validation_results['is_valid'],
        'total_violations': validation_results['total_violations'],
        'total_insights': validation_results['total_insights'],
        'suggestions': suggestions
    }
    
    result = {
        'metadata': metadata,
        'validation': validation_result,
        'summary': summary
    }
    
    return {
        'result': result,
        'insights': insights + [f"端到端视频物理验证完成: {'通过' if is_valid else '失败'}"],
        'memories': [
            f"端到端视频验证: {video_path}, {width}x{height}, {duration}s, {'有效' if is_valid else '无效'}"
        ],
        'facts': [
            ['video_file', 'has_physical_validation_result', 'valid' if is_valid else 'invalid'],
            ['video_file', 'has_resolution', f"{width}x{height}"],
            ['video_file', 'has_frame_rate', str(avg_frame_rate)],
            ['video_file', 'has_duration', str(duration)],
            ['video_file', 'has_codec', codec_name]
        ],
        'next_skills': ['video_repair_tool'] if not is_valid else []
    }