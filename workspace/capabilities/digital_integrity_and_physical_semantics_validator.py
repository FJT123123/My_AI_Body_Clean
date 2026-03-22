# capability_name: digital_integrity_and_physical_semantics_validator

import os
import json
import hashlib
import cv2
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path

def validate_digital_integrity(video_path: str, reference_hash: str = None) -> Dict[str, Any]:
    """
    验证视频文件的数字完整性
    
    Args:
        video_path (str): 视频文件路径
        reference_hash (str, optional): 参考哈希值
        
    Returns:
        Dict[str, Any]: 数字完整性验证结果
    """
    result = {
        'file_exists': False,
        'file_size_valid': False,
        'hash_match': False,
        'codec_valid': False,
        'container_valid': False,
        'overall_score': 0.0
    }
    
    if not os.path.exists(video_path):
        return result
        
    result['file_exists'] = True
    
    # 检查文件大小
    file_size = os.path.getsize(video_path)
    result['file_size_valid'] = file_size > 0
    
    # 计算文件哈希
    if reference_hash:
        hash_md5 = hashlib.md5()
        with open(video_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        calculated_hash = hash_md5.hexdigest()
        result['hash_match'] = calculated_hash == reference_hash
    
    # 验证视频容器和编解码器
    try:
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            result['container_valid'] = True
            # 尝试读取一帧
            ret, frame = cap.read()
            if ret:
                result['codec_valid'] = True
            cap.release()
    except Exception:
        pass
    
    # 计算整体评分
    score = 0
    total_checks = 5
    if result['file_exists']: score += 1
    if result['file_size_valid']: score += 1
    if result['hash_match'] or reference_hash is None: score += 1  # 如果没有参考哈希，此项不扣分
    if result['container_valid']: score += 1
    if result['codec_valid']: score += 1
    
    result['overall_score'] = score / total_checks
    return result

def validate_physical_semantics(video_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    验证视频内容的物理语义一致性
    
    Args:
        video_path (str): 视频文件路径
        config (dict, optional): 验证配置参数
        
    Returns:
        Dict[str, Any]: 物理语义验证结果
    """
    try:
        from workspace.capabilities.video_physics_validation_capability import validate_video_frame_physics_compliance
        from workspace.capabilities.motion_semantic_validation_capability import run_motion_validation_cycle
        
        # 使用现有的物理验证能力
        physics_result = validate_video_frame_physics_compliance(video_path, config=config)
        
        if not physics_result['success']:
            # 如果物理验证失败，尝试使用运动语义验证作为备选
            motion_result = run_motion_validation_cycle(video_path, config=config)
            if 'error' in motion_result['result']:
                return {
                    'success': False,
                    'error': motion_result['result']['error'],
                    'validation_result': None
                }
            
            motion_data = motion_result['result']
            return {
                'success': True,
                'error': None,
                'validation_result': {
                    'frame_continuity': len(motion_data.get('motion_features', [])) > 0,
                    'motion_consistency': motion_data.get('semantic_consistency', False),
                    'physical_laws_compliance': motion_data.get('physical_plausibility', False),
                    'semantic_coherence': motion_data.get('overall_valid', False),
                    'temporal_consistency': True,  # 简化处理
                    'overall_score': 1.0 if motion_data.get('overall_valid', False) else 0.3
                }
            }
        
        # 提取关键指标
        physics_data = physics_result['validation_result']
        motion_analysis = physics_data.get('motion_analysis', {})
        
        return {
            'success': True,
            'error': None,
            'validation_result': {
                'frame_continuity': physics_data.get('video_info', {}).get('analyzed_frames', 0) > 0,
                'motion_consistency': motion_analysis.get('motion_consistency_valid', False),
                'physical_laws_compliance': motion_analysis.get('motion_magnitude_valid', False),
                'semantic_coherence': physics_data.get('overall_valid', False),
                'temporal_consistency': motion_analysis.get('temporal_coherence_valid', False),
                'overall_score': physics_data.get('confidence_score', 0.0)
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'validation_result': None
        }

def validate_digital_integrity_and_physical_semantics(video_path: str, reference_data: Optional[Dict[str, Any]] = None, context: Optional[str] = None) -> Dict[str, Any]:
    """
    同时验证视频的数字完整性与物理语义一致性
    
    Args:
        video_path (str): 待验证的视频文件路径
        reference_data (dict, optional): 参考数据，包含原始视频元数据、预期物理特征等
        context (str, optional): 验证上下文信息
        
    Returns:
        dict: 包含双重验证结果的字典
    """
    if not video_path or not isinstance(video_path, str) or not video_path.strip():
        return {
            'success': False,
            'error': '缺少有效的 video_path 参数',
            'digital_integrity': None,
            'physical_semantics': None,
            'overall_consistency': 0.0,
            'recommendations': []
        }
    
    if not os.path.exists(video_path):
        return {
            'success': False,
            'error': f'视频文件不存在: {video_path}',
            'digital_integrity': None,
            'physical_semantics': None,
            'overall_consistency': 0.0,
            'recommendations': ['检查文件路径是否正确']
        }
    
    # 提取参考数据
    reference_hash = None
    config = None
    if reference_data:
        reference_hash = reference_data.get('original_hash')
        config = reference_data.get('validation_config')
    
    # 执行数字完整性验证
    digital_result = validate_digital_integrity(video_path, reference_hash)
    
    # 执行物理语义验证
    physical_result = validate_physical_semantics(video_path, config)
    
    # 计算整体一致性
    if physical_result['success']:
        physical_score = physical_result['validation_result']['overall_score']
    else:
        physical_score = 0.0
    
    overall_consistency = (digital_result['overall_score'] + physical_score) / 2
    
    # 生成修复建议
    recommendations = []
    if digital_result['overall_score'] < 0.8:
        recommendations.append("数字完整性不足，建议检查文件传输过程或重新编码")
    if physical_score < 0.7:
        recommendations.append("物理语义一致性不足，建议使用smart_video_repair_tool进行修复")
    if overall_consistency < 0.75:
        recommendations.append("整体一致性不足，建议执行完整的视频自愈工作流")
    
    return {
        'success': True,
        'error': None,
        'digital_integrity': digital_result,
        'physical_semantics': physical_result['validation_result'] if physical_result['success'] else None,
        'physical_semantics_error': physical_result['error'] if not physical_result['success'] else None,
        'overall_consistency': overall_consistency,
        'recommendations': recommendations,
        'context': context
    }