# tool_name: enhanced_video_repair_validation_workflow

import json
import os
from typing import Dict, Any
from langchain.tools import tool

@tool
def enhanced_video_repair_validation_workflow(input_args: str) -> Dict[str, Any]:
    """
    增强版视频处理自动修复和验证工作流
    
    用途: 接收视频处理错误信息，自动执行完整的诊断->修复->验证闭环流程，
          包含多级错误分类、自适应修复策略和多层次验证机制
    参数: input_args - JSON字符串，包含以下必需和可选参数:
        - error_info (str, required): 原始错误信息
        - video_path (str, required): 出现问题的视频文件路径
        - context (dict, optional): 上下文信息
        - output_dir (str, optional): 输出目录，默认为当前目录
        - repair_strategy (str, optional): 修复策略 ('conservative', 'aggressive', 'balanced')，默认'balanced'
        
    返回值: 包含完整工作流执行结果的字典，包括:
        - workflow_status: 工作流整体状态 ('success', 'partial_success', 'failed')
        - error_mapping_result: 错误映射结果（使用增强版映射器）
        - repair_result: 修复结果
        - validation_results: 多层次验证结果（语义连续性、物理一致性、内容完整性）
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
        
        output_dir = params.get('output_dir', './enhanced_video_repair_workflow_output')
        context = params.get('context', {})
        repair_strategy = params.get('repair_strategy', 'balanced')  # 'conservative', 'aggressive', 'balanced'
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 步骤1: 使用增强版错误映射器进行精细化错误分类
        from workspace.tools.tool_enhanced_video_processing_error_mapper import enhanced_video_processing_error_mapper
        
        error_mapper_input = json.dumps({
            'error_info': error_info,
            'video_path': video_path,
            'context': context
        })
        
        error_mapping_result = enhanced_video_processing_error_mapper(error_mapper_input)
        
        # 检查错误映射是否成功
        if error_mapping_result.get('status') != 'success':
            return {
                'result': {
                    'workflow_status': 'failed',
                    'error_mapping_result': error_mapping_result,
                    'repair_result': None,
                    'validation_results': None,
                    'final_video_path': None
                },
                'insights': ['增强版错误映射失败，无法继续修复流程'],
                'facts': [['enhanced_video_repair_workflow', 'status', 'error_mapping_failed']],
                'memories': [f'增强版视频修复工作流失败: 错误映射失败 - {video_path}']
            }
        
        # 提取错误类型和建议
        mapped_error = error_mapping_result.get('result', {})
        error_type = mapped_error.get('error_type', 'UnknownError')
        suggestions = mapped_error.get('suggestions', [])
        confidence_score = mapped_error.get('confidence_score', 0.0)
        
        # 步骤2: 自适应修复策略选择
        repair_params = {
            'input_video_path': video_path,
            'force_repair': True
        }
        
        # 根据错误类型、置信度和修复策略调整修复参数
        if confidence_score > 0.8 or repair_strategy == 'aggressive':
            # 高置信度或激进策略：应用所有可能的修复
            if any('audio' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['add_silent_audio'] = True
                
            if any('codec' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['target_codec'] = 'h264'
                
            if any('resolution' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['target_resolution'] = '1920x1080'
                
            if any('framerate' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['target_framerate'] = 30.0
                
        elif confidence_score < 0.5 and repair_strategy == 'conservative':
            # 低置信度且保守策略：只应用最安全的修复
            if any('audio' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['add_silent_audio'] = True
        else:
            # 平衡策略：基于具体错误类型应用修复
            if any('audio' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['add_silent_audio'] = True
                
            if any('codec' in str(suggestion).lower() for suggestion in suggestions):
                repair_params['target_codec'] = 'h264'
        
        base_name = os.path.splitext(video_path)[0]
        repair_params['output_video_path'] = f"{base_name}_enhanced_repaired.mp4"
        
        # 步骤3: 执行修复
        from workspace.tools.tool_smart_video_repair_tool import smart_video_repair_tool
        
        repair_input = json.dumps(repair_params)
        repair_result = smart_video_repair_tool(repair_input)
        
        # 检查修复是否成功
        if not repair_result.get('result', {}).get('success', False):
            return {
                'result': {
                    'workflow_status': 'failed',
                    'error_mapping_result': error_mapping_result,
                    'repair_result': repair_result,
                    'validation_results': None,
                    'final_video_path': None
                },
                'insights': ['视频修复失败，无法继续验证流程'],
                'facts': [['enhanced_video_repair_workflow', 'status', 'repair_failed']],
                'memories': [f'增强版视频修复工作流失败: 修复失败 - {video_path}']
            }
        
        repaired_video_path = repair_result['result']['repaired_video_path']
        
        # 步骤4: 多层次验证
        
        # 4.1 语义连续性验证
        from workspace.tools.tool_video_semantic_continuity_analyzer import video_semantic_continuity_analyzer
        continuity_output_dir = os.path.join(output_dir, 'continuity_validation')
        continuity_validation_result = video_semantic_continuity_analyzer(repaired_video_path, continuity_output_dir)
        
        # 4.2 物理一致性验证（端到端回归验证）
        from workspace.tools.tool_video_frame_physics_compliance_end_to_end_regression_validation import video_frame_physics_compliance_end_to_end_regression_validation
        physics_output_dir = os.path.join(output_dir, 'physics_validation')
        physics_validation_result = video_frame_physics_compliance_end_to_end_regression_validation(
            video_path=repaired_video_path,
            output_dir=physics_output_dir
        )
        
        # 4.3 内容完整性验证（与原始视频比较）
        content_validation_result = {'success': True, 'content_integrity_score': 1.0, 'is_content_preserved': True}
        try:
            import cv2
            import numpy as np
            
            def _calculate_video_similarity_metrics(orig_path, repaired_path):
                cap_orig = cv2.VideoCapture(orig_path)
                cap_repaired = cv2.VideoCapture(repaired_path)
                
                if not cap_orig.isOpened() or not cap_repaired.isOpened():
                    return {'success': False, 'error': '无法打开视频文件'}
                
                orig_fps = cap_orig.get(cv2.CAP_PROP_FPS)
                repaired_fps = cap_repaired.get(cv2.CAP_PROP_FPS)
                orig_frame_count = int(cap_orig.get(cv2.CAP_PROP_FRAME_COUNT))
                repaired_frame_count = int(cap_repaired.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # 计算帧数比率
                frame_count_ratio = repaired_frame_count / max(orig_frame_count, 1)
                
                # 提取关键帧进行比较
                sample_count = min(10, orig_frame_count, repaired_frame_count)
                if sample_count <= 0:
                    return {'success': False, 'error': '视频帧数不足'}
                
                frame_step_orig = max(1, orig_frame_count // sample_count)
                frame_step_repaired = max(1, repaired_frame_count // sample_count)
                
                similarities = []
                for i in range(sample_count):
                    # 读取原始视频帧
                    cap_orig.set(cv2.CAP_PROP_POS_FRAMES, i * frame_step_orig)
                    ret_orig, frame_orig = cap_orig.read()
                    
                    # 读取修复后视频帧
                    cap_repaired.set(cv2.CAP_PROP_POS_FRAMES, i * frame_step_repaired)
                    ret_repaired, frame_repaired = cap_repaired.read()
                    
                    if ret_orig and ret_repaired and frame_orig is not None and frame_repaired is not None:
                        # 调整尺寸以匹配
                        h_orig, w_orig = frame_orig.shape[:2]
                        h_repaired, w_repaired = frame_repaired.shape[:2]
                        min_h, min_w = min(h_orig, h_repaired), min(w_orig, w_repaired)
                        
                        if min_h > 0 and min_w > 0:
                            resized_orig = cv2.resize(frame_orig[:min_h, :min_w], (min_w, min_h))
                            resized_repaired = cv2.resize(frame_repaired[:min_h, :min_w], (min_w, min_h))
                            
                            # 计算结构相似性
                            gray_orig = cv2.cvtColor(resized_orig, cv2.COLOR_BGR2GRAY)
                            gray_repaired = cv2.cvtColor(resized_repaired, cv2.COLOR_BGR2GRAY)
                            
                            # 使用简单的MSE计算相似度
                            mse = np.mean((gray_orig.astype(float) - gray_repaired.astype(float)) ** 2)
                            if mse == 0:
                                similarity = 1.0
                            else:
                                similarity = max(0.0, 1.0 - (mse / (255.0 ** 2)))
                            similarities.append(similarity)
                
                cap_orig.release()
                cap_repaired.release()
                
                if not similarities:
                    return {'success': False, 'error': '无法计算帧相似度'}
                
                avg_similarity = np.mean(similarities)
                content_preservation = avg_similarity >= 0.7
                
                return {
                    'success': True,
                    'content_integrity_score': float(avg_similarity),
                    'is_content_preserved': bool(content_preservation),
                    'frame_count_ratio': float(frame_count_ratio),
                    'fps_ratio': float(repaired_fps / max(orig_fps, 1)),
                    'sampled_frames': len(similarities)
                }
            
            content_validation_result = _calculate_video_similarity_metrics(video_path, repaired_video_path)
            
        except Exception as e:
            content_validation_result = {
                'success': False,
                'error': f'内容完整性验证异常: {str(e)}',
                'content_integrity_score': 0.0,
                'is_content_preserved': False
            }
        
        # 步骤5: 综合评估工作流状态
        workflow_status = 'success'
        
        # 检查各个验证步骤的成功状态
        continuity_success = continuity_validation_result.get('success', False) and continuity_validation_result.get('is_semantically_valid', False)
        physics_success = physics_validation_result.get('result', {}).get('overall_validation_passed', False)
        content_success = content_validation_result.get('success', False) and content_validation_result.get('is_content_preserved', False)
        
        if not (continuity_success or physics_success or content_success):
            workflow_status = 'failed'
        elif continuity_success and physics_success and content_success:
            workflow_status = 'success'
        else:
            workflow_status = 'partial_success'
        
        # 构建最终结果
        final_result = {
            'workflow_status': workflow_status,
            'error_mapping_result': error_mapping_result,
            'repair_result': repair_result['result'],
            'validation_results': {
                'semantic_continuity': continuity_validation_result,
                'physics_compliance': physics_validation_result.get('result', {}),
                'content_integrity': content_validation_result
            },
            'final_video_path': repaired_video_path,
            'original_video_path': video_path,
            'error_type': error_type,
            'confidence_score': confidence_score,
            'repair_strategy': repair_strategy,
            'applied_fixes': repair_result['result'].get('applied_fixes', []),
            'metrics': {
                'continuity_score': continuity_validation_result.get('continuity_score', 0.0),
                'physics_compliance_score': physics_validation_result.get('result', {}).get('overall_compliance_score', 0.0),
                'content_integrity_score': content_validation_result.get('content_integrity_score', 0.0),
                'is_semantically_valid': continuity_validation_result.get('is_semantically_valid', False),
                'is_physically_consistent': physics_validation_result.get('result', {}).get('overall_validation_passed', False),
                'is_content_preserved': content_validation_result.get('is_content_preserved', False)
            }
        }
        
        # 生成见解
        insights = [
            f'增强版视频修复工作流完成: {video_path} -> {repaired_video_path}',
            f'检测到的错误类型: {error_type} (置信度: {confidence_score:.2f})',
            f'使用的修复策略: {repair_strategy}',
            f'应用的修复措施: {", ".join(repair_result["result"].get("applied_fixes", ["无"]))}',
            f'语义连续性: {"通过" if continuity_success else "未通过"} (得分: {continuity_validation_result.get("continuity_score", 0.0):.2f})',
            f'物理一致性: {"通过" if physics_success else "未通过"} (得分: {physics_validation_result.get("result", {}).get("overall_compliance_score", 0.0):.2f})',
            f'内容完整性: {"通过" if content_success else "未通过"} (得分: {content_validation_result.get("content_integrity_score", 0.0):.2f})',
            f'工作流状态: {workflow_status}'
        ]
        
        # 生成事实
        facts = [
            ['enhanced_video_repair_workflow', 'input_path', video_path],
            ['enhanced_video_repair_workflow', 'output_path', repaired_video_path],
            ['enhanced_video_repair_workflow', 'error_type', error_type],
            ['enhanced_video_repair_workflow', 'confidence_score', str(confidence_score)],
            ['enhanced_video_repair_workflow', 'repair_strategy', repair_strategy],
            ['enhanced_video_repair_workflow', 'status', workflow_status],
            ['enhanced_video_repair_workflow', 'continuity_score', str(continuity_validation_result.get('continuity_score', 0.0))],
            ['enhanced_video_repair_workflow', 'physics_compliance_score', str(physics_validation_result.get('result', {}).get('overall_compliance_score', 0.0))],
            ['enhanced_video_repair_workflow', 'content_integrity_score', str(content_validation_result.get('content_integrity_score', 0.0))],
            ['enhanced_video_repair_workflow', 'is_semantically_valid', str(continuity_validation_result.get('is_semantically_valid', False))],
            ['enhanced_video_repair_workflow', 'is_physically_consistent', str(physics_validation_result.get('result', {}).get('overall_validation_passed', False))],
            ['enhanced_video_repair_workflow', 'is_content_preserved', str(content_validation_result.get('is_content_preserved', False))]
        ]
        
        # 生成记忆
        memories = [
            f'增强版视频修复工作流完成: {video_path} -> {repaired_video_path}, 错误类型: {error_type}, 状态: {workflow_status}'
        ]
        
        return {
            'result': final_result,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except Exception as e:
        return {
            'result': {'error': f'增强版工作流执行异常: {str(e)}'},
            'insights': [f'增强版视频修复工作流执行异常: {str(e)}'],
            'facts': [['enhanced_video_repair_workflow', 'status', 'exception']],
            'memories': [f'增强版视频修复工作流异常: {video_path} - {str(e)}']
        }