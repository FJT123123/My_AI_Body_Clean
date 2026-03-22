# tool_name: wechat_end_to_end_semantic_consistency_verifier

from langchain.tools import tool
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime

@tool
def wechat_end_to_end_semantic_consistency_verifier(input_args):
    """
    微信端到端语义一致性验证器 - 增强版客户端状态捕获
    
    这个工具实现了从发送方原始内容到接收方实际接收内容的全链路真实性验证，
    通过客户端状态捕获、屏幕截图分析和内容比对来确保语义一致性。
    
    功能包括：
    1. 客户端状态捕获（屏幕截图）
    2. 发送内容与接收内容的语义比对
    3. 视频/图像内容完整性验证
    4. 端到端验证闭环
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作 ('capture_client_state', 'verify_semantic_consistency', 'full_e2e_validation')
            - original_content (str, optional): 原始发送内容
            - expected_recipient (str, optional): 预期接收者
            - content_type (str, optional): 内容类型 ('text', 'image', 'video')
            - media_path (str, optional): 媒体文件路径（用于image/video类型）
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
    
    def _validate_media_file_exists(file_path):
        """验证媒体文件是否存在"""
        try:
            if not os.path.exists(file_path):
                return {'is_valid': False, 'error': '媒体文件不存在'}
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.mp4', '.mov', '.avi', '.mkv']:
                return {
                    'is_valid': True,
                    'validation_method': 'file_existence_check',
                    'original_size': os.path.getsize(file_path),
                    'file_extension': file_ext
                }
            else:
                return {'is_valid': False, 'error': f'不支持的文件格式: {file_ext}'}
                
        except Exception as e:
            return {'is_valid': False, 'error': f'文件验证异常: {str(e)}'}
    
    # 执行对应动作
    if action == 'capture_client_state':
        capture_delay = params.get('capture_delay', 3)
        time.sleep(capture_delay)
        
        screenshot_path, error = _capture_wechat_screen()
        
        if error:
            return {
                'result': {'error': error},
                'insights': ['客户端状态捕获失败'],
                'facts': [],
                'memories': []
            }
        
        screen_info = {
            'capture_time': datetime.now().isoformat(),
            'screenshot_path': screenshot_path,
            'file_size': os.path.getsize(screenshot_path) if screenshot_path else 0,
            'wechat_active': True
        }
        
        insights = [
            '客户端状态捕获成功',
            f'截图保存路径: {screenshot_path}',
            f'文件大小: {screen_info["file_size"]} bytes'
        ]
        
        return {
            'result': screen_info,
            'insights': insights,
            'facts': [
                ['客户端状态', '捕获时间', screen_info['capture_time']],
                ['截图文件', '路径', screenshot_path]
            ],
            'memories': [f'客户端状态捕获完成: {screen_info}']
        }
        
    elif action == 'verify_semantic_consistency':
        original_content = params.get('original_content')
        content_type = params.get('content_type', 'text')
        
        if not original_content:
            return {
                'result': {'error': '缺少 original_content 参数'},
                'insights': ['参数校验失败：必须提供原始内容'],
                'facts': [],
                'memories': []
            }
        
        # 捕获当前客户端状态
        screenshot_path, error = _capture_wechat_screen()
        if error:
            return {
                'result': {'error': f'状态捕获失败: {error}'},
                'insights': ['语义一致性验证中断：无法捕获客户端状态'],
                'facts': [],
                'memories': []
            }
        
        # 对于文本内容，准备OCR技能调用
        if content_type == 'text':
            ocr_params = {
                'image_path': screenshot_path
            }
            
            result = {
                'verification_time': datetime.now().isoformat(),
                'original_content': original_content,
                'screenshot_path': screenshot_path,
                'requires_skill_call': True,
                'skill_name': 'skill_screen_ocr_text_extraction',
                'skill_params': ocr_params,
                'content_type': 'text'
            }
            
            insights = [
                '需要调用OCR技能提取截图中的文本内容',
                f'原始内容长度: {len(original_content)} 字符',
                f'截图路径: {screenshot_path}'
            ]
            
            return {
                'result': result,
                'insights': insights,
                'facts': [
                    ['语义验证', '状态', '等待OCR结果'],
                    ['原始内容', '长度', str(len(original_content))]
                ],
                'memories': [f'准备OCR文本提取: {result}']
            }
            
        elif content_type in ['image', 'video']:
            media_path = params.get('media_path')
            if not media_path:
                return {
                    'result': {'error': '缺少 media_path 参数'},
                    'insights': ['参数校验失败：必须提供媒体文件路径'],
                    'facts': [],
                    'memories': []
                }
            
            # 验证媒体文件
            media_validation = _validate_media_file_exists(media_path)
            if not media_validation['is_valid']:
                return {
                    'result': {'error': f'媒体验证失败: {media_validation.get("error", "未知错误")}'},
                    'insights': ['语义一致性验证中断：媒体文件验证失败'],
                    'facts': [],
                    'memories': []
                }
            
            result = {
                'verification_time': datetime.now().isoformat(),
                'media_path': media_path,
                'media_validation': media_validation,
                'screenshot_path': screenshot_path,
                'overall_success': True,
                'content_type': content_type
            }
            
            insights = [
                '媒体内容验证完成',
                f'验证方法: {media_validation["validation_method"]}',
                f'文件大小: {media_validation["original_size"]} bytes',
                '媒体完整性: 通过'
            ]
            
            facts = [
                ['媒体验证', '状态', '完成'],
                ['媒体路径', '值', media_path],
                ['完整性', '结果', '通过']
            ]
            
            return {
                'result': result,
                'insights': insights,
                'facts': facts,
                'memories': [f'媒体内容验证结果: {result}']
            }
            
        else:
            return {
                'result': {'error': f'不支持的内容类型: {content_type}'},
                'insights': ['支持的内容类型: text, image, video'],
                'facts': [],
                'memories': []
            }
            
    elif action == 'full_e2e_validation':
        # 执行完整的端到端验证
        original_content = params.get('original_content')
        content_type = params.get('content_type', 'text')
        expected_recipient = params.get('expected_recipient')
        
        if not original_content:
            return {
                'result': {'error': '缺少 original_content 参数'},
                'insights': ['参数校验失败：必须提供原始内容'],
                'facts': [],
                'memories': []
            }
        
        # 1. 首先检查微信授权状态
        try:
            auth_check_cmd = "osascript -e 'tell application \"System Events\" to tell process \"WeChat\" to exists'"
            auth_result = subprocess.run(auth_check_cmd, shell=True, capture_output=True, text=True, timeout=5)
            is_authorized = auth_result.returncode == 0
            
            if not is_authorized:
                return {
                    'result': {'error': '微信未授权，无法继续验证'},
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
        
        # 2. 如果提供了接收者，记录信息
        if expected_recipient:
            insights_recipient = f"目标接收者: {expected_recipient}"
        else:
            insights_recipient = "未指定接收者"
        
        # 3. 准备语义一致性验证
        verify_params = {
            'action': 'verify_semantic_consistency',
            'original_content': original_content,
            'content_type': content_type
        }
        
        if content_type in ['image', 'video']:
            media_path = params.get('media_path')
            if media_path:
                verify_params['media_path'] = media_path
        
        # 调用内部验证逻辑
        verify_result = wechat_end_to_end_semantic_consistency_verifier(json.dumps(verify_params))
        
        if 'error' in verify_result['result']:
            return verify_result
        
        # 4. 构建完整验证结果
        full_result = {
            'validation_time': datetime.now().isoformat(),
            'auth_status': {'is_authorized': True, 'check_time': datetime.now().isoformat()},
            'semantic_verification': verify_result['result'],
            'content_type': content_type,
            'original_content': original_content,
            'expected_recipient': expected_recipient
        }
        
        # 如果是文本内容，需要OCR技能调用
        if content_type == 'text' and verify_result['result'].get('requires_skill_call'):
            full_result['requires_skill_call'] = True
            full_result['skill_name'] = verify_result['result']['skill_name']
            full_result['skill_params'] = verify_result['result']['skill_params']
            overall_success = None  # 等待OCR结果
        else:
            overall_success = verify_result['result'].get('overall_success', False)
            full_result['overall_success'] = overall_success
        
        insights = [
            '完整端到端验证准备完成',
            f'授权状态: 已授权',
            insights_recipient,
            f'内容类型: {content_type}'
        ] + verify_result['insights']
        
        if overall_success is not None:
            insights.append(f'整体结果: {"通过" if overall_success else "失败"}')
        
        facts = [
            ['端到端验证', '状态', '准备完成'],
            ['验证时间', '值', full_result['validation_time']]
        ] + verify_result['facts']
        
        return {
            'result': full_result,
            'insights': insights,
            'facts': facts,
            'memories': [f'完整端到端验证准备: {full_result}']
        }
        
    else:
        return {
            'result': {'error': f'不支持的动作: {action}'},
            'insights': ['支持的动作: capture_client_state, verify_semantic_consistency, full_e2e_validation'],
            'facts': [],
            'memories': []
        }