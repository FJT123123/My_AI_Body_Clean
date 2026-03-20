# tool_name: frame_semantic_continuity_validator

from langchain.tools import tool
import os
import cv2
import numpy as np
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

@tool
def frame_semantic_continuity_validator(video_path: str, output_dir: str = "./semantic_continuity_analysis") -> Dict[str, Any]:
    """
    验证视频帧间语义连续性的完整工具
    
    分析视频中帧与帧之间的运动是否合理、变化是否有意义，
    判断视频内容是否具有物理意义和语义连贯性。
    
    Args:
        video_path (str): 输入视频文件路径
        output_dir (str): 输出分析结果的目录
        
    Returns:
        Dict[str, Any]: 包含语义连续性验证结果的字典
    """
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 第一步：提取视频帧
        frame_output_dir = os.path.join(output_dir, "extracted_frames")
        os.makedirs(frame_output_dir, exist_ok=True)
        
        # 使用ffmpeg提取帧（每0.5秒一帧，平衡精度和性能）
        cmd = [
            'ffmpeg', '-i', video_path,
            '-vf', 'fps=2',  # 每秒2帧（0.5秒间隔）
            '-y',
            os.path.join(frame_output_dir, 'frame_%04d.jpg')
        ]
        
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': '帧提取失败',
                'video_path': video_path
            }
        
        # 获取提取的帧列表
        frame_files = sorted([f for f in os.listdir(frame_output_dir) if f.endswith('.jpg')])
        frame_paths = [os.path.join(frame_output_dir, f) for f in frame_files]
        
        if len(frame_paths) < 2:
            return {
                'success': False,
                'error': '提取的帧数不足，无法进行帧间分析',
                'frame_count': len(frame_paths),
                'video_path': video_path
            }
        
        # 第二步：直接调用帧差异分析逻辑（不依赖工具注册表）
        analysis_results = _analyze_frame_differences_internal(frame_paths, os.path.join(output_dir, "frame_analysis"))
        
        if 'error' in analysis_results:
            return {
                'success': False,
                'error': f'帧差异分析失败: {analysis_results["error"]}',
                'video_path': video_path
            }
        
        # 第三步：综合语义分析
        has_meaningful_motion = analysis_results['summary']['has_meaningful_motion']
        motion_density = analysis_results['summary']['average_motion_magnitude']
        significant_changes_ratio = analysis_results['summary']['total_significant_changes'] / max(1, analysis_results['analyzed_pairs'])
        
        # 判断语义连续性
        if has_meaningful_motion:
            if motion_density > 1.0 and significant_changes_ratio > 0.3:
                semantic_conclusion = "视频包含丰富且有意义的运动，表明内容动态、连贯且具有物理意义"
                continuity_score = 0.9
            elif motion_density > 0.5 or significant_changes_ratio > 0.15:
                semantic_conclusion = "视频包含适度的有意义运动，整体语义连贯"
                continuity_score = 0.7
            else:
                semantic_conclusion = "视频运动较弱，但仍有基本的语义连续性"
                continuity_score = 0.5
        else:
            if significant_changes_ratio > 0.05:
                semantic_conclusion = "视频主要为静态场景，但存在少量有意义的变化"
                continuity_score = 0.4
            else:
                semantic_conclusion = "视频缺乏有意义的运动，可能为纯静态场景或存在修复问题"
                continuity_score = 0.2
        
        # 物理合理性检查
        physical_plausibility = _assess_physical_plausibility(analysis_results)
        
        final_result = {
            'success': True,
            'video_path': video_path,
            'is_semantically_valid': continuity_score >= 0.5,
            'continuity_score': continuity_score,
            'semantic_conclusion': semantic_conclusion,
            'physical_plausibility': physical_plausibility,
            'motion_analysis': analysis_results,
            'recommendations': _generate_recommendations(continuity_score, physical_plausibility)
        }
        
        # 保存完整结果
        results_path = os.path.join(output_dir, "semantic_continuity_analysis.json")
        with open(results_path, 'w') as f:
            json.dump(final_result, f, indent=2, default=str)
        
        return final_result
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': '处理超时',
            'video_path': video_path
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'语义连续性验证失败: {str(e)}',
            'video_path': video_path
        }

def _analyze_frame_differences_internal(frame_paths: List[str], output_dir: str) -> Dict[str, Any]:
    """内部帧差异分析函数，不依赖工具注册表"""
    try:
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
        
    except Exception as e:
        return {'error': str(e)}

def _assess_physical_plausibility(analysis_results: Dict) -> Dict[str, Any]:
    """评估运动的物理合理性"""
    try:
        motion_vectors = analysis_results.get('motion_vectors', [])
        if not motion_vectors:
            return {'is_plausible': True, 'reason': '无运动数据，视为静态场景'}
        
        # 提取有效的运动幅度
        magnitudes = [m.get('mean_magnitude', 0) for m in motion_vectors if 'mean_magnitude' in m]
        if not magnitudes:
            return {'is_plausible': True, 'reason': '无有效运动数据'}
        
        # 检查运动幅度的分布
        mean_mag = np.mean(magnitudes)
        std_mag = np.std(magnitudes) if len(magnitudes) > 1 else 0
        
        # 物理合理性判断：
        # 1. 运动幅度不应过大（避免跳帧或伪影）
        # 2. 运动变化应相对平滑（标准差不应过大）
        if mean_mag > 50:  # 过大的平均运动幅度可能表示问题
            return {
                'is_plausible': False,
                'reason': '平均运动幅度过大，可能存在跳帧或伪影',
                'mean_magnitude': float(mean_mag)
            }
        elif std_mag > mean_mag * 2 and mean_mag > 1:  # 运动变化过于剧烈
            return {
                'is_plausible': False,
                'reason': '运动幅度变化过于剧烈，缺乏物理连续性',
                'mean_magnitude': float(mean_mag),
                'std_magnitude': float(std_mag)
            }
        else:
            return {
                'is_plausible': True,
                'reason': '运动幅度和变化在合理范围内',
                'mean_magnitude': float(mean_mag),
                'std_magnitude': float(std_mag)
            }
            
    except Exception as e:
        return {'is_plausible': True, 'reason': f'物理合理性评估异常: {str(e)}'}

def _generate_recommendations(continuity_score: float, physical_plausibility: Dict) -> List[str]:
    """生成修复建议"""
    recommendations = []
    
    if continuity_score < 0.5:
        recommendations.append("视频缺乏有意义的运动，建议检查源视频质量或修复过程")
    
    if not physical_plausibility.get('is_plausible', True):
        recommendations.append("检测到物理不合理的运动模式，可能需要重新编码或修复")
    
    if continuity_score >= 0.5 and physical_plausibility.get('is_plausible', True):
        recommendations.append("视频具有良好的语义连续性和物理合理性")
    
    return recommendations