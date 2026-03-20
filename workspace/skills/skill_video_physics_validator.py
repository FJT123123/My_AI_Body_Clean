"""
视频修复工具链的物理语义验证层
能够验证视频参数是否符合现实物理约束和硬件能力边界。
该技能接收视频元数据作为输入，检查时间、空间、硬件和运动相关的物理约束，并返回验证结果和建议。

参数契约:
- video_metadata (dict, required): 视频元数据字典，包含duration, width, height, avg_frame_rate等字段
- 或者接受包含video_metadata键的JSON字符串

返回值:
- validation_results: 验证结果详情
- suggestions: 修复建议
- original_metadata: 原始元数据
"""
# skill_name: video_physics_validator

import json
import os
import math

def main(input_args=None):
    """
    视频物理语义验证主函数
    
    参数:
        input_args: 可能是字典或JSON字符串，包含video_metadata字段
        
    返回:
        包含验证结果的结构化字典
    """
    # 参数类型检查和解析
    actual_input = input_args
    
    # 处理不同类型的输入
    if isinstance(input_args, dict) and 'input' in input_args:
        # 从包装结构中提取实际输入
        try:
            actual_input = json.loads(input_args['input'])
        except (json.JSONDecodeError, TypeError):
            actual_input = input_args['input'] if isinstance(input_args['input'], dict) else {}
    elif isinstance(input_args, str):
        try:
            actual_input = json.loads(input_args)
        except (json.JSONDecodeError, TypeError):
            return {
                'result': {'error': '无效的JSON输入格式'},
                'insights': ['输入必须是有效的JSON格式'],
                'facts': [],
                'memories': []
            }
    elif input_args is None:
        actual_input = {}
    elif isinstance(input_args, dict):
        actual_input = input_args
    else:
        return {
            'result': {'error': '不支持的输入参数类型'},
            'insights': ['输入参数必须是字典或JSON字符串'],
            'facts': [],
            'memories': []
        }
    
    # 提取视频元数据
    video_metadata = {}
    if isinstance(actual_input, dict):
        video_metadata = actual_input.get('video_metadata', {})
    else:
        return {
            'result': {'error': '输入格式错误'},
            'insights': ['输入必须包含video_metadata字段'],
            'facts': [],
            'memories': []
        }
    
    if not video_metadata:
        return {
            'result': {'error': '缺少视频元数据'},
            'insights': ['视频物理验证需要输入视频元数据'],
            'facts': [],
            'memories': [],
            'next_skills': ['video_metadata_analyzer']
        }
    
    # 验证视频参数的物理约束
    validation_results = []
    insights = []
    violations = []
    
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
    
    # 检查帧数一致性（如果有nb_frames字段）
    nb_frames = video_metadata.get('nb_frames', 0)
    if nb_frames and duration > 0 and avg_frame_rate > 0:
        expected_frames = duration * avg_frame_rate
        actual_frames = int(nb_frames)
        if abs(expected_frames - actual_frames) > max(10, expected_frames * 0.1):  # 允许10%误差或10帧的绝对误差
            violations.append(f"帧数不一致: 预期{expected_frames:.1f}, 实际{actual_frames}")
    
    # 检查空间分辨率约束
    width = int(video_metadata.get('width', 0))
    height = int(video_metadata.get('height', 0))
    if width <= 0 or height <= 0:
        violations.append(f"无效分辨率: {width}x{height}")
    elif width > 16384 or height > 16384:
        violations.append(f"分辨率超出硬件极限: {width}x{height}")
    elif width > 8192 or height > 8192:
        insights.append(f"超高分辨率: {width}x{height} (可能影响性能)")
    elif width > 4096 or height > 4096:
        insights.append(f"高分辨率: {width}x{height}")
    
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
    elif avg_frame_rate > 240:
        violations.append(f"帧率过高: {avg_frame_rate} fps (超出人眼感知和常规硬件)")
    elif avg_frame_rate > 120:
        insights.append(f"高帧率: {avg_frame_rate} fps")
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
    
    # 硬件解码能力限制（基于现代消费级硬件）
    hardware_limits = {
        'h264': {'max_width': 8192, 'max_height': 8192, 'max_level': 5.2},
        'h265': {'max_width': 8192, 'max_height': 8192, 'max_level': 6.2},
        'hevc': {'max_width': 8192, 'max_height': 8192, 'max_level': 6.2},
        'vp9': {'max_width': 16384, 'max_height': 16384},
        'av1': {'max_width': 16384, 'max_height': 16384}
    }
    
    if codec_name in hardware_limits:
        limits = hardware_limits[codec_name]
        if width > limits['max_width'] or height > limits['max_height']:
            violations.append(f"分辨率超出{codec_name.upper()}硬件解码能力: {width}x{height}")
        
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
    
    result = {
        'validation_results': validation_results,
        'suggestions': suggestions,
        'original_metadata': video_metadata
    }
    
    return {
        'result': result,
        'insights': insights + [f"视频物理验证完成: {'通过' if is_valid else '失败'}"],
        'memories': [
            f"视频物理验证: {width}x{height}, {avg_frame_rate}fps, 时长{duration}s, 编码{codec_name}"
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