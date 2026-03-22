#!/usr/bin/env python3
"""
Control macOS applications using AppleScript
"""
import subprocess
import sys

def main(input_args):
    """
    Control macOS applications using AppleScript
    
    Args:
        input_args (dict): Dictionary with the following structure:
            - input: JSON string or dict with app_name, action, etc.
            - __context__: Context information (ignored)
    
    Returns:
        dict: Result dictionary with success status and output/error
    """
    # Extract the actual parameters from the 'input' key
    if isinstance(input_args, dict) and 'input' in input_args:
        actual_input = input_args['input']
    else:
        actual_input = input_args
    
    # Handle both string and dict input
    if isinstance(actual_input, str):
        import json
        try:
            params = json.loads(actual_input)
        except json.JSONDecodeError:
            return {
                'result': {'error': 'input 必须是有效的JSON字符串或字典'},
                'insights': ['参数解析失败：input 格式错误'],
                'facts': [],
                'memories': []
            }
    else:
        params = actual_input
    
    # Extract parameters
    app_name = params.get('app_name')
    action = params.get('action')
    custom_script = params.get('script')
    
    # Validate required parameters
    if not custom_script and (not app_name or not action):
        return {
            'result': {'error': '必须提供 app_name 和 action，或者提供 script 参数'},
            'insights': ['参数校验失败：缺少必要的参数'],
            'facts': [],
            'memories': []
        }
    
    # Build AppleScript command
    if custom_script:
        applescript_cmd = custom_script
    else:
        # Standard actions
        if action == 'activate':
            applescript_cmd = f'tell application "{app_name}" to activate'
        elif action == 'quit':
            applescript_cmd = f'tell application "{app_name}" to quit'
        elif action == 'open':
            applescript_cmd = f'tell application "{app_name}" to open'
        elif action == 'close':
            applescript_cmd = f'tell application "{app_name}" to close'
        else:
            # Custom action
            applescript_cmd = f'tell application "{app_name}" to {action}'
    
    try:
        # Execute AppleScript
        result = subprocess.run(
            ['osascript', '-e', applescript_cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            output = result.stdout.strip() if result.stdout else "操作成功"
            return {
                'result': {
                    'success': True,
                    'output': output,
                    'app_name': app_name,
                    'action': action
                },
                'insights': [f'成功执行了对 {app_name} 的 {action} 操作'],
                'facts': [f'macOS应用控制: {app_name}.{action} = success'],
                'memories': [f'学会了使用AppleScript控制macOS应用: {app_name}']
            }
        else:
            error_msg = result.stderr.strip() if result.stderr else f"未知错误 (返回码: {result.returncode})"
            return {
                'result': {
                    'success': False,
                    'error': error_msg,
                    'app_name': app_name,
                    'action': action
                },
                'insights': [f'执行 {app_name} 的 {action} 操作时出错: {error_msg}'],
                'facts': [f'macOS应用控制失败: {app_name}.{action} = error'],
                'memories': [f'记录了macOS应用控制错误模式: {error_msg}']
            }
            
    except subprocess.TimeoutExpired:
        return {
            'result': {'error': 'AppleScript 执行超时'},
            'insights': ['AppleScript 执行时间过长，可能应用无响应'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'执行异常: {str(e)}'},
            'insights': [f'系统调用异常: {str(e)}'],
            'facts': [],
            'memories': []
        }

if __name__ == '__main__':
    # For direct execution
    import json
    if len(sys.argv) > 1:
        input_json = sys.argv[1]
    else:
        input_json = sys.stdin.read()
    
    try:
        input_dict = json.loads(input_json)
    except json.JSONDecodeError:
        input_dict = input_json
    
    result = main(input_dict)
    print(json.dumps(result, ensure_ascii=False))