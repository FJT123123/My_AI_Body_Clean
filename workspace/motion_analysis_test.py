import cv2
import numpy as np
import os
import json

# 帧路径
frame_paths = [
    "/Users/zhufeng/My_AI_Body_副本/motion_test_frames/frame_0000_0.00s.jpg",
    "/Users/zhufeng/My_AI_Body_副本/motion_test_frames/frame_0001_1.00s.jpg", 
    "/Users/zhufeng/My_AI_Body_副本/motion_test_frames/frame_0002_2.00s.jpg",
    "/Users/zhufeng/My_AI_Body_副本/motion_test_frames/frame_0003_3.00s.jpg",
    "/Users/zhufeng/My_AI_Body_副本/motion_test_frames/frame_0004_4.00s.jpg"
]

# 检查文件是否存在
for path in frame_paths:
    if not os.path.exists(path):
        print(f"文件不存在: {path}")
    else:
        print(f"文件存在: {path}")

# 读取第一帧
prev_frame = cv2.imread(frame_paths[0])
if prev_frame is None:
    print("无法读取第一帧")
else:
    print(f"成功读取第一帧，形状: {prev_frame.shape}")
    
    # 转换为灰度
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    differences = []
    motion_vectors = []
    
    for i in range(1, len(frame_paths)):
        curr_frame = cv2.imread(frame_paths[i])
        if curr_frame is None:
            print(f"无法读取帧 {i}: {frame_paths[i]}")
            continue
            
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        # 计算绝对差异
        diff = cv2.absdiff(prev_gray, curr_gray)
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        print(f"帧 {i-1} 到 {i} 的平均差异: {mean_diff:.2f}")
        
        # 计算光流
        try:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            mean_magnitude = np.mean(magnitude)
            max_magnitude = np.max(magnitude)
            
            print(f"帧 {i-1} 到 {i} 的平均运动幅度: {mean_magnitude:.2f}")
            
            motion_vectors.append({
                'frame_index': i,
                'mean_magnitude': float(mean_magnitude),
                'max_magnitude': float(max_magnitude),
                'total_motion_pixels': int(np.sum(magnitude > 1.0))
            })
        except Exception as e:
            print(f"光流计算失败: {e}")
            motion_vectors.append({
                'frame_index': i,
                'error': str(e)
            })
        
        differences.append({
            'frame_pair': [i-1, i],
            'mean_difference': float(mean_diff),
            'max_difference': float(max_diff),
            'significant_change': mean_diff > 10.0
        })
        
        prev_gray = curr_gray
    
    # 分析结果
    total_significant_changes = sum(1 for d in differences if d['significant_change'])
    avg_motion_magnitude = np.mean([m.get('mean_magnitude', 0) for m in motion_vectors if 'mean_magnitude' in m])
    
    has_meaningful_motion = (
        total_significant_changes > len(differences) * 0.1 or
        avg_motion_magnitude > 0.5
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
    
    print("\n=== 运动矢量精度分析结果 ===")
    print(f"总帧数: {result['frame_count']}")
    print(f"分析的帧对: {result['analyzed_pairs']}")
    print(f"显著变化帧对: {result['summary']['total_significant_changes']}")
    print(f"平均运动幅度: {result['summary']['average_motion_magnitude']:.2f}")
    print(f"是否有有意义的运动: {result['summary']['has_meaningful_motion']}")
    print(f"运动类型: {result['summary']['motion_type']}")
    
    # 保存结果
    with open("/Users/zhufeng/My_AI_Body_副本/motion_precision_analysis.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\n结果已保存到 motion_precision_analysis.json")