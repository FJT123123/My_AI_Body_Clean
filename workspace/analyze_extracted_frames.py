#!/usr/bin/env python3
"""
分析提取的视频帧，验证运动语义连续性
"""

import sys
import os
import json
import cv2
import numpy as np

# 添加 workspace/capabilities 到路径
workspace_dir = os.path.dirname(os.path.abspath(__file__))
capabilities_dir = os.path.join(workspace_dir, 'workspace', 'capabilities')
if os.path.exists(capabilities_dir):
    sys.path.insert(0, capabilities_dir)

def main():
    # 从命令行参数获取帧目录
    if len(sys.argv) < 2:
        print("Usage: python analyze_extracted_frames.py <frames_dir>")
        sys.exit(1)
    
    frames_dir = sys.argv[1]
    
    # 获取所有帧文件
    frame_files = []
    for file in sorted(os.listdir(frames_dir)):
        if file.endswith('.jpg') or file.endswith('.png'):
            frame_files.append(os.path.join(frames_dir, file))
    
    if len(frame_files) < 2:
        result = {
            "success": False,
            "error": "帧数不足，无法进行运动分析",
            "validation_result": None
        }
        print(json.dumps(result))
        return
    
    # 加载 motion_semantic_validation_capability
    try:
        from motion_semantic_validation_capability import check_video_motion_semantics
    except ImportError as e:
        result = {
            "success": False,
            "error": f"无法导入 motion_semantic_validation_capability: {str(e)}",
            "validation_result": None
        }
        print(json.dumps(result))
        return
    
    # 直接使用 OpenCV 分析帧间运动
    frames = []
    for frame_file in frame_files:
        frame = cv2.imread(frame_file)
        if frame is not None:
            frames.append(frame)
    
    if len(frames) < 2:
        result = {
            "success": False,
            "error": "无法加载足够的有效帧",
            "validation_result": None
        }
        print(json.dumps(result))
        return
    
    # 计算光流和运动分析
    flows = []
    magnitudes = []
    
    for i in range(1, len(frames)):
        prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
        
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
        
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        avg_magnitude = np.mean(magnitude)
        
        flows.append(flow)
        magnitudes.append(avg_magnitude)
    
    # 分析运动一致性
    if len(magnitudes) > 0:
        avg_magnitude = float(np.mean(magnitudes))
        magnitude_variance = float(np.var(magnitudes))
        
        # 检测运动跳变
        motion_jumps = 0
        jump_threshold = avg_magnitude * 1.5 if avg_magnitude > 0 else 0.1
        for i in range(1, len(magnitudes)):
            if abs(magnitudes[i] - magnitudes[i-1]) > jump_threshold:
                motion_jumps += 1
        
        motion_consistency = (motion_jumps / len(magnitudes)) < 0.3
        anomaly_detected = motion_jumps > 0 or avg_magnitude > 50
        
        validation_result = {
            "total_frames_analyzed": len(frames),
            "motion_analysis": {
                "motion_consistency": bool(motion_consistency),
                "avg_magnitude": avg_magnitude,
                "magnitude_variance": magnitude_variance,
                "motion_jumps": int(motion_jumps),
                "anomaly_detected": bool(anomaly_detected)
            },
            "semantic_consistency": bool(motion_consistency and motion_jumps == 0),
            "physical_plausibility": bool(avg_magnitude < 30),
            "overall_valid": bool(motion_consistency and motion_jumps == 0 and avg_magnitude < 30)
        }
        
        result = {
            "success": True,
            "error": None,
            "validation_result": validation_result
        }
    else:
        result = {
            "success": False,
            "error": "无法计算光流",
            "validation_result": None
        }
    
    # 确保结果可以JSON序列化
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()