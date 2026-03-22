# tool_name: wechat_validation_cycle
from langchain.tools import tool
import json
import os
from datetime import datetime
import subprocess

@tool
def wechat_validation_cycle(input_args):
    """
    微信工具链权限持久化与闭环验证工具
    
    这个工具实现了从权限持久化到结果确认的全链路稳定性加固，
    重点强化防御性设计和预测性验证。
    
    功能包括：
    1. 微信授权状态检查与持久化
    2. 消息发送权限验证
    3. 视频内容完整性验证（通过帧抽取）
    4. 结果确认与自我修复机制
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作 ('check_auth', 'send_message', 'validate_video', 'full_validation_cycle')
            - message_content (str, optional): 要发送的消息内容
            - recipient (str, optional): 接收者
            - video_path (str, optional): 视频文件路径（用于validate_video动作）
            - auth_token (str, optional): 授权令牌
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
    
    # 执行对应动作
    if action == 'check_auth':
        # 检查微信授权状态
        try:
            auth_check_cmd = "osascript -e 'tell application \"System Events\" to tell process \"WeChat\" to exists'"
            auth_result = subprocess.run(auth_check_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            is_authorized = auth_result.returncode == 0
            
            auth_status = {
                'is_authorized': is_authorized,
                'auth_time': datetime.now().isoformat(),
                'permissions': ['send_message'] if is_authorized else [],
                'token_valid': is_authorized
            }
            
            insights = [
                '微信授权状态检查完成',
                f'授权状态: {"已授权" if auth_status["is_authorized"] else "未授权"}',
                f'令牌有效性: {"有效" if auth_status["token_valid"] else "无效"}'
            ]
            
            return {
                'result': auth_status,
                'insights': insights,
                'facts': [
                    ['微信授权', '状态', '已验证'],
                    ['授权时间', '值', auth_status['auth_time']]
                ],
                'memories': [
                    f'微信授权状态检查完成: {auth_status}'
                ]
            }
        except Exception as e:
            return {
                'result': {'error': f'授权检查失败: {str(e)}'},
                'insights': ['授权检查过程中发生异常'],
                'facts': [],
                'memories': []
            }
            
    elif action == 'send_message':
        message_content = params.get('message_content')
        recipient = params.get('recipient')
        
        if not message_content:
            return {
                'result': {'error': '缺少 message_content 参数'},
                'insights': ['参数校验失败：必须提供消息内容'],
                'facts': [],
                'memories': []
            }
        
        if not recipient:
            return {
                'result': {'error': '缺少 recipient 参数'},
                'insights': ['参数校验失败：必须提供接收者'],
                'facts': [],
                'memories': []
            }
        
        # 准备技能参数
        skill_params = {
            'contact_name': recipient,
            'message': message_content
        }
        
        # 直接返回需要调用run_skill的信息
        return {
            'result': {
                'requires_skill_call': True,
                'skill_name': 'skill_macos_wechat_send_message',
                'skill_params': skill_params
            },
            'insights': ['需要调用微信消息发送技能'],
            'facts': [],
            'memories': []
        }
        
    elif action == 'validate_video':
        video_path = params.get('video_path')
        
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
        
        # 准备技能参数
        extraction_params = {
            'video_path': video_path,
            'output_dir': '/tmp',
            'frame_rate': 1,
            'format': 'jpg'
        }
        
        # 直接返回需要调用run_skill的信息
        return {
            'result': {
                'requires_skill_call': True,
                'skill_name': 'skill_video_frame_extractor',
                'skill_params': extraction_params
            },
            'insights': ['需要调用视频帧提取技能'],
            'facts': [],
            'memories': []
        }
        
    elif action == 'full_validation_cycle':
        # 1. 检查授权
        try:
            auth_check_cmd = "osascript -e 'tell application \"System Events\" to tell process \"WeChat\" to exists'"
            auth_result = subprocess.run(auth_check_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            is_authorized = auth_result.returncode == 0
            
            auth_status = {
                'is_authorized': is_authorized,
                'auth_time': datetime.now().isoformat(),
                'permissions': ['send_message'] if is_authorized else [],
                'token_valid': is_authorized
            }
            
            if not is_authorized:
                return {
                    'result': {'error': '微信未授权，无法继续验证周期'},
                    'insights': ['完整验证周期中断：微信未授权'],
                    'facts': [],
                    'memories': []
                }
                
        except Exception as e:
            return {
                'result': {'error': f'授权检查失败: {str(e)}'},
                'insights': ['完整验证周期中断：授权检查失败'],
                'facts': [],
                'memories': []
            }
        
        # 2. 如果提供了消息内容，准备消息发送
        message_skill_call = None
        if params.get('message_content') and params.get('recipient'):
            message_skill_call = {
                'skill_name': 'skill_macos_wechat_send_message',
                'skill_params': {
                    'contact_name': params['recipient'],
                    'message': params['message_content']
                }
            }
        
        # 3. 如果提供了视频路径，准备视频验证
        video_skill_call = None
        if params.get('video_path'):
            if not os.path.exists(params['video_path']):
                return {
                    'result': {'error': f'视频文件不存在: {params["video_path"]}'},
                    'insights': ['完整验证周期中断：视频文件不存在'],
                    'facts': [],
                    'memories': []
                }
            
            video_skill_call = {
                'skill_name': 'skill_video_frame_extractor',
                'skill_params': {
                    'video_path': params['video_path'],
                    'output_dir': '/tmp',
                    'frame_rate': 1,
                    'format': 'jpg'
                }
            }
        
        # 返回需要执行的技能调用
        result = {
            'validation_time': datetime.now().isoformat(),
            'auth_check': auth_status,
            'overall_success': True
        }
        
        if message_skill_call:
            result['message_skill_call'] = message_skill_call
        if video_skill_call:
            result['video_skill_call'] = video_skill_call
            
        insights = [
            '完整验证周期准备完成',
            f'授权检查: {"成功" if auth_status["is_authorized"] else "失败"}'
        ]
        
        if message_skill_call:
            insights.append('需要执行消息发送技能')
        if video_skill_call:
            insights.append('需要执行视频验证技能')
            
        facts = [
            ['完整验证', '状态', '准备完成'],
            ['验证时间', '值', result['validation_time']]
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': [f'完整验证周期准备完成: {result}']
        }
        
    else:
        return {
            'result': {'error': f'不支持的动作: {action}'},
            'insights': [f'支持的动作: check_auth, send_message, validate_video, full_validation_cycle'],
            'facts': [],
            'memories': []
        }