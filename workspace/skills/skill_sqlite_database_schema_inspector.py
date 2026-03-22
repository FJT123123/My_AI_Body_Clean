"""
自动生成的技能模块
需求: 检查SQLite数据库的表结构，包括表名、列名、数据类型等信息
生成时间: 2026-03-22 07:28:13
"""

# skill_name: sqlite_database_schema_inspector

import sqlite3
import os

def main(args=None):
    """
    检查SQLite数据库的表结构，包括表名、列名、数据类型等信息
    输入参数应包含数据库路径信息
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 如果没有从上下文获取到db_path，尝试从args直接获取
    if not db_path:
        db_path = args.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库路径不可用或文件不存在'},
            'insights': ['无法访问指定的数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_info = {}
        
        for table in tables:
            table_name = table[0]
            # 获取表的列信息
            table_info = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
            
            columns = []
            for col in table_info:
                column_info = {
                    'cid': col[0],  # 列ID
                    'name': col[1],  # 列名
                    'type': col[2],  # 数据类型
                    'not_null': bool(col[3]),  # 是否非空
                    'default_value': col[4],  # 默认值
                    'primary_key': bool(col[5])  # 是否为主键
                }
                columns.append(column_info)
            
            # 获取表的索引信息
            indexes_query = f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';"
            index_result = cursor.execute(indexes_query).fetchall()
            indexes = [idx[0] for idx in index_result]
            
            schema_info[table_name] = {
                'columns': columns,
                'indexes': indexes
            }
        
        conn.close()
        
        # 收集洞察信息
        table_count = len(schema_info)
        total_columns = sum(len(table['columns']) for table in schema_info.values())
        insights = [
            f"数据库包含 {table_count} 个表",
            f"总计 {total_columns} 个列",
            f"表结构分析完成"
        ]
        
        return {
            'result': {
                'database_path': db_path,
                'schema': schema_info,
                'table_count': table_count,
                'total_columns': total_columns
            },
            'insights': insights,
            'facts': [
                ['数据库', '包含', f'{table_count} 个表'],
                ['数据库', '路径', db_path]
            ],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f'数据库表结构分析完成，发现 {table_count} 个表',
                    'importance': 0.8,
                    'timestamp': 'now',
                    'tags': ['database', 'schema', 'analysis']
                }
            ]
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库连接或查询失败'],
            'facts': [],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f'数据库表结构分析失败: {str(e)}',
                    'importance': 0.9,
                    'timestamp': 'now',
                    'tags': ['database', 'error']
                }
            ]
        }
    except Exception as e:
        return {
            'result': {'error': f'其他错误: {str(e)}'},
            'insights': ['执行过程中发生未知错误'],
            'facts': [],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f'数据库表结构分析失败: {str(e)}',
                    'importance': 0.9,
                    'timestamp': 'now',
                    'tags': ['database', 'error']
                }
            ]
        }