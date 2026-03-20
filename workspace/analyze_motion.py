import cv2
import numpy as np
import os
import json

# 获取帧文件列表
frame_dir = "motion_test_frames"
frame_files = []
for i in range(10):
    frame_path = f"motion_test_frames/frame_{i:04d}_{i*0.5:.2f}s.jpg"
    if os.path.exists(frame_path):
        frame_files.append(frame_path)

print(f"找到 {len(frame_files)} 个帧文件")

# 分析运动
if len(frame_files) < 2:
    result = {
        'error': '至少需要2帧才能进行差异分析',
        'motion_detected': False,
        'motion_metrics': []
    }
else:
    motion_metrics = []
    
    for i in range(1, len(frame_files)):
        # 读取当前帧和前一帧
        prev_frame = cv2.imread(frame_files[i-1])
        curr_frame = cv2.imread(frame_files[i])
        
        if prev_frame is None or curr_frame is None:
            continue
        
        # 转换为灰度图
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # 计算绝对差值
        frame_diff = cv2.absdiff(prev_gray, curr_gray)
        
        # 应用高斯模糊减少噪声
        blurred = cv2.GaussianBlur(frame_diff, (5, 5), 0)
        
        # 应用阈值处理
        _, thresh = cv2.threshold(blurred, 30, 255, cv2.THRESH_BINARY)
        
        # 计算运动区域面积
        motion_area = np.sum(thresh > 0)
        total_pixels = thresh.size
        motion_ratio = motion_area / total_pixels
        
        # 如果运动区域占比超过阈值，认为检测到显著运动
        significant_motion = motion_ratio > 0.01  # 1%阈值
        
        motion_metrics.append({
            'frame_pair': f"{i-1}-{i}",
            'time_interval': 0.5,  # 假设0.5秒间隔
            'motion_area_pixels': int(motion_area),
            'motion_ratio': float(motion_ratio),
            'significant_motion': bool(significant_motion),
            'motion_intensity': float(np.mean(frame_diff))
        })
    
    # 判断整体是否检测到运动
    any_significant_motion = any(metric['significant_motion'] for metric in motion_metrics)
    
    result = {
        'motion_detected': bool(any_significant_motion),
        'total_frame_pairs': len(motion_metrics),
        'motion_metrics': motion_metrics,
        'summary': {
            'max_motion_ratio': max([m['motion_ratio'] for m in motion_metrics]) if motion_metrics else 0,
            'avg_motion_ratio': float(np.mean([m['motion_ratio'] for m in motion_metrics])) if motion_metrics else 0,
            'frames_with_significant_motion': sum(1 for m in motion_metrics if m['significant_motion'])
        }
    }

# 保存结果
with open("motion_analysis_result.json", "w") as f:
    json.dump(result, f, indent=2)

print("运动分析结果:")
print(json.dumps(result, indent=2))