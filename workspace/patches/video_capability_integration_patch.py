"""
视频能力集成补丁
将系统视频处理能力评估结果集成到视频物理语义验证工作流中
"""

import json

def integrate_system_capabilities(video_metadata, system_capabilities):
    """
    将系统能力评估结果集成到视频元数据验证中
    
    Args:
        video_metadata: 视频元数据字典
        system_capabilities: 系统能力评估结果字典
        
    Returns:
        更新后的验证约束条件
    """
    # 从系统能力中提取关键约束
    constraints = {
        'max_resolution': get_max_resolution_from_capabilities(system_capabilities),
        'supported_codecs': get_supported_codecs_from_capabilities(system_capabilities),
        'max_framerate': get_max_framerate_from_capabilities(system_capabilities),
        'hardware_acceleration': get_hardware_acceleration_info(system_capabilities)
    }
    
    return constraints

def get_max_resolution_from_capabilities(system_capabilities):
    """从系统能力中获取最大支持分辨率"""
    available_params = system_capabilities.get('available_params', {})
    resolution_support = available_params.get('resolution_support', [])
    
    if '4K' in resolution_support:
        return (3840, 2160)
    elif '1080p' in resolution_support:
        return (1920, 1080)
    elif '720p' in resolution_support:
        return (1280, 720)
    else:
        return (1920, 1080)  # 默认1080p

def get_supported_codecs_from_capabilities(system_capabilities):
    """从系统能力中获取支持的编解码器列表"""
    available_params = system_capabilities.get('available_params', {})
    codec_support = available_params.get('codec_support', [])
    return [codec.lower() for codec in codec_support]

def get_max_framerate_from_capabilities(system_capabilities):
    """从系统能力中获取最大支持帧率"""
    available_params = system_capabilities.get('available_params', {})
    framerate_support = available_params.get('framerate_support', [])
    return max(framerate_support) if framerate_support else 60

def get_hardware_acceleration_info(system_capabilities):
    """获取硬件加速信息"""
    assessment_summary = system_capabilities.get('assessment_summary', {})
    return assessment_summary.get('gpu_acceleration_available', False)