"""
自动生成的技能模块
需求: 分析SQLite数据库结构，特别是v3_episodic_memory.db中的表结构，返回所有表名和列信息
生成时间: 2026-03-22 07:22:43
"""

# skill_name: analyze_sqlite_database_schema

import sqlite3
import os
import json

def main(args=None):
    """
    分析SQLite数据库结构，获取所有表名和列信息
    
    参数:
        args: 包含数据库路径的参数字典，必需包含 '__context__' 键，其中包含 'db_path'
    
    返回:
        包含数据库结构信息的字典
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或数据库文件不存在'},
            'insights': ['无法访问数据库文件'],
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
            table_info = cursor.execute(f"PRAGMA table_info('{table_name}');").fetchall()
            
            columns = []
            for col in table_info:
                column_info = {
                    'id': col[0],
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                }
                columns.append(column_info)
            
            # 获取表的索引信息
            indexes_query = f"SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}';"
            index_info = cursor.execute(indexes_query).fetchall()
            indexes = [idx[0] for idx in index_info]
            
            schema_info[table_name] = {
                'columns': columns,
                'indexes': indexes
            }
        
        conn.close()
        
        # 生成分析报告
        table_count = len(schema_info)
        total_columns = sum(len(table['columns']) for table in schema_info.values())
        
        insights = [
            f"数据库包含 {table_count} 个表",
            f"数据库总共有 {total_columns} 个列",
            f"数据库文件路径: {db_path}"
        ]
        
        # 为每个表生成洞察
        for table_name, table_info in schema_info.items():
            columns_info = [col['name'] for col in table_info['columns']]
            insights.append(f"表 '{table_name}' 包含列: {', '.join(columns_info)}")
        
        return {
            'result': {
                'database_path': db_path,
                'schema': schema_info,
                'table_count': table_count,
                'total_columns': total_columns
            },
            'insights': insights,
            'facts': [
                ['database', 'has_path', db_path],
                ['database', 'has_table_count', str(table_count)],
                ['database', 'has_total_columns', str(total_columns)]
            ],
            'memories': [
                {
                    'event_type': 'workspace_analysis',
                    'content': f"数据库结构分析: {table_count} 个表，{total_columns} 个列",
                    'importance': 0.7,
                    'timestamp': None,
                    'tags': ['database_analysis']
                }
            ]
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库连接或查询失败'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'分析数据库时发生错误: {str(e)}'},
            'insights': ['分析数据库结构失败'],
            'facts': [],
            'memories': []
        }