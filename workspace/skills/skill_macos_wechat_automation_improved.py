"""
自动生成的技能模块
需求: 创建一个改进版的macOS微信自动化脚本，使用更通用的UI元素查找方法，避免具体索引引用。脚本将尝试多种方法来定位微信界面元素，并提供详细的错误处理和用户指导。
生成时间: 2026-03-21 11:29:54
"""

# skill_name: macos_wechat_automation_improved

import subprocess
import time
import json
from typing import Dict, Any, List, Optional
import os

def main(args=None) -> Dict[str, Any]:
    """
    改进版的macOS微信自动化脚本，使用更通用的UI元素查找方法
    避免具体索引引用，尝试多种方法来定位微信界面元素
    提供详细的错误处理和用户指导
    """
    if args is None:
        args = {}
    
    # 检查微信是否已安装
    if not is_wechat_installed():
        return {
            'result': {'error': '微信未安装'},
            'insights': ['微信应用未在系统中找到，请先安装微信'],
            'capabilities': ['macos_wechat_automation_improved']
        }
    
    # 检查是否已运行
    if not is_wechat_running():
        return {
            'result': {'error': '微信未运行'},
            'insights': ['微信应用未运行，请先启动微信并登录'],
            'capabilities': ['macos_wechat_automation_improved']
        }
    
    # 尝试执行微信自动化操作
    try:
        result = perform_wechat_automation(args)
        return {
            'result': result,
            'insights': ['微信自动化操作完成'],
            'capabilities': ['macos_wechat_automation_improved']
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'微信自动化操作失败: {str(e)}'],
            'capabilities': ['macos_wechat_automation_improved']
        }

def is_wechat_installed() -> bool:
    """检查微信是否已安装"""
    try:
        result = subprocess.run(['open', '-Ra', 'WeChat'], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def is_wechat_running() -> bool:
    """检查微信是否正在运行"""
    try:
        result = subprocess.run(['pgrep', 'WeChat'], capture_output=True, text=True)
        return len(result.stdout) > 0
    except subprocess.CalledProcessError:
        return False

def execute_applescript(script: str) -> str:
    """执行AppleScript并返回结果"""
    try:
        result = subprocess.run(['osascript', '-e', script], 
                                capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"AppleScript执行失败: {e.stderr}")

def find_wechat_window() -> str:
    """查找微信窗口"""
    script = '''
    tell application "System Events"
        tell process "WeChat"
            if (count of windows) > 0 then
                return name of first window
            else
                return "无窗口"
            end if
        end tell
    end tell
    '''
    return execute_applescript(script)

def find_element_by_description(description: str) -> Optional[str]:
    """通过描述查找UI元素"""
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            try
                set targetElement to first UI element of ¬
                    (every UI element whose description is "{description}")
                return "found"
            on error
                return "not found"
            end try
        end tell
    end tell
    '''
    result = execute_applescript(script)
    return result if result == "found" else None

def find_element_by_title(title: str) -> Optional[str]:
    """通过标题查找UI元素"""
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            try
                set targetElement to first UI element of ¬
                    (every UI element whose title is "{title}")
                return "found"
            on error
                return "not found"
            end try
        end tell
    end tell
    '''
    result = execute_applescript(script)
    return result if result == "found" else None

def find_element_by_role(role: str) -> Optional[str]:
    """通过角色查找UI元素"""
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            try
                set targetElement to first UI element of ¬
                    (every UI element whose role is "{role}")
                return "found"
            on error
                return "not found"
            end try
        end tell
    end tell
    '''
    result = execute_applescript(script)
    return result if result == "found" else None

def find_element_by_value(value: str) -> Optional[str]:
    """通过值查找UI元素"""
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            try
                set targetElement to first UI element of ¬
                    (every UI element whose value is "{value}")
                return "found"
            on error
                return "not found"
            end try
        end tell
    end tell
    '''
    result = execute_applescript(script)
    return result if result == "found" else None

def find_element_by_class_name(class_name: str) -> Optional[str]:
    """通过类名查找UI元素"""
    script = f'''
    tell application "System Events"
        tell process "WeChat"
            try
                set targetElement to first UI element of ¬
                    (every UI element whose class is "{class_name}")
                return "found"
            on error
                return "not found"
            end try
        end tell
    end tell
    '''
    result = execute_applescript(script)
    return result if result == "found" else None

def find_all_elements() -> List[str]:
    """查找所有微信UI元素"""
    script = '''
    tell application "System Events"
        tell process "WeChat"
            set allElements to every UI element
            set elementList to {}
            repeat with i from 1 to count of allElements
                set thisElement to item i of allElements
                set end of elementList to (name of thisElement) & ":" & (description of thisElement) & ":" & (title of thisElement) & ":" & (role of thisElement)
            end repeat
            return elementList
        end tell
    end tell
    '''
    try:
        result = execute_applescript(script)
        return result.split('\n') if result else []
    except:
        return []

def find_element_by_multiple_criteria(criteria_list: List[Dict[str, str]]) -> Optional[str]:
    """通过多种条件查找UI元素"""
    for criteria in criteria_list:
        if 'description' in criteria:
            result = find_element_by_description(criteria['description'])
            if result:
                return criteria['description']
        elif 'title' in criteria:
            result = find_element_by_title(criteria['title'])
            if result:
                return criteria['title']
        elif 'role' in criteria:
            result = find_element_by_role(criteria['role'])
            if result:
                return criteria['role']
        elif 'value' in criteria:
            result = find_element_by_value(criteria['value'])
            if result:
                return criteria['value']
        elif 'class_name' in criteria:
            result = find_element_by_class_name(criteria['class_name'])
            if result:
                return criteria['class_name']
    return None

def simulate_click_on_element(target_element: str, method: str) -> bool:
    """模拟点击指定元素"""
    if method == 'description':
        script = f'''
        tell application "System Events"
            tell process "WeChat"
                click (first UI element whose description is "{target_element}")
            end tell
        end tell
        '''
    elif method == 'title':
        script = f'''
        tell application "System Events"
            tell process "WeChat"
                click (first UI element whose title is "{target_element}")
            end tell
        end tell
        '''
    elif method == 'role':
        script = f'''
        tell application "System Events"
            tell process "WeChat"
                click (first UI element whose role is "{target_element}")
            end tell
        end tell
        '''
    else:
        return False
    
    try:
        execute_applescript(script)
        return True
    except:
        return False

def send_text_to_wechat(text: str) -> bool:
    """发送文本到微信"""
    try:
        # 检查是否在微信窗口中
        window_name = find_wechat_window()
        if window_name == "无窗口":
            return False
        
        # 模拟粘贴文本
        subprocess.run(['osascript', '-e', 'tell application "WeChat" to activate'])
        time.sleep(0.5)
        subprocess.run(['osascript', '-e', f'clipboard to "{text}"'])
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "v" using {command down}'])
        time.sleep(0.1)
        
        # 模拟回车发送
        subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke return'])
        return True
    except:
        return False

def perform_wechat_automation(args: Dict[str, Any]) -> Dict[str, Any]:
    """执行微信自动化操作"""
    # 检查参数
    action = args.get('action', 'send_text')
    text = args.get('text', '')
    
    # 验证微信是否可用
    if not is_wechat_running():
        raise Exception("微信未运行，请先启动微信并登录")
    
    # 激活微信窗口
    subprocess.run(['osascript', '-e', 'tell application "WeChat" to activate'])
    time.sleep(1)
    
    if action == 'send_text':
        if not text:
            raise Exception("未提供要发送的文本")
        
        success = send_text_to_wechat(text)
        if not success:
            raise Exception("发送文本到微信失败")
        
        return {
            'action': 'send_text',
            'text': text,
            'status': 'success',
            'message': '文本已发送到微信'
        }
    
    elif action == 'find_elements':
        elements = find_all_elements()
        return {
            'action': 'find_elements',
            'status': 'success',
            'elements': elements,
            'element_count': len(elements)
        }
    
    elif action == 'find_specific_element':
        criteria = args.get('criteria', [])
        if not criteria:
            raise Exception("未提供查找条件")
        
        found_element = find_element_by_multiple_criteria(criteria)
        if found_element:
            return {
                'action': 'find_specific_element',
                'status': 'success',
                'found_element': found_element,
                'message': f'找到元素: {found_element}'
            }
        else:
            return {
                'action': 'find_specific_element',
                'status': 'not_found',
                'found_element': None,
                'message': '未找到指定元素'
            }
    
    elif action == 'click_element':
        criteria = args.get('criteria', [])
        if not criteria:
            raise Exception("未提供点击条件")
        
        found_element = find_element_by_multiple_criteria(criteria)
        if not found_element:
            raise Exception("未找到要点击的元素")
        
        # 确定点击方法
        method = 'description'
        for criteria_item in criteria:
            if criteria_item.get('description') == found_element:
                method = 'description'
                break
            elif criteria_item.get('title') == found_element:
                method = 'title'
                break
            elif criteria_item.get('role') == found_element:
                method = 'role'
                break
        
        success = simulate_click_on_element(found_element, method)
        if not success:
            raise Exception("点击元素失败")
        
        return {
            'action': 'click_element',
            'status': 'success',
            'clicked_element': found_element,
            'message': f'已点击元素: {found_element}'
        }
    
    else:
        raise Exception(f"不支持的操作: {action}")