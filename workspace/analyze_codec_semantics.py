import os
import glob
import cv2
import numpy as np
import json

def analyze_codec_physical_semantics(frame_dir, output_dir):
    """
    分析编解码器的物理语义，特别是H.264的帧间预测和运动补偿
    """
    # 获取所有帧文件
    frame_pattern = os.path.join(frame_dir, "frame_*.jpg")
    frame_paths = sorted(glob.glob(frame_pattern))
    
    if not frame_paths:
        return {"error": "No frames found in directory"}
    
    print(f"Found {len(frame_paths)} frames")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 分析前几帧的差异
    results = {
        "frame_count": len(frame_paths),
        "motion_analysis": [],
        "physical_semantics": {
            "inter_frame_prediction": "H.264 uses inter-frame prediction to reduce temporal redundancy",
            "motion_compensation": "Motion vectors describe how blocks move between frames",
            "quantization_effects": "Higher quantization reduces quality but increases compression"
        }
    }
    
    # 计算帧间差异
    prev_frame = None
    for i, frame_path in enumerate(frame_paths[:10]):  # 只分析前10帧
        frame = cv2.imread(frame_path)
        if frame is None:
            continue
            
        if prev_frame is not None:
            # 计算绝对差异
            diff = cv2.absdiff(frame, prev_frame)
            mean_diff = np.mean(diff)
            max_diff = np.max(diff)
            
            # 计算运动能量（差异的平方和）
            motion_energy = np.sum(diff.astype(np.float64) ** 2)
            
            motion_info = {
                "frame_pair": [i-1, i],
                "mean_difference": float(mean_diff),
                "max_difference": int(max_diff),
                "motion_energy": float(motion_energy),
                "has_significant_motion": mean_diff > 5.0  # 阈值
            }
            
            results["motion_analysis"].append(motion_info)
        
        prev_frame = frame
    
    # 保存结果
    with open(os.path.join(output_dir, "codec_semantics_analysis.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    result = analyze_codec_physical_semantics(
        "./extracted_frames_for_codec_analysis", 
        "./codec_semantics_results"
    )
    print(json.dumps(result, indent=2))