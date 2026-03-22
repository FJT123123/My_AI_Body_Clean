"""
自动生成的技能模块
需求: 执行SQL脚本文件来修改数据库结构
生成时间: 2026-03-22 04:07:52
"""

# skill_name: execute_sql_script_file
import sqlite3
import os
import re

def main(args=None):
    """
    执行SQL脚本文件来修改数据库结构
    输入参数应包含sql_script_path和db_path，该技能将执行SQL脚本文件来修改数据库结构
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    sql_script_path = args.get('sql_script_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库路径不可用'},
            'insights': ['无法访问数据库文件'],
            'facts': [('database', 'access_status', 'unavailable')]
        }
    
    if not sql_script_path or not os.path.exists(sql_script_path):
        return {
            'result': {'error': 'SQL脚本路径不可用'},
            'insights': ['无法访问SQL脚本文件'],
            'facts': [('sql_script', 'access_status', 'unavailable')]
        }
    
    try:
        # 读取SQL脚本文件内容
        with open(sql_script_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行SQL脚本
        # 分割SQL语句，处理多个语句的情况
        sql_statements = re.split(r';\s*(?=\n|$)', sql_script)
        executed_statements = []
        
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                executed_statements.append(statement)
        
        # 提交更改
        conn.commit()
        
        # 获取执行结果
        rows_affected = cursor.rowcount
        executed_count = len(executed_statements)
        
        # 关闭连接
        conn.close()
        
        return {
            'result': {
                'status': 'success',
                'executed_statements': executed_count,
                'rows_affected': rows_affected,
                'db_path': db_path,
                'script_path': sql_script_path
            },
            'insights': [f'成功执行SQL脚本，执行了{executed_count}个语句', f'影响了{rows_affected}行数据'],
            'facts': [
                ('database', 'modified', db_path),
                ('sql_script', 'executed', sql_script_path),
                ('executed_statements_count', 'value', executed_count)
            ],
            'memories': [
                f'执行SQL脚本文件: {sql_script_path}，修改了数据库: {db_path}，执行了{executed_count}个语句'
            ]
        }
        
    except sqlite3.Error as e:
        return {
            'result': {
                'error': f'SQLite错误: {str(e)}',
                'sql_script_path': sql_script_path,
                'db_path': db_path
            },
            'insights': ['SQL执行过程中出现错误'],
            'facts': [
                ('database', 'error_occurred', db_path),
                ('sql_error', 'message', str(e))
            ],
            'memories': [f'SQL脚本执行失败: {str(e)}']
        }
    
    except Exception as e:
        return {
            'result': {
                'error': f'执行异常: {str(e)}',
                'sql_script_path': sql_script_path,
                'db_path': db_path
            },
            'insights': ['执行SQL脚本时发生异常'],
            'facts': [
                ('execution', 'error_occurred', True),
                ('error_message', 'value', str(e))
            ],
            'memories': [f'执行SQL脚本异常: {str(e)}']
        }