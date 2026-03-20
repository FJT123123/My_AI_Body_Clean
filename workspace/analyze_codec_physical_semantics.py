import cv2
import numpy as np
import os
import json

# 帧路径
frame_paths = [
    "/Users/zhufeng/My_AI_Body_副本/extracted_frames_for_codec_analysis/frame_0001.jpg",
    "/Users/zhufeng/My_AI_Body_副本/extracted_frames_for_codec_analysis/frame_0002.jpg",
    "/Users/zhufeng/My_AI_Body_副本/extracted_frames_for_codec_analysis/frame_0003.jpg",
    "/Users/zhufeng/My_AI_Body_副本/extracted_frames_for_codec_analysis/frame_0004.jpg",
    "/Users/zhufeng/My_AI_Body_副本/extracted_frames_for_codec_analysis/frame_0005.jpg"
]

# 创建输出目录
output_dir = "./codec_physical_semantics_analysis"
os.makedirs(output_dir, exist_ok=True)

results = {
    "frame_count": len(frame_paths),
    "motion_analysis": [],
    "physical_semantics": {
        "inter_frame_prediction": "H.264 uses inter-frame prediction to reduce temporal redundancy by predicting current frame from previous frames",
        "motion_compensation": "Motion vectors describe displacement of macroblocks between frames, enabling efficient compression",
        "quantization_effects": "Quantization matrices control quality vs compression trade-off; higher quantization reduces detail but increases compression ratio",
        "codec_specifics": "H.264 (AVC) uses 4x4 and 8x8 transform blocks with adaptive quantization for optimal compression"
    }
}

prev_frame = None
for i, frame_path in enumerate(frame_paths):
    if not os.path.exists(frame_path):
        print(f"Frame not found: {frame_path}")
        continue
        
    frame = cv2.imread(frame_path)
    if frame is None:
        print(f"Could not read frame: {frame_path}")
        continue
        
    if prev_frame is not None:
        # 计算绝对差异
        diff = cv2.absdiff(frame, prev_frame)
        mean_diff = np.mean(diff)
        max_diff = np.max(diff)
        
        # 计算运动能量
        motion_energy = np.sum(diff.astype(np.float64) ** 2)
        
        # 计算光流（简化版）
        gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        mean_magnitude = np.mean(magnitude)
        
        motion_info = {
            "frame_pair": [i-1, i],
            "mean_difference": float(mean_diff),
            "max_difference": int(max_diff),
            "motion_energy": float(motion_energy),
            "mean_optical_flow_magnitude": float(mean_magnitude),
            "has_significant_motion": mean_diff > 5.0 or mean_magnitude > 0.5
        }
        
        results["motion_analysis"].append(motion_info)
        print(f"Frame {i-1} -> {i}: mean_diff={mean_diff:.2f}, motion_energy={motion_energy:.2f}, flow_mag={mean_magnitude:.2f}")
    
    prev_frame = frame

# 保存结果
with open(os.path.join(output_dir, "codec_physical_semantics.json"), "w") as f:
    json.dump(results, f, indent=2)

print("Analysis completed!")
print(f"Results saved to {output_dir}/codec_physical_semantics.json")