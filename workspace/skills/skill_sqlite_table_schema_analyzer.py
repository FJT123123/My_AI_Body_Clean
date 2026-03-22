"""
自动生成的技能模块
需求: 查询SQLite数据库的表结构信息，包括表名、列名、数据类型和约束条件
生成时间: 2026-03-22 06:53:54
"""

# skill_name: sqlite_table_schema_analyzer

import sqlite3
import os
import json

def main(args=None):
    """
    查询SQLite数据库的表结构信息，包括表名、列名、数据类型和约束条件
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或文件不存在'},
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
            cursor.execute(f"PRAGMA table_info('{table_name}');")
            columns = cursor.fetchall()
            
            # 获取表的索引信息
            cursor.execute(f"PRAGMA index_list('{table_name}');")
            indexes = cursor.fetchall()
            
            # 获取表的外键信息
            cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
            foreign_keys = cursor.fetchall()
            
            table_info = {
                'columns': [],
                'indexes': [],
                'foreign_keys': []
            }
            
            # 处理列信息
            for col in columns:
                column_info = {
                    'cid': col[0],  # 列ID
                    'name': col[1],  # 列名
                    'type': col[2],  # 数据类型
                    'not_null': bool(col[3]),  # 是否非空
                    'default_value': col[4],  # 默认值
                    'primary_key': bool(col[5])  # 是否为主键
                }
                table_info['columns'].append(column_info)
            
            # 处理索引信息
            for idx in indexes:
                index_info = {
                    'name': idx[1],  # 索引名
                    'unique': bool(idx[2]),  # 是否唯一
                    'seq': idx[0]  # 序号
                }
                
                # 获取索引的列信息
                cursor.execute(f"PRAGMA index_info('{idx[1]}');")
                index_columns = cursor.fetchall()
                
                index_info['columns'] = [col[2] for col in index_columns]
                table_info['indexes'].append(index_info)
            
            # 处理外键信息
            for fk in foreign_keys:
                foreign_key_info = {
                    'id': fk[0],  # 外键ID
                    'column': fk[3],  # 本表列名
                    'ref_table': fk[2],  # 引用表名
                    'ref_column': fk[4]  # 引用列名
                }
                table_info['foreign_keys'].append(foreign_key_info)
            
            schema_info[table_name] = table_info
        
        conn.close()
        
        # 生成洞察信息
        table_names = list(schema_info.keys())
        total_tables = len(table_names)
        total_columns = sum(len(table_info['columns']) for table_info in schema_info.values())
        
        insights = [
            f"数据库中共有 {total_tables} 个表",
            f"数据库中共有 {total_columns} 个列",
            f"表名: {', '.join(table_names)}"
        ]
        
        facts = [
            ['database', 'has_table_count', str(total_tables)],
            ['database', 'has_column_count', str(total_columns)]
        ]
        
        for table_name, table_info in schema_info.items():
            facts.append(['table', 'exists_in_database', table_name])
            facts.append([table_name, 'has_column_count', str(len(table_info['columns']))])
        
        return {
            'result': schema_info,
            'insights': insights,
            'facts': facts,
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f"分析了数据库表结构，包含 {total_tables} 个表",
                    'importance': 0.8,
                    'tags': ['database', 'schema', 'analysis']
                }
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'分析数据库表结构时发生错误: {str(e)}'],
            'facts': [],
            'memories': []
        }