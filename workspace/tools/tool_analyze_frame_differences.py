# tool_name: analyze_frame_differences

from langchain.tools import tool
import os
import cv2
import numpy as np
import json
from pathlib import Path

@tool
def analyze_frame_differences(frame_paths, output_dir='./frame_analysis'):
    """
    分析视频帧序列之间的差异，计算帧间运动向量和变化程度，
    识别有意义的运动语义（如物体移动、场景变化等）。
    
    Args:
        frame_paths (list): 帧文件路径列表，按时间顺序排列
        output_dir (str): 输出分析结果的目录
    
    Returns:
        dict: 包含帧间差异分析结果的字典
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    if not frame_paths or len(frame_paths) < 2:
        return {
            'error': '至少需要两个帧进行差异分析',
            'frame_count': len(frame_paths) if frame_paths else 0
        }
    
    # 读取第一帧
    prev_frame = cv2.imread(frame_paths[0])
    if prev_frame is None:
        return {'error': f'无法读取第一帧: {frame_paths[0]}'}
    
    # 转换为灰度图
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    differences = []
    motion_vectors = []
    
    for i in range(1, len(frame_paths)):
        curr_frame = cv2.imread(frame_paths[i])
        if curr_frame is None:
            continue
            
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # 计算绝对差异
        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        # 计算光流（运动向量）
        try:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            # 计算平均运动幅度
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            mean_magnitude = np.mean(magnitude)
            max_magnitude = np.max(magnitude)
            
            motion_vectors.append({
                'frame_index': i,
                'mean_magnitude': float(mean_magnitude),
                'max_magnitude': float(max_magnitude),
                'total_motion_pixels': int(np.sum(magnitude > 1.0))
            })
        except Exception as e:
            motion_vectors.append({
                'frame_index': i,
                'error': str(e)
            })
        
        differences.append({
            'frame_pair': [i-1, i],
            'mean_difference': float(mean_diff),
            'max_difference': float(max_diff),
            'significant_change': mean_diff > 10.0  # 阈值可调整
        })
        
        prev_gray = curr_gray
    
    # 分析整体运动模式
    total_significant_changes = sum(1 for d in differences if d['significant_change'])
    avg_motion_magnitude = np.mean([m.get('mean_magnitude', 0) for m in motion_vectors if 'mean_magnitude' in m])
    
    # 判断是否有有意义的运动
    has_meaningful_motion = (
        total_significant_changes > len(differences) * 0.1 or  # 至少10%的帧对有显著变化
        avg_motion_magnitude > 0.5  # 平均运动幅度大于阈值
    )
    
    result = {
        'frame_count': len(frame_paths),
        'analyzed_pairs': len(differences),
        'differences': differences,
        'motion_vectors': motion_vectors,
        'summary': {
            'total_significant_changes': total_significant_changes,
            'average_motion_magnitude': float(avg_motion_magnitude),
            'has_meaningful_motion': bool(has_meaningful_motion),
            'motion_type': 'dynamic' if has_meaningful_motion else 'static'
        }
    }
    
    # 保存结果到文件
    result_path = os.path.join(output_dir, 'frame_differences_analysis.json')
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return result