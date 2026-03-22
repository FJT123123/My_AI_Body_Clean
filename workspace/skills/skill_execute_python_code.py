"""
自动生成的技能模块
需求: 执行任意Python代码并返回结果
生成时间: 2026-03-22 03:15:11
"""

# skill_name: execute_python_code

import subprocess
import sys
import os
import tempfile
import json
import traceback

def main(args=None):
    """
    执行任意Python代码并返回结果
    
    Args:
        args: 包含 'code' 键的字典，值为要执行的Python代码字符串
        可选参数：
        - 'timeout': 执行超时时间（秒），默认30秒
        - 'capture_output': 是否捕获输出，默认True
        - 'return_dict': 是否返回字典格式结果，默认True
    
    Returns:
        dict: 包含执行结果、错误信息、执行时间等的结构化数据
    """
    if args is None:
        args = {}
    
    code = args.get('code', '')
    timeout = args.get('timeout', 30)
    capture_output = args.get('capture_output', True)
    return_dict = args.get('return_dict', True)
    
    if not code:
        return {
            'result': {'error': '未提供代码'},
            'insights': ['执行失败：缺少代码参数'],
            'facts': [],
            'memories': []
        }
    
    # 创建临时文件来执行代码
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        # 执行Python代码
        if capture_output:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            stdout = result.stdout
            stderr = result.stderr
            exit_code = result.returncode
        else:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                timeout=timeout
            )
            stdout = ""
            stderr = ""
            exit_code = result.returncode

        # 检查执行结果
        execution_success = exit_code == 0
        output = stdout if execution_success else stderr
        
        # 构建结果
        result_data = {
            'success': execution_success,
            'exit_code': exit_code,
            'output': output,
            'stdout': stdout,
            'stderr': stderr,
            'code_executed': code
        }
        
        if execution_success:
            insights = ['Python代码执行成功']
        else:
            insights = ['Python代码执行失败']
        
        return {
            'result': result_data,
            'insights': insights,
            'facts': [
                ['executed_code', 'exit_code', str(exit_code)],
                ['executed_code', 'success', str(execution_success)],
            ],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f"执行Python代码: 退出码 {exit_code}",
                    'tags': ['execution', 'python']
                }
            ]
        }
    
    except subprocess.TimeoutExpired:
        return {
            'result': {
                'error': f'执行超时（超过{timeout}秒）',
                'success': False,
                'code_executed': code
            },
            'insights': ['代码执行超时'],
            'facts': [
                ['executed_code', 'timeout', str(timeout)],
                ['executed_code', 'success', 'False'],
            ],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f"Python代码执行超时: {timeout}秒",
                    'tags': ['execution', 'timeout']
                }
            ]
        }
    
    except Exception as e:
        return {
            'result': {
                'error': str(e),
                'success': False,
                'code_executed': code
            },
            'insights': ['执行过程中发生异常'],
            'facts': [
                ['executed_code', 'exception', str(e)],
                ['executed_code', 'success', 'False'],
            ],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f"执行Python代码时发生异常: {str(e)}",
                    'tags': ['execution', 'exception']
                }
            ]
        }
    
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except:
            pass  # 如果无法删除临时文件，忽略错误