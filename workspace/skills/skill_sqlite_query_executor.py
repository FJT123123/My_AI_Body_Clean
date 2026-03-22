"""
自动生成的技能模块
需求: 执行SQL查询在SQLite数据库上，支持查询和修改操作
生成时间: 2026-03-22 03:13:35
"""

# skill_name: sqlite_query_executor
import sqlite3
import os
import json
from typing import Dict, Any, List, Tuple

def main(args=None) -> Dict[str, Any]:
    """
    执行SQL查询在SQLite数据库上，支持查询和修改操作
    
    Args:
        args: 包含查询参数的字典，必须包含 '__context__' 和 'query'
              可选参数: 'parameters' (SQL参数), 'db_path' (数据库路径)
    
    Returns:
        Dict[str, Any]: 包含执行结果的结构化字典
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = args.get('db_path', context.get('db_path', ''))
    query = args.get('query', '')
    parameters = args.get('parameters', ())
    
    # 检查数据库路径是否存在
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库路径不可用或不存在'},
            'insights': ['无法访问数据库文件'],
            'facts': [('database', 'path_status', 'not_found')]
        }
    
    if not query:
        return {
            'result': {'error': '查询语句为空'},
            'insights': ['缺少SQL查询语句'],
            'facts': [('query', 'status', 'empty')]
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行查询
        if isinstance(parameters, (list, tuple)):
            cursor.execute(query, parameters)
        else:
            cursor.execute(query, (parameters,))
        
        # 确定是否为查询语句
        query_upper = query.strip().upper()
        is_query = query_upper.startswith('SELECT') or query_upper.startswith('PRAGMA')
        
        if is_query:
            # 获取列名
            column_names = [description[0] for description in cursor.description] if cursor.description else []
            # 获取结果
            rows = cursor.fetchall()
            result_data = {
                'rows': rows,
                'columns': column_names,
                'count': len(rows),
                'query_type': 'SELECT'
            }
        else:
            # 提交事务
            conn.commit()
            result_data = {
                'rows_affected': cursor.rowcount,
                'last_row_id': cursor.lastrowid,
                'query_type': 'MODIFY'
            }
        
        # 获取数据库信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'result': result_data,
            'insights': [f'执行了{result_data["query_type"]}查询', f'数据库包含{len(tables)}个表'],
            'facts': [
                ('database', 'path', db_path),
                ('query', 'type', result_data['query_type']),
                ('database', 'table_count', len(tables))
            ],
            'memories': [
                f"执行SQL查询: {query[:100]}{'...' if len(query) > 100 else ''}",
                f"查询影响行数: {result_data.get('rows_affected', result_data.get('count', 0))}"
            ]
        }
        
    except sqlite3.Error as e:
        conn.close()
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': [f'SQL执行失败: {str(e)}'],
            'facts': [('query', 'status', 'failed'), ('error', 'type', 'sqlite_error')]
        }
    except Exception as e:
        return {
            'result': {'error': f'执行错误: {str(e)}'},
            'insights': [f'执行过程中发生错误: {str(e)}'],
            'facts': [('query', 'status', 'failed'), ('error', 'type', 'execution_error')]
        }