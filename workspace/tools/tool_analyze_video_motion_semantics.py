# tool_name: analyze_video_motion_semantics

from langchain.tools import tool
import os
import json
import subprocess
import cv2
import numpy as np

@tool
def analyze_video_motion_semantics(video_path: str, output_dir: str = "./motion_analysis") -> dict:
    """
    完整的视频运动语义分析流程：
    1. 提取视频帧
    2. 分析帧间差异和运动向量
    3. 判断运动是否具有物理意义
    
    Args:
        video_path (str): 视频文件路径
        output_dir (str): 输出分析结果的目录
    
    Returns:
        dict: 包含完整运动语义分析结果的字典
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 第一步：提取视频帧
        frame_output_dir = os.path.join(output_dir, "extracted_frames")
        os.makedirs(frame_output_dir, exist_ok=True)
        
        # 使用ffmpeg提取帧（每0.5秒一帧）
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', 'fps=2',  # 每秒2帧（0.5秒间隔）
            '-y',
            os.path.join(frame_output_dir, 'frame_%04d.jpg')
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode != 0:
            return {
                'error': '帧提取失败',
                'video_path': video_path
            }
        
        # 获取提取的帧列表
        frame_files = sorted([f for f in os.listdir(frame_output_dir) if f.endswith('.jpg')])
        frame_paths = [os.path.join(frame_output_dir, f) for f in frame_files]
        
        if len(frame_paths) < 2:
            return {
                'error': '提取的帧数不足',
                'frame_count': len(frame_paths)
            }
        
        # 第二步：分析帧间差异 - 直接调用内部函数避免工具注册表问题
        def _analyze_frame_differences_internal(frame_paths, output_dir):
            """内部帧差异分析函数"""
            os.makedirs(output_dir, exist_ok=True)
            
            if not frame_paths or len(frame_paths) < 2:
                return {'error': '至少需要两个帧进行差异分析'}
            
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
                    'significant_change': mean_diff > 10.0
                })
                
                prev_gray = curr_gray
            
            # 分析整体运动模式
            total_significant_changes = sum(1 for d in differences if d['significant_change'])
            avg_motion_magnitude = np.mean([m.get('mean_magnitude', 0) for m in motion_vectors if 'mean_magnitude' in m])
            
            # 判断是否有有意义的运动
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
            
            # 保存结果到文件
            result_path = os.path.join(output_dir, 'frame_differences_analysis.json')
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            return result
        
        analysis_results = _analyze_frame_differences_internal(frame_paths, os.path.join(output_dir, "frame_analysis"))
        if 'error' in analysis_results:
            return {
                'error': f'帧差异分析失败: {analysis_results["error"]}',
                'video_path': video_path
            }
        
        # 第三步：综合语义分析
        if 'summary' in analysis_results:
            has_meaningful_motion = analysis_results['summary']['has_meaningful_motion']
            motion_density = analysis_results['summary']['average_motion_magnitude']
            significant_changes_ratio = analysis_results['summary']['total_significant_changes'] / max(1, analysis_results['analyzed_pairs'])
            
            # 判断语义连续性
            if has_meaningful_motion:
                if motion_density > 1.0 and significant_changes_ratio > 0.3:
                    semantic_conclusion = "视频包含丰富且有意义的运动，表明内容动态、连贯且具有物理意义"
                elif motion_density > 0.5 or significant_changes_ratio > 0.15:
                    semantic_conclusion = "视频包含适度的有意义运动，整体语义连贯"
                else:
                    semantic_conclusion = "视频运动较弱，但仍有基本的语义连续性"
            else:
                if significant_changes_ratio > 0.05:
                    semantic_conclusion = "视频主要为静态场景，但存在少量有意义的变化"
                else:
                    semantic_conclusion = "视频缺乏有意义的运动，可能为纯静态场景或存在修复问题"
            
            analysis_results['semantic_conclusion'] = semantic_conclusion
            analysis_results['is_semantically_valid'] = has_meaningful_motion
        
        # 保存完整结果
        results_path = os.path.join(output_dir, "motion_semantic_analysis.json")
        with open(results_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        return analysis_results
    except Exception as e:
        return {
            'error': str(e),
            'video_path': video_path
        }