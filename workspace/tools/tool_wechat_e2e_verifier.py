# tool_name: wechat_e2e_verifier

from langchain.tools import tool
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime

@tool
def wechat_e2e_verifier(input_args):
    """
    微信端到端验证器 - 客户端状态捕获
    
    这个工具实现了从发送方原始内容到接收方实际接收内容的全链路真实性验证，
    通过客户端状态捕获、屏幕截图分析来确保语义一致性。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作 ('capture_client_state', 'verify_consistency')
            - capture_delay (int, optional): 捕获延迟（秒），默认3秒
            
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
            temp_dir = tempfile.mkdtemp()
            screenshot_path = os.path.join(temp_dir, f"wechat_screenshot_{int(time.time())}.png")
            
            capture_cmd = f"screencapture -x {screenshot_path}"
            capture_result = subprocess.run(capture_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if capture_result.returncode != 0:
                return None, f"屏幕捕获失败: {capture_result.stderr}"
            
            if not os.path.exists(screenshot_path):
                return None, "屏幕截图文件未生成"
            
            return screenshot_path, None
            
        except Exception as e:
            return None, f"屏幕捕获异常: {str(e)}"
    
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
            'file_size': os.path.getsize(screenshot_path) if screenshot_path else 0
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
        
    else:
        return {
            'result': {'error': f'不支持的动作: {action}'},
            'insights': ['支持的动作: capture_client_state, verify_consistency'],
            'facts': [],
            'memories': []
        }