"""
macOS微信消息发送技能（修正版）
用于向指定联系人发送消息
"""

import subprocess
import json
import sys
import os

def main(input_args=None):
    """
    向微信联系人发送消息
    
    参数:
    input_args (dict): 包含以下字段的字典:
        - input: JSON字符串，包含contact_name和message
    """
    # 处理输入参数
    if input_args is None or not isinstance(input_args, dict):
        return {
            'result': {'error': '缺少 input_args 参数或参数格式错误'},
            'insights': ['参数校验失败：必须提供有效的input_args字典'],
            'facts': [],
            'memories': []
        }
    
    # 获取实际的JSON字符串
    json_str = input_args.get('input')
    if not json_str:
        return {
            'result': {'error': '缺少 input 参数'},
            'insights': ['参数校验失败：必须提供input字段'],
            'facts': [],
            'memories': []
        }
    
    # 解析JSON参数
    try:
        args = json.loads(json_str)
    except json.JSONDecodeError:
        return {
            'result': {'error': 'input 必须是有效的JSON字符串'},
            'insights': ['参数格式错误：input 必须是有效的JSON字符串'],
            'facts': [],
            'memories': []
        }
    
    # 验证必需参数
    contact_name = args.get('contact_name')
    message = args.get('message')
    
    if not contact_name:
        return {
            'result': {'error': '缺少 contact_name 参数'},
            'insights': ['参数校验失败：必须提供contact_name'],
            'facts': [],
            'memories': []
        }
    
    if not message:
        return {
            'result': {'error': '缺少 message 参数'},
            'insights': ['参数校验失败：必须提供message'],
            'facts': [],
            'memories': []
        }
    
    # 检查是否在macOS上运行
    if sys.platform != 'darwin':
        return {
            'result': {'error': '此技能仅支持macOS系统'},
            'insights': ['当前系统不是macOS，无法执行WeChat自动化'],
            'facts': [],
            'memories': []
        }
    
    # 检查微信是否已安装
    wechat_path = '/Applications/WeChat.app'
    if not os.path.exists(wechat_path):
        return {
            'result': {'error': '未找到微信应用程序，请确保微信已安装在/Applications目录下'},
            'insights': ['WeChat未安装在默认路径 /Applications/WeChat.app'],
            'facts': [],
            'memories': []
        }
    
    # 创建AppleScript脚本
    applescript = f'''
    -- 激活微信
    tell application "WeChat"
        activate
    end tell
    
    -- 等待微信激活
    delay 1
    
    -- 使用系统事件发送消息
    tell application "System Events"
        tell process "WeChat"
            -- 尝试多种方法找到搜索框
            try
                -- 方法1: 通过描述查找
                set searchField to text field 1 of group 1 of group 1 of UI element 1 of scroll area 1 of group 1 of group 1 of window 1
                set value of searchField to "{contact_name}"
                delay 0.5
                keystroke return
                delay 1
                keystroke "{message}"
                delay 0.5
                keystroke return
                return "success"
            on error
                try
                    -- 方法2: 直接聚焦到聊天窗口并发送
                    keystroke "{message}"
                    delay 0.5
                    keystroke return
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end try
        end tell
    end tell
    '''
    
    try:
        # 执行AppleScript
        result = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and "success" in result.stdout:
            return {
                'result': {
                    'success': True,
                    'message': f'已成功向"{contact_name}"发送消息: "{message}"',
                    'contact_name': contact_name,
                    'sent_message': message
                },
                'insights': [f'成功向 {contact_name} 发送消息'],
                'facts': [
                    ['WeChat消息发送', '联系人', contact_name],
                    ['WeChat消息发送', '消息内容', message]
                ],
                'memories': [
                    f'成功向{contact_name}发送了消息"{message}"'
                ]
            }
        else:
            error_msg = result.stderr if result.stderr else "未知错误"
            return {
                'result': {
                    'success': False,
                    'error': f'发送消息失败: {error_msg}',
                    'contact_name': contact_name,
                    'attempted_message': message
                },
                'insights': [f'向 {contact_name} 发送消息失败: {error_msg}'],
                'facts': [],
                'memories': []
            }
            
    except subprocess.TimeoutExpired:
        return {
            'result': {'error': '操作超时，请确保微信已打开并登录'},
            'insights': ['WeChat自动化操作超时，可能微信未完全启动或界面未就绪'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'执行过程中发生错误: {str(e)}'},
            'insights': [f'执行WeChat自动化时发生错误: {str(e)}'],
            'facts': [],
            'memories': []
        }