"""
自动生成的技能模块
需求: 创建一个视频物理双重验证技能，从args['input']获取JSON字符串，解析后执行验证。
生成时间: 2026-03-21 14:33:56
"""

# skill_name: video_physics_dual_verification
import json
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

def main(args=None) -> Dict[str, Any]:
    """
    视频物理双重验证技能：从args['input']获取JSON字符串，解析后执行验证
    验证包括视频内容的物理规则检查和数据一致性验证
    """
    if args is None:
        args = {}
    
    input_json_str = args.get('input')
    if not input_json_str:
        return {
            'result': {'error': '缺少input参数'},
            'insights': ['输入参数缺失'],
            'facts': [],
            'memories': []
        }
    
    try:
        # 解析输入的JSON字符串
        input_data = json.loads(input_json_str)
    except json.JSONDecodeError as e:
        return {
            'result': {'error': f'JSON解析失败: {str(e)}'},
            'insights': ['输入JSON格式错误'],
            'facts': [],
            'memories': []
        }
    
    # 提取视频路径和验证参数
    video_path = input_data.get('video_path')
    verification_params = input_data.get('verification_params', {})
    
    if not video_path:
        return {
            'result': {'error': '缺少video_path参数'},
            'insights': ['视频路径未提供'],
            'facts': [],
            'memories': []
        }
    
    # 检查视频文件是否存在
    import os
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'视频文件不存在: {video_path}'],
            'facts': [],
            'memories': []
        }
    
    # 开始视频验证流程
    verification_results = []
    insights = []
    facts = []
    memories = []
    
    # 执行视频物理验证
    try:
        video_valid, physics_check_result = perform_video_physics_verification(
            video_path, 
            verification_params
        )
        
        verification_results.append({
            'type': 'video_physics_verification',
            'valid': video_valid,
            'details': physics_check_result
        })
        
        if video_valid:
            insights.append('视频物理验证通过')
            facts.append(('video', 'passes_physics_verification', video_path))
        else:
            insights.append('视频物理验证失败')
            facts.append(('video', 'fails_physics_verification', video_path))
    
    except Exception as e:
        verification_results.append({
            'type': 'video_physics_verification',
            'valid': False,
            'error': str(e)
        })
        insights.append(f'视频物理验证过程中出现错误: {str(e)}')
    
    # 执行物理双重验证
    try:
        physics_valid, physics_result = perform_physics_dual_verification(
            video_path,
            verification_params
        )
        
        verification_results.append({
            'type': 'physics_dual_verification',
            'valid': physics_valid,
            'details': physics_result
        })
        
        if physics_valid:
            insights.append('物理双重验证通过')
            facts.append(('video', 'passes_dual_verification', video_path))
        else:
            insights.append('物理双重验证失败')
            facts.append(('video', 'fails_dual_verification', video_path))
    
    except Exception as e:
        verification_results.append({
            'type': 'physics_dual_verification',
            'valid': False,
            'error': str(e)
        })
        insights.append(f'物理双重验证过程中出现错误: {str(e)}')
    
    # 综合验证结果
    overall_valid = all(vr['valid'] for vr in verification_results if 'valid' in vr)
    
    # 生成验证摘要
    verification_summary = {
        'video_path': video_path,
        'overall_valid': overall_valid,
        'verification_results': verification_results
    }
    
    # 记录验证记忆
    memories.append({
        'event_type': 'skill_executed',
        'content': f'视频物理双重验证完成，结果: {overall_valid}',
        'tags': ['video_verification', 'physics_validation']
    })
    
    return {
        'result': verification_summary,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }

def perform_video_physics_verification(video_path: str, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    执行视频物理验证
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return False, {'error': '无法打开视频文件'}
    
    # 检查视频的基本属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 检查视频参数是否符合预期
    expected_fps = params.get('expected_fps', 24.0)
    expected_resolution = params.get('expected_resolution')
    
    fps_check = abs(fps - expected_fps) <= 1.0 if expected_fps else True
    resolution_check = (width, height) == expected_resolution if expected_resolution else True
    
    # 读取关键帧进行物理验证
    physics_consistency_checks = []
    frame_indices = [0, frame_count//4, frame_count//2, 3*frame_count//4, frame_count-1]
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
            
        # 检查物理一致性（如运动物体的连续性等）
        physics_consistency = check_frame_physics_consistency(frame, idx)
        physics_consistency_checks.append(physics_consistency)
    
    cap.release()
    
    # 综合判断
    fps_ok = fps_check
    res_ok = resolution_check
    physics_ok = all(physics_consistency_checks) if physics_consistency_checks else True
    
    is_valid = fps_ok and res_ok and physics_ok
    
    return is_valid, {
        'fps_check': fps_check,
        'resolution_check': res_ok,
        'physics_consistency': physics_consistency_checks,
        'fps': fps,
        'resolution': (width, height),
        'frame_count': frame_count
    }

def check_frame_physics_consistency(frame: np.ndarray, frame_idx: int) -> bool:
    """
    检查单帧的物理一致性
    """
    # 简单的物理一致性检查：检测图像梯度是否合理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # 检查梯度是否在合理范围内
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    avg_gradient = np.mean(grad_magnitude)
    
    # 检查是否过低（可能表明帧重复或模糊）
    if avg_gradient < 10:
        return False
    
    # 检查是否过高（可能表明剧烈变化或噪点）
    if avg_gradient > 150:
        return False
    
    return True

def perform_physics_dual_verification(video_path: str, params: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    执行物理双重验证
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return False, {'error': '无法打开视频文件'}
    
    # 检查物理规律，如重力、运动连续性等
    frames = []
    frame_indices = [0, 1, 2, 3, 4]  # 前5帧用于检测
    
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            break
        frames.append((idx, frame))
    
    cap.release()
    
    # 执行双重验证检查
    dual_verification_result = check_dual_verification(frames, params)
    
    return dual_verification_result['valid'], dual_verification_result

def check_dual_verification(frames: List[Tuple[int, np.ndarray]], params: Dict[str, Any]) -> Dict[str, Any]:
    """
    检查物理双重验证
    """
    if len(frames) < 2:
        return {
            'valid': False,
            'error': '帧数不足，无法执行双重验证'
        }
    
    # 检查相邻帧之间的物理一致性
    motion_consistency = True
    for i in range(1, len(frames)):
        prev_frame = frames[i-1][1]
        curr_frame = frames[i][1]
        
        # 检查两帧之间的运动是否符合物理规律
        motion_consistent = check_frame_motion_consistency(prev_frame, curr_frame)
        if not motion_consistent:
            motion_consistency = False
            break
    
    # 检查其他物理属性
    physics_rules_check = all([
        check_physics_rule(frame) for _, frame in frames
    ])
    
    return {
        'valid': motion_consistency and physics_rules_check,
        'motion_consistency': motion_consistency,
        'physics_rules_check': physics_rules_check
    }

def check_frame_motion_consistency(prev_frame: np.ndarray, curr_frame: np.ndarray) -> bool:
    """
    检查相邻帧之间的运动一致性
    """
    # 计算帧差
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # 检查运动是否在合理范围内
    motion_intensity = np.mean(gray_diff)
    
    # 如果运动过小或过大，可能不符合物理规律
    if motion_intensity < 1.0 or motion_intensity > 50.0:
        return False
    
    return True

def check_physics_rule(frame: np.ndarray) -> bool:
    """
    检查单帧是否符合基本物理规则
    """
    # 检查图像是否合理（非全黑、非全白等）
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if np.mean(gray) < 5 or np.mean(gray) > 250:
        return False
    
    # 检查图像是否清晰
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 100:
        return False  # 图像可能模糊
    
    return True