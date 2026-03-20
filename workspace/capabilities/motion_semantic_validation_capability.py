# capability_name: motion_semantic_validation_capability

import cv2
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

def calculate_optical_flow(prev_frame: np.ndarray, curr_frame: np.ndarray) -> Tuple[np.ndarray, float]:
    """计算两帧之间的光流"""
    # 转换为灰度图
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
    
    # 计算光流
    flow = cv2.calcOpticalFlowFarneback(
        prev_gray, curr_gray, 
        None, 
        pyr_scale=0.5, 
        levels=3, 
        winsize=15, 
        iterations=3, 
        poly_n=5, 
        poly_sigma=1.2, 
        flags=0
    )
    
    # 计算平均运动向量的大小
    magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
    avg_magnitude = np.mean(magnitude)
    
    return flow, avg_magnitude

def analyze_motion_consistency(flows: List[np.ndarray], magnitudes: List[float]) -> Dict[str, Any]:
    """分析运动的一致性"""
    if len(magnitudes) < 2:
        return {
            "motion_consistency": True,
            "avg_magnitude": 0,
            "magnitude_variance": 0,
            "motion_jumps": 0,
            "anomaly_detected": False
        }
    
    # 计算运动幅度的统计信息
    avg_magnitude = np.mean(magnitudes)
    magnitude_variance = np.var(magnitudes)
    
    # 检测运动幅度的异常跳变
    motion_jumps = 0
    jump_threshold = avg_magnitude * 1.5 if avg_magnitude > 0 else 0.1
    for i in range(1, len(magnitudes)):
        if abs(magnitudes[i] - magnitudes[i-1]) > jump_threshold:
            motion_jumps += 1
    
    # 判断运动一致性
    motion_consistency = (motion_jumps / len(magnitudes)) < 0.3  # 超过30%跳变为不一致
    
    # 检测异常
    anomaly_detected = motion_jumps > 0 or avg_magnitude > 50  # 阈值可调整
    
    return {
        "motion_consistency": bool(motion_consistency),
        "avg_magnitude": float(avg_magnitude),
        "magnitude_variance": float(magnitude_variance),
        "motion_jumps": int(motion_jumps),
        "anomaly_detected": bool(anomaly_detected)
    }

def extract_motion_features(flow: np.ndarray) -> Dict[str, Any]:
    """从光流中提取运动特征"""
    # 计算水平和垂直方向的运动分布
    horizontal_flow = flow[..., 0]
    vertical_flow = flow[..., 1]
    
    # 计算运动方向的分布
    magnitude = np.sqrt(horizontal_flow**2 + vertical_flow**2)
    angle = np.arctan2(vertical_flow, horizontal_flow)
    
    # 计算统计特征
    features = {
        "avg_horizontal_flow": float(np.mean(horizontal_flow)),
        "avg_vertical_flow": float(np.mean(vertical_flow)),
        "avg_magnitude": float(np.mean(magnitude)),
        "max_magnitude": float(np.max(magnitude)),
        "flow_direction_entropy": float(calculate_entropy(angle)),
        "horizontal_variance": float(np.var(horizontal_flow)),
        "vertical_variance": float(np.var(vertical_flow))
    }
    
    return features

def calculate_entropy(arr: np.ndarray) -> float:
    """计算数组的熵值"""
    # 将角度值归一化到0-2π范围
    arr = np.abs(arr) % (2 * np.pi)
    # 计算直方图
    hist, _ = np.histogram(arr, bins=36, range=(0, 2*np.pi))
    # 计算概率
    prob = hist / np.sum(hist)
    # 计算熵
    entropy = -np.sum(prob[prob > 0] * np.log2(prob[prob > 0] + 1e-10))
    return entropy

def validate_video_frames(video_path: str, frame_interval: int = 5) -> Dict[str, Any]:
    """验证视频帧间的运动语义连续性"""
    try:
        # 打开视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {
                'result': {'error': '无法打开视频文件，可能文件不存在或格式不支持'},
                'insights': [f'视频文件访问失败: {video_path}'],
                'facts': [],
                'memories': []
            }
        
        # 提取关键帧
        frames = []
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame.copy())
            
            frame_count += 1
        
        cap.release()
        
        if len(frames) < 2:
            return {
                'result': {'error': '视频帧数不足，无法进行运动分析'},
                'insights': ['视频内容验证失败：帧数少于2帧'],
                'facts': [],
                'memories': []
            }
        
        # 计算帧间光流
        flows = []
        magnitudes = []
        motion_features_list = []
        
        for i in range(1, len(frames)):
            try:
                flow, magnitude = calculate_optical_flow(frames[i-1], frames[i])
                flows.append(flow)
                magnitudes.append(magnitude)
                
                # 提取运动特征
                features = extract_motion_features(flow)
                motion_features_list.append(features)
            except Exception as e:
                logging.warning(f"计算光流时出错于帧 {i}: {str(e)}")
                continue
        
        if not flows:
            return {
                'result': {'error': '无法计算光流，视频内容可能无效'},
                'insights': ['运动分析失败：无法计算帧间光流'],
                'facts': [],
                'memories': []
            }
        
        # 分析运动一致性
        motion_analysis = analyze_motion_consistency(flows, magnitudes)
        
        # 综合评估
        semantic_consistency = motion_analysis["motion_consistency"] and motion_analysis["motion_jumps"] == 0
        physical_plausibility = motion_analysis["avg_magnitude"] < 30  # 阈值可调整
        
        # 构建验证结果
        validation_result = {
            "total_frames_analyzed": len(frames),
            "frame_interval": frame_interval,
            "motion_analysis": motion_analysis,
            "semantic_consistency": bool(semantic_consistency),
            "physical_plausibility": bool(physical_plausibility),
            "overall_valid": bool(semantic_consistency and physical_plausibility),
            "motion_features": motion_features_list,
            "total_motion_jumps": motion_analysis["motion_jumps"]
        }
        
        return {
            'result': validation_result,
            'insights': [f'成功完成视频帧间运动语义验证: {video_path}'],
            'facts': [f'video_motion_semantic_validation_success_for_{video_path}'],
            'memories': [f'validated_motion_semantics_successfully_for_{video_path}']
        }
        
    except Exception as e:
        return {
            'result': {'error': f'处理视频时发生错误: {str(e)}'},
            'insights': [f'视频处理异常: {str(e)}'],
            'facts': [],
            'memories': []
        }

def run_motion_validation_cycle(video_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    执行视频帧间运动语义验证周期
    
    Args:
        video_path: 视频文件路径
        config: 可选配置参数，如 frame_interval
    
    Returns:
        包含验证结果的字典
    """
    # 默认配置
    default_config = {"frame_interval": 5}
    if config:
        default_config.update(config)
    
    frame_interval = default_config.get("frame_interval", 5)
    
    # 验证输入参数
    if not video_path:
        return {
            'result': {'error': '缺少 video_path 参数'},
            'insights': ['参数校验失败：必须提供 video_path'],
            'facts': [],
            'memories': []
        }
    elif not isinstance(video_path, str):
        return {
            'result': {'error': 'video_path 参数类型错误，应为字符串'},
            'insights': ['参数校验失败：video_path 必须是字符串类型'],
            'facts': [],
            'memories': []
        }
    elif video_path.strip() == "":
        return {
            'result': {'error': 'video_path 参数不能为空字符串'},
            'insights': ['参数校验失败：video_path 不能为空'],
            'facts': [],
            'memories': []
        }
    
    if not isinstance(frame_interval, int) or frame_interval <= 0:
        return {
            'result': {'error': '缺少有效的 frame_interval 参数，必须为正整数'},
            'insights': ['参数校验失败：frame_interval 必须为正整数'],
            'facts': [],
            'memories': []
        }
    
    # 开始验证
    result = validate_video_frames(video_path, frame_interval)
    
    return result

# 兼容性入口函数
def check_video_motion_semantics(video_path: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    检查视频的运动语义连贯性
    
    Args:
        video_path: 视频文件路径
        config: 配置参数
    
    Returns:
        验证结果字典
    """
    return run_motion_validation_cycle(video_path, config)