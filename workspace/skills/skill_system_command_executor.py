"""
自动生成的技能模块
需求: 运行系统命令并返回结果
生成时间: 2026-03-22 03:18:18
"""

# skill_name: system_command_executor
import subprocess
import os
import sys

def main(args=None):
    """
    执行系统命令并返回结果
    参数:
        command: 要执行的系统命令字符串
        shell: 是否使用shell执行，默认True
        timeout: 命令超时时间，默认30秒
    """
    if args is None:
        args = {}
    
    command = args.get('command', '')
    shell = args.get('shell', True)
    timeout = args.get('timeout', 30)
    
    if not command:
        return {
            'result': {'error': '命令不能为空'},
            'insights': ['缺少command参数'],
            'facts': []
        }
    
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # 获取执行结果
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        return_code = result.returncode
        
        # 构建返回结果
        execution_result = {
            'command': command,
            'return_code': return_code,
            'stdout': stdout,
            'stderr': stderr,
            'success': return_code == 0
        }
        
        # 根据执行结果添加洞察
        insights = []
        if return_code == 0:
            insights.append(f'命令执行成功: {command}')
            if stdout:
                insights.append(f'命令输出长度: {len(stdout)} 字符')
        else:
            insights.append(f'命令执行失败，返回码: {return_code}')
            if stderr:
                insights.append(f'错误信息: {stderr}')
        
        # 统计信息
        facts = [
            ['command_execution', 'command', command],
            ['command_execution', 'return_code', str(return_code)],
            ['command_execution', 'success', str(return_code == 0)]
        ]
        
        return {
            'result': execution_result,
            'insights': insights,
            'facts': facts
        }
        
    except subprocess.TimeoutExpired:
        timeout_result = {
            'command': command,
            'error': f'命令执行超时，超过 {timeout} 秒',
            'success': False
        }
        
        return {
            'result': timeout_result,
            'insights': [f'命令执行超时: {command}'],
            'facts': [
                ['command_execution', 'command', command],
                ['command_execution', 'error', 'timeout'],
                ['command_execution', 'success', 'False']
            ]
        }
    except Exception as e:
        error_result = {
            'command': command,
            'error': str(e),
            'success': False
        }
        
        return {
            'result': error_result,
            'insights': [f'命令执行异常: {str(e)}'],
            'facts': [
                ['command_execution', 'command', command],
                ['command_execution', 'error', str(e)],
                ['command_execution', 'success', 'False']
            ]
        }