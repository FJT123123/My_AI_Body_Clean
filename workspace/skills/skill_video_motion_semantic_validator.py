"""
视频帧间运动语义验证技能
需求: 验证视频中帧与帧之间的运动是否合理、变化是否有意义，
判断视频内容是否具有物理意义和语义连贯性。
生成时间: 2026-03-20
"""

# skill_name: video_motion_semantic_validator

def main(args=None):
    """
    验证视频帧间运动语义连续性
    
    参数:
    - video_path: 输入视频文件路径
    - output_dir: 输出分析结果的目录（可选）
    """
    import os
    import sys
    import json
    import traceback
    
    # 添加 capabilities 目录到路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    capabilities_dir = os.path.join(current_dir, '..', 'capabilities')
    if os.path.exists(capabilities_dir):
        sys.path.insert(0, capabilities_dir)
    
    # 解析参数
    actual_args = {}
    if isinstance(args, dict) and 'input' in args:
        try:
            actual_args = json.loads(args['input'])
        except (json.JSONDecodeError, TypeError):
            actual_args = {}
    elif isinstance(args, str):
        try:
            actual_args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            actual_args = {}
    elif isinstance(args, dict):
        actual_args = args
    else:
        actual_args = {}
    
    # 获取参数
    video_path = actual_args.get('video_path')
    output_dir = actual_args.get('output_dir', './motion_semantic_analysis')
    
    if not video_path:
        return {
            'result': {'error': '缺少 video_path 参数'},
            'insights': ['参数校验失败：必须提供视频文件路径'],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'视频文件路径无效：{video_path}'],
            'facts': [],
            'memories': []
        }
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 尝试导入 OpenCV
    try:
        import cv2
    except ImportError:
        return {
            'result': {'error': 'OpenCV 未安装，请先安装 opencv-python'},
            'insights': ['需要安装 opencv-python 包才能进行运动分析'],
            'facts': [],
            'memories': ['OpenCV 依赖缺失，无法进行运动语义验证']
        }
    
    # 尝试导入 capability
    try:
        from motion_semantic_validation_capability import check_video_motion_semantics
    except ImportError as e:
        # 如果无法导入 capability，直接实现核心功能
        try:
            import numpy as np
            
            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return {
                    'result': {'error': '无法打开视频文件'},
                    'insights': ['视频文件可能损坏或格式不受支持'],
                    'facts': [],
                    'memories': [f'无法打开视频文件：{video_path}']
                }
            
            # 提取关键帧
            frames = []
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % 5 == 0:  # 每5帧提取一帧
                    frames.append(frame.copy())
                
                frame_count += 1
            
            cap.release()
            
            if len(frames) < 2:
                return {
                    'result': {'error': '视频帧数不足，无法进行运动分析'},
                    'insights': ['视频太短或帧率太低，无法进行有效的运动分析'],
                    'facts': [],
                    'memories': [f'视频帧数不足：{video_path}']
                }
            
            # 计算帧间光流
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
            
            if not flows:
                return {
                    'result': {'error': '无法计算光流'},
                    'insights': ['光流计算失败，可能是帧质量或内容问题'],
                    'facts': [],
                    'memories': [f'光流计算失败：{video_path}']
                }
            
            # 分析运动一致性
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
            
        except Exception as inner_e:
            return {
                'result': {'error': f'运动语义验证失败: {str(inner_e)}'},
                'insights': [f'运动语义验证过程中发生错误：{str(inner_e)}'],
                'facts': [],
                'memories': [f'运动语义验证失败：{video_path}，错误：{str(inner_e)}']
            }
    else:
        # 使用 capability 模块
        try:
            result = check_video_motion_semantics(video_path)
        except Exception as e:
            return {
                'result': {'error': f'capability 模块执行失败: {str(e)}'},
                'insights': [f'capability 模块执行异常：{str(e)}'],
                'facts': [],
                'memories': [f'capability 模块执行失败：{video_path}，错误：{str(e)}']
            }
    
    # 确保结果可以JSON序列化
    def ensure_json_serializable(obj):
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, dict):
            return {key: ensure_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [ensure_json_serializable(item) for item in obj]
        else:
            return obj
    
    serializable_result = ensure_json_serializable(result)
    
    # 保存结果到文件
    result_path = os.path.join(output_dir, 'motion_semantic_validation_result.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(serializable_result, f, ensure_ascii=False, indent=2)
    
    # 准备返回结果
    if result.get('success', False):
        validation_result = result.get('validation_result', {})
        overall_valid = validation_result.get('overall_valid', False)
        
        insights = [
            f"视频帧间运动语义验证完成",
            f"总体有效性: {'有效' if overall_valid else '无效'}",
            f"语义一致性: {'是' if validation_result.get('semantic_consistency', False) else '否'}",
            f"物理合理性: {'是' if validation_result.get('physical_plausibility', False) else '否'}"
        ]
        
        facts = [
            ['视频', '运动语义验证结果', '完成'],
            ['视频', '总体有效性', '有效' if overall_valid else '无效'],
            [video_path, '处理结果', '成功']
        ]
        
        memories = [
            f"视频运动语义验证完成，源视频：{video_path}，结果：{'有效' if overall_valid else '无效'}"
        ]
    else:
        error_msg = result.get('error', '未知错误')
        insights = [f"视频帧间运动语义验证失败: {error_msg}"]
        facts = []
        memories = [f"视频运动语义验证失败，源视频：{video_path}，错误：{error_msg}"]
    
    return {
        'result': serializable_result,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }