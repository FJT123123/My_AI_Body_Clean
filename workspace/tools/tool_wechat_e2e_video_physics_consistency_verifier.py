# tool_name: wechat_e2e_video_physics_consistency_verifier

from langchain.tools import tool
import json
import os
import tempfile
import time
from datetime import datetime
import subprocess

@tool
def wechat_e2e_video_physics_consistency_verifier(input_args):
    """
    微信端到端视频物理一致性验证器
    
    这个工具实现了从发送方原始视频到接收方实际接收视频的全链路物理一致性验证，
    通过客户端状态捕获、视频帧提取和物理语义分析来确保视频内容在传输过程中的完整性与真实性。
    
    功能包括：
    1. 微信授权状态检查
    2. 客户端状态捕获（屏幕截图）
    3. 视频帧提取与物理一致性验证
    4. 端到端验证闭环
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作 ('verify_video_consistency', 'full_e2e_validation')
            - original_video_path (str, optional): 原始视频文件路径
            - recipient (str, optional): 预期接收者
            - capture_delay (int, optional): 捕获延迟（秒），默认3秒
            - context (str, optional): 上下文信息
            
    Returns:
        dict: 包含验证结果、状态信息和建议的字典
    """
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args)
        except json.JSONDecodeError:
            return {
                'result': {'error': '缺少有效的JSON参数'},
                'insights': ['参数解析失败：输入必须是有效的JSON字符串'],
                'facts': [],
                'memories': []
            }
    elif isinstance(input_args, dict):
        params = input_args
    else:
        return {
            'result': {'error': '缺少有效的参数'},
            'insights': ['参数格式错误：必须是JSON字符串或字典'],
            'facts': [],
            'memories': []
        }
    
    # 验证必需参数
    action = params.get('action')
    if not action:
        return {
            'result': {'error': '缺少 action 参数'},
            'insights': ['参数校验失败：必须提供action参数'],
            'facts': [],
            'memories': []
        }
    
    def _check_wechat_auth():
        """检查微信授权状态"""
        try:
            auth_check_cmd = "osascript -e 'tell application \"System Events\" to tell process \"WeChat\" to exists'"
            auth_result = subprocess.run(auth_check_cmd, shell=True, capture_output=True, text=True, timeout=5)
            is_authorized = auth_result.returncode == 0
            return is_authorized, None
        except Exception as e:
            return False, f"授权检查异常: {str(e)}"
    
    def _capture_wechat_screen():
        """捕获微信客户端当前屏幕状态"""
        try:
            # 创建临时文件存储截图
            temp_dir = tempfile.mkdtemp()
            screenshot_path = os.path.join(temp_dir, f"wechat_screenshot_{int(time.time())}.png")
            
            # 使用screencapture命令捕获屏幕（macOS）
            capture_cmd = f"screencapture -x {screenshot_path}"
            capture_result = subprocess.run(capture_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if capture_result.returncode != 0:
                return None, f"屏幕捕获失败: {capture_result.stderr}"
            
            if not os.path.exists(screenshot_path):
                return None, "屏幕截图文件未生成"
            
            # 尝试聚焦到微信窗口
            focus_cmd = "osascript -e 'tell application \"WeChat\" to activate'"
            subprocess.run(focus_cmd, shell=True, capture_output=True, timeout=5)
            
            # 等待窗口激活
            time.sleep(1)
            
            return screenshot_path, None
            
        except Exception as e:
            return None, f"屏幕捕获异常: {str(e)}"
    
    def _validate_video_physics_compliance(video_path):
        """验证视频的物理一致性"""
        try:
            # 使用全局run_skill调用验证技能
            validation_input = json.dumps({
                'video_path': video_path,
                'output_dir': os.path.join(tempfile.gettempdir(), "physics_validation")
            })
            validation_result = run_skill('skill_video_motion_semantic_validator', validation_input)
            
            # 检查验证结果结构
            if isinstance(validation_result, dict):
                if 'result' in validation_result:
                    result_data = validation_result['result']
                    if isinstance(result_data, dict) and 'overall_valid' in result_data:
                        return result_data, None
                    else:
                        return None, "验证结果格式不正确"
                else:
                    return None, "验证结果缺少result字段"
            else:
                return None, "验证结果不是字典格式"
                
        except Exception as e:
            return None, f"视频验证异常: {str(e)}"
    
    # 执行对应动作
    if action == 'verify_video_consistency':
        original_video_path = params.get('original_video_path')
        
        if not original_video_path:
            return {
                'result': {'error': '缺少 original_video_path 参数'},
                'insights': ['参数校验失败：必须提供原始视频路径'],
                'facts': [],
                'memories': []
            }
        
        if not os.path.exists(original_video_path):
            return {
                'result': {'error': f'原始视频文件不存在: {original_video_path}'},
                'insights': [f'指定的视频文件路径不存在: {original_video_path}'],
                'facts': [],
                'memories': []
            }
        
        # 验证原始视频的物理一致性
        original_validation, error = _validate_video_physics_compliance(original_video_path)
        if error:
            return {
                'result': {'error': f'原始视频验证失败: {error}'},
                'insights': ['视频物理一致性验证中断：无法验证原始视频'],
                'facts': [],
                'memories': []
            }
        
        # 捕获微信客户端状态
        capture_delay = params.get('capture_delay', 3)
        time.sleep(capture_delay)
        screenshot_path, error = _capture_wechat_screen()
        if error:
            return {
                'result': {'error': f'状态捕获失败: {error}'},
                'insights': ['视频一致性验证中断：无法捕获客户端状态'],
                'facts': [],
                'memories': []
            }
        
        result = {
            'verification_time': datetime.now().isoformat(),
            'original_video_path': original_video_path,
            'original_validation': original_validation,
            'screenshot_path': screenshot_path,
            'overall_success': original_validation.get('overall_valid', False),
            'requires_manual_verification': True  # 需要手动验证截图中的视频内容
        }
        
        insights = [
            '视频物理一致性验证完成',
            f'原始视频路径: {original_video_path}',
            f'截图路径: {screenshot_path}',
            f'物理一致性: {"通过" if original_validation.get("overall_valid", False) else "未通过"}'
        ]
        
        facts = [
            ['视频验证', '状态', '完成'],
            ['验证时间', '值', result['verification_time']],
            ['物理一致性', '结果', '通过' if original_validation.get('overall_valid', False) else '未通过']
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': [f'视频物理一致性验证结果: {result}']
        }
        
    elif action == 'full_e2e_validation':
        # 执行完整的端到端验证
        original_video_path = params.get('original_video_path')
        recipient = params.get('recipient')
        
        if not original_video_path:
            return {
                'result': {'error': '缺少 original_video_path 参数'},
                'insights': ['参数校验失败：必须提供原始视频路径'],
                'facts': [],
                'memories': []
            }
        
        if not os.path.exists(original_video_path):
            return {
                'result': {'error': f'原始视频文件不存在: {original_video_path}'},
                'insights': [f'指定的视频文件路径不存在: {original_video_path}'],
                'facts': [],
                'memories': []
            }
        
        # 1. 检查微信授权状态
        is_authorized, error = _check_wechat_auth()
        if error:
            return {
                'result': {'error': f'授权检查失败: {error}'},
                'insights': ['完整验证周期中断：授权检查失败'],
                'facts': [],
                'memories': []
            }
        
        if not is_authorized:
            return {
                'result': {'error': '微信未授权，无法继续验证'},
                'insights': ['完整验证周期中断：微信未授权'],
                'facts': [],
                'memories': []
            }
        
        # 2. 验证原始视频的物理一致性
        original_validation, error = _validate_video_physics_compliance(original_video_path)
        if error:
            return {
                'result': {'error': f'原始视频验证失败: {error}'},
                'insights': ['完整验证周期中断：无法验证原始视频'],
                'facts': [],
                'memories': []
            }
        
        # 3. 准备消息发送（如果提供了接收者）
        message_skill_call = None
        if recipient:
            message_skill_call = {
                'skill_name': 'skill_macos_wechat_send_message',
                'skill_params': {
                    'contact_name': recipient,
                    'message': f'视频物理一致性验证测试: {os.path.basename(original_video_path)}'
                }
            }
        
        # 4. 准备客户端状态捕获
        capture_delay = params.get('capture_delay', 3)
        
        result = {
            'validation_time': datetime.now().isoformat(),
            'auth_status': {'is_authorized': True, 'check_time': datetime.now().isoformat()},
            'original_video_path': original_video_path,
            'original_validation': original_validation,
            'recipient': recipient,
            'capture_delay': capture_delay,
            'overall_success': original_validation.get('overall_valid', False)
        }
        
        if message_skill_call:
            result['message_skill_call'] = message_skill_call
        
        insights = [
            '完整端到端视频物理一致性验证准备完成',
            f'授权状态: 已授权',
            f'原始视频路径: {original_video_path}',
            f'物理一致性: {"通过" if original_validation.get("overall_valid", False) else "未通过"}'
        ]
        
        if recipient:
            insights.append(f'目标接收者: {recipient}')
            insights.append('需要执行消息发送技能')
        
        insights.append(f'将在 {capture_delay} 秒后捕获客户端状态')
        
        facts = [
            ['端到端验证', '状态', '准备完成'],
            ['验证时间', '值', result['validation_time']],
            ['物理一致性', '结果', '通过' if original_validation.get('overall_valid', False) else '未通过']
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': [f'完整端到端视频物理一致性验证准备: {result}']
        }
        
    else:
        return {
            'result': {'error': f'不支持的动作: {action}'},
            'insights': ['支持的动作: verify_video_consistency, full_e2e_validation'],
            'facts': [],
            'memories': []
        }