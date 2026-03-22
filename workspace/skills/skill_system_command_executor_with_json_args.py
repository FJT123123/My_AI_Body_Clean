"""
自动生成的技能模块
需求: 正确处理run_skill参数传递的系统命令执行器，能够处理字符串或字典格式的输入
生成时间: 2026-03-21 13:42:17
"""

# skill_name: system_command_executor_with_json_args
import subprocess
import json
import os
import sys

def main(args=None):
    """
    执行系统命令的技能，支持字符串或字典格式的参数输入
    如果输入是字典格式，会提取command键执行命令
    如果输入是字符串格式，直接执行该命令
    返回命令执行结果的结构化数据
    """
    if args is None:
        args = {}
    
    # 检查输入参数格式
    command = None
    if isinstance(args, dict):
        # 如果是字典格式，尝试从command键获取命令
        if 'command' in args:
            command = args['command']
        elif 'cmd' in args:
            command = args['cmd']
        else:
            # 如果字典中没有command或cmd键，尝试直接使用整个字典作为命令参数
            command = json.dumps(args)
    elif isinstance(args, str):
        # 如果是字符串格式，直接使用
        command = args
    else:
        return {
            'result': {'error': '输入参数格式不正确，应为字符串或包含command键的字典'},
            'insights': ['参数格式错误', '支持字符串或字典格式输入'],
            'facts': [('command_executor', 'requires', 'string_or_dict_input')]
        }
    
    # 验证command是否为字符串
    if not isinstance(command, str):
        return {
            'result': {'error': '命令必须是字符串格式'},
            'insights': ['命令格式错误'],
            'facts': [('command_executor', 'requires', 'string_command')]
        }
    
    # 执行命令
    try:
        # 使用shell=True以支持复杂的命令，如管道等
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30  # 设置超时时间
        )
        
        # 检查命令是否成功执行
        success = result.returncode == 0
        
        # 返回结果
        output = {
            'result': {
                'command': command,
                'return_code': result.returncode,
                'stdout': result.stdout.strip() if result.stdout else '',
                'stderr': result.stderr.strip() if result.stderr else '',
                'success': success
            },
            'insights': [],
            'facts': [('command', 'executed', command)]
        }
        
        # 添加执行结果洞察
        if success:
            output['insights'].append(f'命令执行成功: {command}')
            if result.stdout:
                output['insights'].append(f'标准输出: {result.stdout[:100]}...')  # 只显示前100个字符
        else:
            output['insights'].append(f'命令执行失败: {command}')
            if result.stderr:
                output['insights'].append(f'错误信息: {result.stderr[:100]}...')  # 只显示前100个字符
        
        # 如果有标准输出，添加到facts
        if result.stdout:
            output['facts'].append(('command_output', 'contains', result.stdout[:50] + '...' if len(result.stdout) > 50 else result.stdout))
        
        return output
        
    except subprocess.TimeoutExpired:
        return {
            'result': {'error': f'命令执行超时: {command}', 'command': command},
            'insights': ['命令执行超时，可能需要优化或检查命令逻辑'],
            'facts': [('command', 'timeout', command)]
        }
    except Exception as e:
        return {
            'result': {'error': f'执行命令时发生错误: {str(e)}', 'command': command},
            'insights': [f'命令执行异常: {str(e)}'],
            'facts': [('command', 'error', str(e))]
        }