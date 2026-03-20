#!/usr/bin/env python3
"""
分析视频帧间运动语义
"""

import cv2
import numpy as np
import os
import json

# 帧目录
frame_dir = "extracted_frames_local"
frame_files = sorted([f for f in os.listdir(frame_dir) if f.endswith('.jpg')])
frame_paths = [os.path.join(frame_dir, f) for f in frame_files]

print(f"找到 {len(frame_paths)} 个帧")

if len(frame_paths) < 2:
    print("帧数不足，无法分析")
    exit(1)

# 分析相邻帧
results = {
    'frame_pairs_analyzed': 0,
    'motion_vectors': [],
    'difference_scores': [],
    'semantic_analysis': []
}

for i in range(len(frame_paths) - 1):
    # 读取帧
    frame1 = cv2.imread(frame_paths[i])
    frame2 = cv2.imread(frame_paths[i + 1])
    
    if frame1 is None or frame2 is None:
        continue
    
    # 调整到相同尺寸
    h1, w1 = frame1.shape[:2]
    h2, w2 = frame2.shape[:2]
    min_h, min_w = min(h1, h2), min(w1, w2)
    frame1_resized = cv2.resize(frame1, (min_w, min_h))
    frame2_resized = cv2.resize(frame2, (min_w, min_h))
    
    # 计算帧间差异
    diff = cv2.absdiff(frame1_resized, frame2_resized)
    diff_score = np.mean(diff)
    
    # 光流分析
    gray1 = cv2.cvtColor(frame1_resized, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2_resized, cv2.COLOR_BGR2GRAY)
    
    try:
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # 计算运动幅度
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_magnitude = np.mean(magnitude)
        
        # 判断运动是否具有物理意义
        if avg_magnitude > 1.0 and diff_score > 5.0:
            motion_significance = "significant"
            semantic_desc = "检测到显著运动：可能表示物体移动或场景变化"
        elif avg_magnitude > 0.5 or diff_score > 2.0:
            motion_significance = "minor"
            semantic_desc = "检测到轻微运动：可能是相机抖动或小物体移动"
        else:
            motion_significance = "negligible"
            semantic_desc = "未检测到明显运动：帧间内容基本一致"
        
        results['motion_vectors'].append({
            'frame_pair': [i, i + 1],
            'average_motion_magnitude': float(avg_magnitude),
            'difference_score': float(diff_score),
            'motion_significance': motion_significance
        })
        
        results['semantic_analysis'].append({
            'frame_pair': [i, i + 1],
            'semantic_description': semantic_desc,
            'physical_meaning': motion_significance != "negligible"
        })
        
        results['frame_pairs_analyzed'] += 1
        
    except Exception as e:
        print(f"光流分析失败: {e}")
        # 使用简单的差异分析
        if diff_score > 5.0:
            motion_significance = "significant"
            semantic_desc = "检测到显著变化：可能表示场景切换"
        elif diff_score > 2.0:
            motion_significance = "minor"
            semantic_desc = "检测到轻微变化"
        else:
            motion_significance = "negligible"
            semantic_desc = "未检测到明显变化"
            
        results['semantic_analysis'].append({
            'frame_pair': [i, i + 1],
            'semantic_description': semantic_desc,
            'physical_meaning': motion_significance != "negligible"
        })
        
        results['frame_pairs_analyzed'] += 1

# 总体分析
total_significant = sum(1 for sa in results['semantic_analysis'] if sa['physical_meaning'])
results['overall_analysis'] = {
    'total_frame_pairs': len(results['semantic_analysis']),
    'significant_motion_pairs': total_significant,
    'motion_density': total_significant / len(results['semantic_analysis']) if results['semantic_analysis'] else 0,
    'video_has_meaningful_motion': total_significant > 0
}

if results['overall_analysis']['video_has_meaningful_motion']:
    if results['overall_analysis']['motion_density'] > 0.5:
        results['semantic_conclusion'] = "视频包含丰富的有意义运动，表明内容动态且具有物理意义"
    else:
        results['semantic_conclusion'] = "视频包含一些有意义的运动，但整体较为静态"
else:
    results['semantic_conclusion'] = "视频缺乏有意义的运动，可能为静态场景或修复后丢失了运动信息"

# 保存结果
with open("motion_semantic_analysis.json", "w") as f:
    json.dump(results, f, indent=2)

print("分析完成!")
print(f"分析了 {results['frame_pairs_analyzed']} 对帧")
print(f"视频是否有有意义的运动: {results['overall_analysis']['video_has_meaningful_motion']}")
print(f"结论: {results['semantic_conclusion']}")