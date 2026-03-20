# tool_name: video_processing_automatic_repair_and_validation_workflow

import json
import os
from typing import Dict, Any
from langchain.tools import tool

@tool
def video_processing_automatic_repair_and_validation_workflow(input_args: str) -> Dict[str, Any]:
    """
    视频处理自动修复和验证工作流
    
    用途: 接收视频处理错误信息，自动执行完整的诊断->修复->验证闭环流程
    参数: input_args - JSON字符串，包含以下必需和可选参数:
        - error_info (str, required): 原始错误信息
        - video_path (str, required): 出现问题的视频文件路径
        - context (dict, optional): 上下文信息
        - output_dir (str, optional): 输出目录，默认为当前目录
        
    返回值: 包含完整工作流执行结果的字典，包括:
        - workflow_status: 工作流整体状态 ('success', 'partial_success', 'failed')
        - error_mapping_result: 错误映射结果
        - repair_result: 修复结果
        - validation_result: 验证结果
        - final_video_path: 最终修复后的视频路径
        - insights: 执行过程中的见解
        - facts: 可存储的事实
        - memories: 可存储的记忆
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args) if input_args else {}
        else:
            params = input_args if isinstance(input_args, dict) else {}
        
        # 验证必需参数
        error_info = params.get('error_info')
        video_path = params.get('video_path')
        
        if not error_info:
            return {
                'result': {'error': '缺少 error_info 参数'},
                'insights': ['参数校验失败：必须提供error_info'],
                'facts': [],
                'memories': []
            }
            
        if not video_path:
            return {
                'result': {'error': '缺少 video_path 参数'},
                'insights': ['参数校验失败：必须提供video_path'],
                'facts': [],
                'memories': []
            }
            
        if not os.path.exists(video_path):
            return {
                'result': {'error': f'视频文件不存在: {video_path}'},
                'insights': ['指定的视频文件路径不存在'],
                'facts': [],
                'memories': []
            }
        
        output_dir = params.get('output_dir', './video_repair_workflow_output')
        context = params.get('context', {})
        
        # 步骤1: 错误映射
        from workspace.tools.tool_video_processing_error_mapper import video_processing_error_mapper
        
        error_mapper_input = json.dumps({
            'error_info': error_info,
            'video_path': video_path,
            'context': context
        })
        
        error_mapping_result = video_processing_error_mapper(error_mapper_input)
        
        # 检查错误映射是否成功
        if error_mapping_result.get('status') != 'success':
            return {
                'result': {
                    'workflow_status': 'failed',
                    'error_mapping_result': error_mapping_result,
                    'repair_result': None,
                    'validation_result': None,
                    'final_video_path': None
                },
                'insights': ['错误映射失败，无法继续修复流程'],
                'facts': [['video_repair_workflow', 'status', 'error_mapping_failed']],
                'memories': [f'视频修复工作流失败: 错误映射失败 - {video_path}']
            }
        
        # 提取错误类型和建议
        mapped_error = error_mapping_result.get('result', {})
        error_type = mapped_error.get('error_type', 'UnknownError')
        suggestions = mapped_error.get('suggestions', [])
        
        # 步骤2: 自动修复
        from workspace.tools.tool_smart_video_repair_tool import smart_video_repair_tool
        
        # 根据错误类型和建议确定修复参数
        repair_params = {
            'input_video_path': video_path,
            'force_repair': True
        }
        
        # 如果建议中包含特定修复指令，添加到参数中
        if any('audio' in str(suggestion).lower() for suggestion in suggestions):
            repair_params['add_silent_audio'] = True
            
        if any('codec' in str(suggestion).lower() for suggestion in suggestions):
            repair_params['target_codec'] = 'h264'
        
        base_name = os.path.splitext(video_path)[0]
        repair_params['output_video_path'] = f"{base_name}_auto_repaired.mp4"
        
        repair_input = json.dumps(repair_params)
        repair_result = smart_video_repair_tool(repair_input)
        
        # 检查修复是否成功
        if not repair_result.get('result', {}).get('success', False):
            return {
                'result': {
                    'workflow_status': 'failed',
                    'error_mapping_result': error_mapping_result,
                    'repair_result': repair_result,
                    'validation_result': None,
                    'final_video_path': None
                },
                'insights': ['视频修复失败，无法继续验证流程'],
                'facts': [['video_repair_workflow', 'status', 'repair_failed']],
                'memories': [f'视频修复工作流失败: 修复失败 - {video_path}']
            }
        
        repaired_video_path = repair_result['result']['repaired_video_path']
        
        # 步骤3: 验证修复结果（语义连续性）
        from workspace.tools.tool_video_semantic_continuity_analyzer import video_semantic_continuity_analyzer
        
        validation_output_dir = os.path.join(output_dir, 'validation_results')
        continuity_validation_result = video_semantic_continuity_analyzer(repaired_video_path, validation_output_dir)
        
        # 步骤4: 验证语义一致性（确保修复没有改变原始语义）
        consistency_validation_result = {'success': True, 'is_semantically_consistent': True, 'consistency_score': 1.0}
        try:
            # 复用现有的运动语义验证能力进行一致性比较
            import cv2
            import numpy as np
            from scipy.spatial.distance import cosine
            
            def _extract_key_frames(video_path, max_frames=8):
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return None
                
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                frames = []
                
                if total_frames <= max_frames:
                    frame_indices = list(range(total_frames))
                else:
                    step = total_frames // max_frames
                    frame_indices = [i * step for i in range(max_frames)]
                    if frame_indices[-1] != total_frames - 1:
                        frame_indices[-1] = total_frames - 1
                
                for idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        frames.append(frame)
                
                cap.release()
                return frames if frames else None
            
            def _calculate_frame_similarity(frame1, frame2):
                if frame1 is None or frame2 is None:
                    return 0.0
                
                h1, w1 = frame1.shape[:2]
                h2, w2 = frame2.shape[:2]
                min_h, min_w = min(h1, h2), min(w1, w2)
                
                if min_h == 0 or min_w == 0:
                    return 0.0
                
                resized_frame1 = cv2.resize(frame1[:min_h, :min_w], (min_w, min_h))
                resized_frame2 = cv2.resize(frame2[:min_h, :min_w], (min_w, min_h))
                
                gray1 = cv2.cvtColor(resized_frame1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(resized_frame2, cv2.COLOR_BGR2GRAY)
                
                try:
                    correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
                    return max(0.0, float(correlation))
                except:
                    mse = np.mean((gray1.astype(float) - gray2.astype(float)) ** 2)
                    if mse == 0:
                        return 1.0
                    return max(0.0, 1.0 - (mse / (255.0 ** 2)))
            
            def _extract_motion_signature(frames):
                if len(frames) < 2:
                    return []
                
                motion_magnitudes = []
                prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
                
                for i in range(1, len(frames)):
                    curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                    try:
                        flow = cv2.calcOpticalFlowFarneback(
                            prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
                        )
                        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                        motion_magnitudes.append(np.mean(magnitude))
                    except:
                        motion_magnitudes.append(0.0)
                    prev_gray = curr_gray
                
                return motion_magnitudes
            
            def _calculate_motion_similarity(orig_motion, repaired_motion):
                if len(orig_motion) == 0 or len(repaired_motion) == 0:
                    return 0.0
                
                min_len = min(len(orig_motion), len(repaired_motion))
                if min_len == 0:
                    return 0.0
                
                orig_vec = np.array(orig_motion[:min_len])
                repaired_vec = np.array(repaired_motion[:min_len])
                
                if np.linalg.norm(orig_vec) == 0 or np.linalg.norm(repaired_vec) == 0:
                    return 1.0 if np.allclose(orig_vec, repaired_vec) else 0.0
                
                orig_norm = orig_vec / np.linalg.norm(orig_vec)
                repaired_norm = repaired_vec / np.linalg.norm(repaired_vec)
                
                similarity = 1.0 - cosine(orig_norm, repaired_norm)
                return max(0.0, min(1.0, float(similarity)))
            
            # 执行一致性验证
            orig_frames = _extract_key_frames(video_path)
            repaired_frames = _extract_key_frames(repaired_video_path)
            
            if orig_frames is not None and repaired_frames is not None and len(orig_frames) > 0 and len(repaired_frames) > 0:
                min_frames = min(len(orig_frames), len(repaired_frames))
                frame_similarities = []
                
                for i in range(min_frames):
                    similarity = _calculate_frame_similarity(orig_frames[i], repaired_frames[i])
                    frame_similarities.append(similarity)
                
                avg_frame_similarity = np.mean(frame_similarities) if frame_similarities else 0.0
                
                orig_motion = _extract_motion_signature(orig_frames)
                repaired_motion = _extract_motion_signature(repaired_frames)
                motion_similarity = _calculate_motion_similarity(orig_motion, repaired_motion)
                
                consistency_score = (avg_frame_similarity * 0.6 + motion_similarity * 0.4)
                is_consistent = consistency_score >= 0.7
                
                consistency_validation_result = {
                    'success': True,
                    'is_semantically_consistent': bool(is_consistent),
                    'consistency_score': float(consistency_score),
                    'semantic_preservation_ratio': float(avg_frame_similarity),
                    'motion_pattern_similarity': float(motion_similarity),
                    'key_scene_preservation': sum(1 for s in frame_similarities if s >= 0.8) / len(frame_similarities) if frame_similarities else 0.0
                }
            else:
                consistency_validation_result = {
                    'success': False,
                    'error': '无法提取帧进行一致性比较',
                    'is_semantically_consistent': False,
                    'consistency_score': 0.0
                }
                
        except Exception as e:
            consistency_validation_result = {
                'success': False,
                'error': f'语义一致性验证异常: {str(e)}',
                'is_semantically_consistent': False,
                'consistency_score': 0.0
            }
        
        # 确定工作流最终状态
        workflow_status = 'success'
        if not continuity_validation_result.get('success', False) or not consistency_validation_result.get('success', False):
            workflow_status = 'partial_success'  # 修复成功但验证失败
        elif continuity_validation_result.get('is_semantically_valid', False) and consistency_validation_result.get('is_semantically_consistent', False):
            workflow_status = 'success'
        else:
            workflow_status = 'partial_success'  # 修复成功但语义验证不通过
        
        # 构建最终结果
        final_result = {
            'workflow_status': workflow_status,
            'error_mapping_result': error_mapping_result,
            'repair_result': repair_result['result'],
            'continuity_validation_result': continuity_validation_result,
            'consistency_validation_result': consistency_validation_result,
            'final_video_path': repaired_video_path,
            'original_video_path': video_path,
            'error_type': error_type,
            'applied_fixes': repair_result['result'].get('applied_fixes', []),
            'continuity_score': continuity_validation_result.get('continuity_score', 0.0),
            'is_semantically_valid': continuity_validation_result.get('is_semantically_valid', False),
            'consistency_score': consistency_validation_result.get('consistency_score', 0.0),
            'is_semantically_consistent': consistency_validation_result.get('is_semantically_consistent', False)
        }
        
        # 生成见解
        insights = [
            f'视频修复工作流完成: {video_path} -> {repaired_video_path}',
            f'检测到的错误类型: {error_type}',
            f'应用的修复措施: {", ".join(repair_result["result"].get("applied_fixes", ["无"]))}',
            f'语义连续性得分: {continuity_validation_result.get("continuity_score", 0.0):.2f}',
            f'语义一致性得分: {consistency_validation_result.get("consistency_score", 0.0):.2f}',
            f'工作流状态: {workflow_status}'
        ]
        
        # 生成事实
        facts = [
            ['video_repair_workflow', 'input_path', video_path],
            ['video_repair_workflow', 'output_path', repaired_video_path],
            ['video_repair_workflow', 'error_type', error_type],
            ['video_repair_workflow', 'status', workflow_status],
            ['video_repair_workflow', 'continuity_score', str(continuity_validation_result.get('continuity_score', 0.0))],
            ['video_repair_workflow', 'is_semantically_valid', str(continuity_validation_result.get('is_semantically_valid', False))],
            ['video_repair_workflow', 'consistency_score', str(consistency_validation_result.get('consistency_score', 0.0))],
            ['video_repair_workflow', 'is_semantically_consistent', str(consistency_validation_result.get('is_semantically_consistent', False))]
        ]
        
        # 生成记忆
        memories = [
            f'视频修复工作流成功: {video_path} -> {repaired_video_path}, 错误类型: {error_type}, 状态: {workflow_status}'
        ]
        
        return {
            'result': final_result,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except Exception as e:
        return {
            'result': {'error': f'工作流执行异常: {str(e)}'},
            'insights': [f'视频修复工作流执行异常: {str(e)}'],
            'facts': [['video_repair_workflow', 'status', 'exception']],
            'memories': [f'视频修复工作流异常: {video_path} - {str(e)}']
        }