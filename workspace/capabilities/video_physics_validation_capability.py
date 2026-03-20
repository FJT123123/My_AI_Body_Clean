# capability_name: video_physics_validation_capability

def validate_video_frame_physics_compliance(video_path, output_dir=None, config=None):
    """
    验证视频帧间物理约束合规性
    
    Args:
        video_path (str): 输入视频文件路径
        output_dir (str, optional): 输出分析结果的目录
        config (dict, optional): 验证配置参数
        
    Returns:
        dict: 包含物理约束验证结果的字典
    """
    try:
        import os
        import json
        import cv2
        import numpy as np
        from pathlib import Path
        
        # 默认配置
        default_config = {
            'max_motion_magnitude': 30.0,
            'motion_consistency_threshold': 0.7,
            'temporal_coherence_threshold': 0.8,
            'frame_sample_rate': 5,
            'min_frames_for_analysis': 10
        }
        
        if config is None:
            config = default_config
        else:
            # 合并配置
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
        
        # 创建输出目录
        if output_dir is None:
            output_dir = "./physics_validation"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 打开视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {
                'success': False,
                'error': '无法打开视频文件',
                'validation_result': None
            }
        
        # 获取视频基本信息
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 提取帧进行分析
        frames = []
        frame_indices = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 按采样率提取帧
            if frame_count % config['frame_sample_rate'] == 0:
                frames.append(frame.copy())
                frame_indices.append(frame_count)
            
            frame_count += 1
        
        cap.release()
        
        if len(frames) < config['min_frames_for_analysis']:
            return {
                'success': False,
                'error': f'视频帧数不足 ({len(frames)} < {config["min_frames_for_analysis"]})，无法进行有效分析',
                'validation_result': None
            }
        
        # 计算帧间光流和运动向量
        flows = []
        magnitudes = []
        directions = []
        
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # 使用Farneback光流算法
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
            
            # 计算幅度和方向
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            direction = np.arctan2(flow[..., 1], flow[..., 0])
            
            avg_magnitude = float(np.mean(magnitude))
            flows.append(flow)
            magnitudes.append(avg_magnitude)
            directions.append(np.mean(direction))
        
        # 物理约束验证
        
        # 1. 运动幅度合理性检查
        avg_motion_magnitude = float(np.mean(magnitudes))
        motion_magnitude_valid = avg_motion_magnitude <= config['max_motion_magnitude']
        
        # 2. 运动一致性检查
        if len(magnitudes) > 1:
            magnitude_std = float(np.std(magnitudes))
            motion_consistency_score = 1.0 - (magnitude_std / (avg_motion_magnitude + 1e-8))
            motion_consistency_valid = motion_consistency_score >= config['motion_consistency_threshold']
        else:
            motion_consistency_score = 1.0
            motion_consistency_valid = True
        
        # 3. 时间相干性检查（基于方向变化）
        if len(directions) > 1:
            direction_changes = []
            for i in range(1, len(directions)):
                # 计算方向差（考虑角度环绕）
                dir_diff = abs(directions[i] - directions[i-1])
                dir_diff = min(dir_diff, 2*np.pi - dir_diff)
                direction_changes.append(dir_diff)
            
            avg_direction_change = float(np.mean(direction_changes))
            temporal_coherence_score = 1.0 - (avg_direction_change / np.pi)
            temporal_coherence_valid = temporal_coherence_score >= config['temporal_coherence_threshold']
        else:
            temporal_coherence_score = 1.0
            temporal_coherence_valid = True
        
        # 4. 异常运动检测
        motion_jumps = 0
        jump_threshold = avg_motion_magnitude * 1.5 if avg_motion_magnitude > 0 else 0.1
        for i in range(1, len(magnitudes)):
            if abs(magnitudes[i] - magnitudes[i-1]) > jump_threshold:
                motion_jumps += 1
        
        anomaly_detected = motion_jumps > len(magnitudes) * 0.2  # 超过20%的帧有跳跃
        
        # 综合验证结果
        overall_valid = (
            motion_magnitude_valid and 
            motion_consistency_valid and 
            temporal_coherence_valid and 
            not anomaly_detected
        )
        
        validation_result = {
            'video_info': {
                'path': video_path,
                'fps': fps,
                'total_frames': total_frames,
                'width': width,
                'height': height,
                'analyzed_frames': len(frames)
            },
            'motion_analysis': {
                'avg_motion_magnitude': avg_motion_magnitude,
                'motion_magnitude_valid': motion_magnitude_valid,
                'motion_consistency_score': motion_consistency_score,
                'motion_consistency_valid': motion_consistency_valid,
                'temporal_coherence_score': temporal_coherence_score,
                'temporal_coherence_valid': temporal_coherence_valid,
                'motion_jumps': motion_jumps,
                'anomaly_detected': anomaly_detected
            },
            'physical_constraints': {
                'motion_magnitude_constraint': f"<= {config['max_motion_magnitude']}",
                'motion_consistency_threshold': config['motion_consistency_threshold'],
                'temporal_coherence_threshold': config['temporal_coherence_threshold']
            },
            'overall_valid': overall_valid,
            'confidence_score': float(np.mean([
                float(motion_magnitude_valid),
                motion_consistency_score,
                temporal_coherence_score,
                float(not anomaly_detected)
            ]))
        }
        
        # 保存详细结果
        result_path = os.path.join(output_dir, 'physics_validation_result.json')
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(validation_result, f, ensure_ascii=False, indent=2)
        
        return {
            'success': True,
            'error': None,
            'validation_result': validation_result
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'validation_result': None
        }