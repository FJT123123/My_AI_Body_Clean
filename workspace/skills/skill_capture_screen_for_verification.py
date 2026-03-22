"""
自动生成的技能模块
需求: 截取当前屏幕截图并保存到临时文件，用于后续视觉分析验证微信消息是否成功发送
生成时间: 2026-03-21 11:36:39
"""

# skill_name: capture_screen_for_verification

def main(args=None):
    """
    截取当前屏幕截图并保存到临时文件，用于后续视觉分析验证微信消息是否成功发送
    
    参数:
    - args: 包含截图参数的字典，可选
        - output_path: 指定截图保存路径，可选
        - delay: 截图前延迟秒数，可选，默认为0
    """
    import os
    import tempfile
    import time
    from datetime import datetime
    
    args = args or {}
    delay = args.get('delay', 0)
    
    # 检查系统类型并导入相应截图库
    import platform
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        import subprocess
        screenshot_path = args.get('output_path') or os.path.join(tempfile.gettempdir(), f"screen_capture_{int(datetime.now().timestamp())}.png")
        try:
            if delay > 0:
                time.sleep(delay)
            result = subprocess.run(['screencapture', '-x', screenshot_path], capture_output=True, text=True)
            if result.returncode == 0:
                return {
                    'result': {'screenshot_path': screenshot_path, 'success': True},
                    'insights': [f'屏幕截图已成功保存到: {screenshot_path}'],
                    'memories': [{'event_type': 'skill_executed', 'content': f'截取屏幕截图: {screenshot_path}', 'importance': 0.5}]
                }
            else:
                return {
                    'result': {'error': f'截图失败: {result.stderr}', 'success': False},
                    'insights': ['截取屏幕截图失败']
                }
        except Exception as e:
            return {
                'result': {'error': str(e), 'success': False},
                'insights': ['截取屏幕截图时发生异常']
            }
    
    elif system == 'windows':  # Windows
        try:
            import pyautogui
            screenshot_path = args.get('output_path') or os.path.join(tempfile.gettempdir(), f"screen_capture_{int(datetime.now().timestamp())}.png")
            if delay > 0:
                time.sleep(delay)
            screenshot = pyautogui.screenshot()
            screenshot.save(screenshot_path)
            return {
                'result': {'screenshot_path': screenshot_path, 'success': True},
                'insights': [f'屏幕截图已成功保存到: {screenshot_path}'],
                'memories': [{'event_type': 'skill_executed', 'content': f'截取屏幕截图: {screenshot_path}', 'importance': 0.5}]
            }
        except ImportError:
            # 尝试使用PIL
            try:
                from PIL import ImageGrab
                screenshot_path = args.get('output_path') or os.path.join(tempfile.gettempdir(), f"screen_capture_{int(datetime.now().timestamp())}.png")
                if delay > 0:
                    time.sleep(delay)
                screenshot = ImageGrab.grab()
                screenshot.save(screenshot_path)
                return {
                    'result': {'screenshot_path': screenshot_path, 'success': True},
                    'insights': [f'屏幕截图已成功保存到: {screenshot_path}'],
                    'memories': [{'event_type': 'skill_executed', 'content': f'截取屏幕截图: {screenshot_path}', 'importance': 0.5}]
                }
            except ImportError:
                return {
                    'result': {'error': 'Windows系统缺少截图库(pyautogui或PIL)', 'success': False},
                    'insights': ['当前系统缺少截图所需的库']
                }
        except Exception as e:
            return {
                'result': {'error': str(e), 'success': False},
                'insights': ['截取屏幕截图时发生异常']
            }
    
    elif system == 'linux':  # Linux
        screenshot_path = args.get('output_path') or os.path.join(tempfile.gettempdir(), f"screen_capture_{int(datetime.now().timestamp())}.png")
        try:
            # 尝试使用gnome-screenshot
            result = subprocess.run(['which', 'gnome-screenshot'], capture_output=True, text=True)
            if result.returncode == 0:
                if delay > 0:
                    time.sleep(delay)
                result = subprocess.run(['gnome-screenshot', '-f', screenshot_path], capture_output=True, text=True)
                if result.returncode == 0:
                    return {
                        'result': {'screenshot_path': screenshot_path, 'success': True},
                        'insights': [f'屏幕截图已成功保存到: {screenshot_path}'],
                        'memories': [{'event_type': 'skill_executed', 'content': f'截取屏幕截图: {screenshot_path}', 'importance': 0.5}]
                    }
                else:
                    return {
                        'result': {'error': f'gnome-screenshot失败: {result.stderr}', 'success': False},
                        'insights': ['使用gnome-screenshot截图失败']
                    }
            else:
                # 尝试使用scrot
                result = subprocess.run(['which', 'scrot'], capture_output=True, text=True)
                if result.returncode == 0:
                    if delay > 0:
                        time.sleep(delay)
                    result = subprocess.run(['scrot', screenshot_path], capture_output=True, text=True)
                    if result.returncode == 0:
                        return {
                            'result': {'screenshot_path': screenshot_path, 'success': True},
                            'insights': [f'屏幕截图已成功保存到: {screenshot_path}'],
                            'memories': [{'event_type': 'skill_executed', 'content': f'截取屏幕截图: {screenshot_path}', 'importance': 0.5}]
                        }
                    else:
                        return {
                            'result': {'error': f'scrot失败: {result.stderr}', 'success': False},
                            'insights': ['使用scrot截图失败']
                        }
                else:
                    return {
                        'result': {'error': 'Linux系统缺少截图工具(gnome-screenshot或scrot)', 'success': False},
                        'insights': ['当前系统缺少截图所需的工具']
                    }
        except Exception as e:
            return {
                'result': {'error': str(e), 'success': False},
                'insights': ['截取屏幕截图时发生异常']
            }
    
    else:
        return {
            'result': {'error': f'不支持当前操作系统: {system}', 'success': False},
            'insights': [f'当前操作系统 {system} 不支持截图功能']
        }