"""
自动生成的技能模块
需求: 直接执行Python代码文件，使用exec函数而不是subprocess
生成时间: 2026-03-22 03:58:39
"""

# skill_name: execute_python_file
import os
import sys
from io import StringIO
import traceback

def main(args=None):
    """
    执行Python代码文件，使用exec函数而不是subprocess
    args: 包含file_path参数的字典
    """
    if args is None:
        args = {}
    
    file_path = args.get('file_path', '')
    
    if not file_path:
        return {
            'result': {'error': 'file_path参数缺失'},
            'insights': [],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(file_path):
        return {
            'result': {'error': f'文件不存在: {file_path}'},
            'insights': [],
            'facts': [],
            'memories': []
        }
    
    if not file_path.endswith('.py'):
        return {
            'result': {'error': '文件不是Python文件'},
            'insights': [],
            'facts': [],
            'memories': []
        }
    
    # 读取Python文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return {
            'result': {'error': f'读取文件失败: {str(e)}'},
            'insights': [],
            'facts': [],
            'memories': []
        }
    
    # 重定向标准输出以捕获执行结果
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture
        
        # 执行Python代码
        exec_globals = {
            '__name__': '__main__',
            '__file__': file_path,
            '__builtins__': __builtins__
        }
        exec(code, exec_globals)
        
        # 获取输出
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        execution_result = {
            'success': True,
            'file_path': file_path,
            'stdout': stdout_output,
            'stderr': stderr_output,
            'return_code': 0
        }
        
        insights = [f'成功执行Python文件: {file_path}']
        facts = []
        memories = []
        
    except Exception as e:
        stderr_output = stderr_capture.getvalue()
        error_traceback = traceback.format_exc()
        execution_result = {
            'success': False,
            'file_path': file_path,
            'error': str(e),
            'traceback': error_traceback,
            'stderr': stderr_output,
            'return_code': 1
        }
        
        insights = [f'执行Python文件失败: {file_path}, 错误: {str(e)}']
        facts = []
        memories = []
    
    finally:
        # 恢复标准输出
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        stdout_capture.close()
        stderr_capture.close()
    
    return {
        'result': execution_result,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }