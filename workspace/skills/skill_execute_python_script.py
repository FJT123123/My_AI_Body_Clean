"""
自动生成的技能模块
需求: 执行指定路径的Python脚本文件并返回结果
生成时间: 2026-03-22 03:58:02
"""

# skill_name: execute_python_script
import subprocess
import os
import sys
import json

def main(args=None):
    """
    执行指定路径的Python脚本文件并返回结果
    
    参数:
    - script_path: 要执行的Python脚本文件路径
    - script_args: 传递给脚本的参数列表（可选）
    """
    if args is None:
        args = {}
    
    script_path = args.get('script_path', '')
    script_args = args.get('script_args', [])
    
    # 检查脚本文件是否存在
    if not script_path:
        return {
            'result': {'error': 'script_path 参数缺失'},
            'insights': ['执行失败：未提供脚本路径'],
            'facts': [('execute_python_script', 'status', 'failed due to missing script_path')]
        }
    
    if not os.path.exists(script_path):
        return {
            'result': {'error': f'脚本文件不存在: {script_path}'},
            'insights': [f'执行失败：脚本文件不存在: {script_path}'],
            'facts': [('execute_python_script', 'status', 'failed due to file not found')]
        }
    
    if not script_path.endswith('.py'):
        return {
            'result': {'error': f'不是Python脚本文件: {script_path}'},
            'insights': [f'执行失败：文件不是Python脚本: {script_path}'],
            'facts': [('execute_python_script', 'status', 'failed due to invalid file type')]
        }
    
    try:
        # 准备执行命令
        cmd = [sys.executable, script_path] + script_args
        
        # 执行脚本
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 设置30秒超时
        )
        
        # 收集执行结果
        execution_result = {
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'command': ' '.join(cmd)
        }
        
        if result.returncode == 0:
            status = 'success'
            insight = f'脚本执行成功: {script_path}'
        else:
            status = 'failed'
            insight = f'脚本执行失败: {script_path}，返回码: {result.returncode}'
        
        return {
            'result': execution_result,
            'insights': [insight],
            'facts': [('execute_python_script', 'status', status), 
                     ('execute_python_script', 'script_path', script_path),
                     ('execute_python_script', 'return_code', str(result.returncode))]
        }
        
    except subprocess.TimeoutExpired:
        return {
            'result': {'error': '脚本执行超时（超过30秒）'},
            'insights': ['执行失败：脚本执行超时'],
            'facts': [('execute_python_script', 'status', 'timeout')]
        }
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'执行异常：{str(e)}'],
            'facts': [('execute_python_script', 'status', 'exception')]
        }