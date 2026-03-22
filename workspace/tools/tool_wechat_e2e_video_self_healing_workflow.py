# tool_name: wechat_e2e_video_self_healing_workflow

import json
import os
from typing import Dict, Any
from langchain.tools import tool

@tool
def wechat_e2e_video_self_healing_workflow(input_args: str) -> Dict[str, Any]:
    """
    微信端到端视频自愈工作流
    
    用途: 实现完整的微信视频传输自愈闭环，包括发送、验证、诊断、修复和再验证
    参数: input_args - JSON字符串，包含以下必需和可选参数:
        - video_path (str, required): 要发送的视频文件路径
        - recipient (str, required): 接收者名称
        - message_content (str, optional): 附加消息内容
        - repair_strategy (str, optional): 修复策略 ('conservative', 'aggressive', 'balanced')，默认'balanced'
        - max_repair_attempts (int, optional): 最大修复尝试次数，默认3
        
    返回值: 包含完整自愈工作流执行结果的字典，包括:
        - workflow_status: 工作流整体状态 ('success', 'partial_success', 'failed')
        - original_video_path: 原始视频路径
        - final_video_path: 最终修复后的视频路径
        - repair_attempts: 修复尝试次数
        - validation_results: 验证结果（语义连续性、物理一致性、内容完整性）
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
        video_path = params.get('video_path')
        recipient = params.get('recipient')
        
        if not video_path:
            return {
                'result': {'error': '缺少 video_path 参数'},
                'insights': ['参数校验失败：必须提供video_path'],
                'facts': [],
                'memories': []
            }
            
        if not recipient:
            return {
                'result': {'error': '缺少 recipient 参数'},
                'insights': ['参数校验失败：必须提供recipient'],
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
        
        message_content = params.get('message_content', '')
        repair_strategy = params.get('repair_strategy', 'balanced')
        max_repair_attempts = params.get('max_repair_attempts', 3)
        
        # 创建工作目录
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        workflow_output_dir = f"./wechat_e2e_self_healing_{base_name}"
        os.makedirs(workflow_output_dir, exist_ok=True)
        
        current_video_path = video_path
        repair_attempts = 0
        
        # 步骤1: 检查微信授权状态
        from workspace.tools.tool_wechat_validation_cycle import wechat_validation_cycle
        
        auth_params = {'action': 'check_auth'}
        auth_result = wechat_validation_cycle(json.dumps(auth_params))
        
        if not auth_result.get('result', {}).get('is_authorized', False):
            return {
                'result': {'error': '微信未授权，无法继续自愈工作流'},
                'insights': ['微信授权检查失败，无法发送消息'],
                'facts': [],
                'memories': []
            }
        
        # 步骤2: 发送初始视频
        send_params = {
            'action': 'send_message',
            'recipient': recipient,
            'message_content': f"[视频] {message_content}" if message_content else "[视频]"
        }
        
        send_result = wechat_validation_cycle(json.dumps(send_params))
        
        # 步骤3: 执行端到端验证
        from workspace.tools.tool_wechat_e2e_video_physics_consistency_verifier import wechat_e2e_video_physics_consistency_verifier
        
        verify_params = {
            'action': 'full_e2e_validation',
            'original_video_path': current_video_path,
            'recipient': recipient,
            'capture_delay': 5
        }
        
        verification_result = wechat_e2e_video_physics_consistency_verifier(json.dumps(verify_params))
        
        # 步骤4: 检查验证结果并决定是否需要修复
        is_valid = False
        validation_details = {}
        
        if 'result' in verification_result:
            result_data = verification_result['result']
            if isinstance(result_data, dict):
                # 检查物理一致性和语义一致性
                physics_valid = result_data.get('physics_consistency_passed', False)
                semantic_valid = result_data.get('semantic_consistency_passed', False)
                is_valid = physics_valid and semantic_valid
                
                validation_details = {
                    'physics_consistency': result_data.get('physics_consistency_details', {}),
                    'semantic_consistency': result_data.get('semantic_consistency_details', {}),
                    'overall_valid': is_valid
                }
        
        # 如果验证通过，直接返回成功
        if is_valid:
            final_result = {
                'workflow_status': 'success',
                'original_video_path': video_path,
                'final_video_path': current_video_path,
                'repair_attempts': 0,
                'validation_results': validation_details,
                'message': '视频传输和验证成功完成，无需修复'
            }
        else:
            # 需要修复
            if max_repair_attempts <= 0:
                final_result = {
                    'workflow_status': 'failed',
                    'original_video_path': video_path,
                    'final_video_path': current_video_path,
                    'repair_attempts': 0,
                    'validation_results': validation_details,
                    'message': '验证失败且修复被禁用'
                }
            else:
                # 执行修复流程
                error_info = "视频端到端验证失败"
                if not validation_details.get('physics_consistency', {}).get('passed', True):
                    error_info += ", 物理一致性问题"
                if not validation_details.get('semantic_consistency', {}).get('passed', True):
                    error_info += ", 语义一致性问题"
                
                from workspace.tools.tool_video_repair_validation_workflow import enhanced_video_repair_validation_workflow
                
                repair_params = {
                    'error_info': error_info,
                    'video_path': current_video_path,
                    'repair_strategy': repair_strategy,
                    'output_dir': os.path.join(workflow_output_dir, 'repair')
                }
                
                repair_result = enhanced_video_repair_validation_workflow(json.dumps(repair_params))
                
                # 检查修复结果
                if repair_result.get('result', {}).get('workflow_status') == 'success':
                    repaired_video_path = repair_result['result']['final_video_path']
                    
                    # 验证修复后的视频
                    final_verify_params = {
                        'action': 'full_e2e_validation',
                        'original_video_path': repaired_video_path,
                        'recipient': recipient,
                        'capture_delay': 5
                    }
                    
                    final_verification_result = wechat_e2e_video_physics_consistency_verifier(json.dumps(final_verify_params))
                    
                    # 检查最终验证结果
                    final_is_valid = False
                    final_validation_details = {}
                    
                    if 'result' in final_verification_result:
                        final_result_data = final_verification_result['result']
                        if isinstance(final_result_data, dict):
                            final_physics_valid = final_result_data.get('physics_consistency_passed', False)
                            final_semantic_valid = final_result_data.get('semantic_consistency_passed', False)
                            final_is_valid = final_physics_valid and final_semantic_valid
                            
                            final_validation_details = {
                                'physics_consistency': final_result_data.get('physics_consistency_details', {}),
                                'semantic_consistency': final_result_data.get('semantic_consistency_details', {}),
                                'overall_valid': final_is_valid
                            }
                    
                    if final_is_valid:
                        final_result = {
                            'workflow_status': 'success',
                            'original_video_path': video_path,
                            'final_video_path': repaired_video_path,
                            'repair_attempts': 1,
                            'validation_results': final_validation_details,
                            'message': '视频修复成功并通过验证'
                        }
                    else:
                        final_result = {
                            'workflow_status': 'partial_success',
                            'original_video_path': video_path,
                            'final_video_path': repaired_video_path,
                            'repair_attempts': 1,
                            'validation_results': final_validation_details,
                            'message': '视频已修复但验证仍不完全通过'
                        }
                else:
                    final_result = {
                        'workflow_status': 'failed',
                        'original_video_path': video_path,
                        'final_video_path': current_video_path,
                        'repair_attempts': 1,
                        'validation_results': validation_details,
                        'message': '视频修复失败'
                    }
        
        # 生成见解
        insights = [
            f'微信端到端视频自愈工作流完成: {video_path} -> {final_result["final_video_path"]}',
            f'修复尝试次数: {final_result["repair_attempts"]}',
            f'工作流状态: {final_result["workflow_status"]}',
            f'最终消息: {final_result["message"]}'
        ]
        
        # 生成事实
        facts = [
            ['wechat_e2e_video_self_healing', 'input_path', video_path],
            ['wechat_e2e_video_self_healing', 'output_path', final_result['final_video_path']],
            ['wechat_e2e_video_self_healing', 'recipient', recipient],
            ['wechat_e2e_video_self_healing', 'repair_attempts', str(final_result['repair_attempts'])],
            ['wechat_e2e_video_self_healing', 'status', final_result['workflow_status']]
        ]
        
        # 生成记忆
        memories = [
            f'微信端到端视频自愈工作流完成: {video_path} -> {final_result["final_video_path"]}, 状态: {final_result["workflow_status"]}, 尝试次数: {final_result["repair_attempts"]}'
        ]
        
        return {
            'result': final_result,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except Exception as e:
        return {
            'result': {'error': f'微信端到端视频自愈工作流异常: {str(e)}'},
            'insights': [f'工作流执行过程中发生异常: {str(e)}'],
            'facts': [],
            'memories': [f'微信端到端视频自愈工作流异常: {str(e)}']
        }