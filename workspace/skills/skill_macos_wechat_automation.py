"""
自动生成的技能模块
需求: 创建一个AppleScript脚本，用于在macOS上自动打开微信并向指定联系人发送消息。脚本将接受联系人名称和消息内容作为参数，并处理可能的错误情况。
生成时间: 2026-03-21 11:28:41
"""

# skill_name: macos_wechat_automation

import subprocess
import os
import sys
import json
import time

def main(args=None):
    """
    在macOS上自动打开微信并向指定联系人发送消息的AppleScript脚本
    该技能会创建一个AppleScript脚本，用于在macOS系统上自动打开微信应用程序，
    并向指定的联系人发送消息。脚本会处理可能的错误情况，包括微信未运行、
    联系人不存在或消息发送失败等。
    """
    if args is None:
        args = {}
    
    # 提取参数
    contact_name = args.get('contact_name', '')
    message_content = args.get('message_content', '')
    script_path = args.get('script_path', './send_wechat_message.scpt')
    
    # 检查是否在macOS上运行
    if sys.platform != 'darwin':
        return {
            'result': {'error': '此技能仅支持macOS系统'},
            'insights': ['当前系统不是macOS，无法执行WeChat自动化'],
            'capabilities': []
        }
    
    # 检查是否安装了微信
    wechat_path = '/Applications/WeChat.app'
    if not os.path.exists(wechat_path):
        return {
            'result': {'error': '未找到微信应用程序'},
            'insights': ['WeChat未安装在默认路径 /Applications/WeChat.app'],
            'capabilities': []
        }
    
    # 生成AppleScript脚本内容
    applescript_content = f'''
    -- 打开微信应用
    tell application "WeChat"
        activate
    end tell
    
    -- 等待微信启动
    delay 3
    
    -- 搜索联系人并发送消息
    tell application "System Events"
        tell process "WeChat"
            -- 点击搜索框
            click text field 1 of group 1 of group 1 of UI element 1 of scroll area 1 of group 1 of group 1 of window 1
            -- 输入联系人名称
            keystroke "{contact_name}"
            delay 1
            -- 按回车键选择联系人
            keystroke return
            delay 1
            -- 输入消息内容
            set value of text area 1 of group 1 of group 1 of UI element 1 of scroll area 1 of group 2 of group 1 of window 1 to "{message_content}"
            -- 按回车键发送消息
            keystroke return
        end tell
    end tell
    '''
    
    try:
        # 创建AppleScript脚本文件
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(applescript_content)
        
        # 执行AppleScript脚本
        result = subprocess.run(['osascript', script_path], 
                               capture_output=True, text=True, timeout=30)
        
        # 检查执行结果
        if result.returncode == 0:
            execution_result = {
                'success': True,
                'message': f'成功向联系人 "{contact_name}" 发送消息',
                'contact_name': contact_name,
                'message_content': message_content,
                'script_path': script_path
            }
            insights = [f'成功向 {contact_name} 发送消息: {message_content}']
        else:
            execution_result = {
                'success': False,
                'error': result.stderr,
                'contact_name': contact_name,
                'message_content': message_content
            }
            insights = [f'向 {contact_name} 发送消息失败: {result.stderr}']
        
        # 清理临时脚本文件
        if os.path.exists(script_path):
            os.remove(script_path)
        
        return {
            'result': execution_result,
            'insights': insights,
            'facts': [
                ['WeChat自动化脚本', '发送消息给', contact_name],
                ['WeChat自动化脚本', '消息内容', message_content]
            ],
            'capabilities': ['macOS WeChat自动化消息发送']
        }
        
    except subprocess.TimeoutExpired:
        return {
            'result': {'error': '脚本执行超时'},
            'insights': ['WeChat自动化脚本执行超时，可能微信未完全启动或界面未就绪'],
            'facts': [
                ['WeChat自动化脚本', '执行状态', '超时']
            ],
            'capabilities': []
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'执行WeChat自动化脚本时发生错误: {str(e)}'],
            'facts': [
                ['WeChat自动化脚本', '执行状态', '错误'],
                ['WeChat自动化脚本', '错误信息', str(e)]
            ],
            'capabilities': []
        }