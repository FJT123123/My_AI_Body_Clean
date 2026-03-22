"""
自动生成的技能模块
需求: 分析SQLite数据库结构，检查现有索引，并为性能优化建议和创建新的索引
生成时间: 2026-03-21 20:02:42
"""

# skill_name: sqlite_index_analyzer
import sqlite3
import os
import json
from typing import Dict, List, Any

def main(args=None):
    """
    分析SQLite数据库结构，检查现有索引，并为性能优化建议和创建新的索引
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = args.get('db_path', context.get('db_path', ''))
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库路径不存在或不可访问'},
            'insights': ['无法访问数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        tables_result = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall()
        table_names = [row[0] for row in tables_result]
        
        # 获取所有索引信息
        indexes_result = cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';").fetchall()
        
        # 分析每个表的结构
        table_details = {}
        for table_name in table_names:
            # 获取表的列信息
            columns_info = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
            columns = []
            for col in columns_info:
                columns.append({
                    'cid': col[0],
                    'name': col[1],
                    'type': col[2],
                    'notnull': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                })
            
            # 获取表的索引信息
            table_indexes = [idx for idx in indexes_result if idx[1] == table_name]
            
            table_details[table_name] = {
                'columns': columns,
                'indexes': [{'name': idx[0], 'sql': idx[2]} for idx in table_indexes]
            }
        
        # 获取表的行数信息
        table_row_counts = {}
        for table_name in table_names:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
                table_row_counts[table_name] = count
            except:
                table_row_counts[table_name] = 0
        
        # 分析索引性能
        index_analysis = []
        for idx in indexes_result:
            index_name = idx[0]
            table_name = idx[1]
            index_sql = idx[2]
            
            # 分析索引是否有效
            index_info = cursor.execute(f"PRAGMA index_info({index_name});").fetchall()
            indexed_columns = [info[2] for info in index_info]
            
            index_analysis.append({
                'name': index_name,
                'table': table_name,
                'columns': indexed_columns,
                'sql': index_sql,
                'is_unique': 'UNIQUE' in (index_sql or '').upper()
            })
        
        # 识别可能需要索引的列
        potential_indexes = []
        for table_name in table_names:
            columns = table_details[table_name]['columns']
            for col in columns:
                # 检查列是否已有索引
                has_index = any(col['name'] in idx['columns'] for idx in index_analysis if idx['table'] == table_name)
                
                # 如果是主键或已有索引，跳过
                if col['primary_key'] or has_index:
                    continue
                
                # 检查是否是外键或经常用于查询的列类型
                if col['type'].upper() in ['TEXT', 'INTEGER', 'REAL']:
                    potential_indexes.append({
                        'table': table_name,
                        'column': col['name'],
                        'type': col['type'],
                        'suggestion': f"CREATE INDEX idx_{table_name}_{col['name']} ON {table_name}({col['name']});"
                    })
        
        # 统计信息
        stats = {
            'total_tables': len(table_names),
            'total_indexes': len(indexes_result),
            'total_rows': sum(table_row_counts.values()),
            'table_row_counts': table_row_counts
        }
        
        # 总结分析结果
        insights = [
            f"数据库中共有 {len(table_names)} 个表",
            f"数据库中共有 {len(indexes_result)} 个索引",
            f"数据库总行数: {sum(table_row_counts.values())}",
            f"建议为 {len(potential_indexes)} 个列创建索引以优化性能"
        ]
        
        # 准备返回结果
        result = {
            'database_path': db_path,
            'stats': stats,
            'tables': table_details,
            'indexes': index_analysis,
            'potential_indexes': potential_indexes[:10],  # 限制返回前10个建议
            'recommendations': [idx['suggestion'] for idx in potential_indexes[:10]]
        }
        
        conn.close()
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                ['database', 'has_table_count', str(len(table_names))],
                ['database', 'has_index_count', str(len(indexes_result))],
                ['database', 'total_row_count', str(sum(table_row_counts.values()))]
            ],
            'memories': [
                f"分析了数据库 {db_path}，发现 {len(table_names)} 个表，{len(indexes_result)} 个索引"
            ],
            'next_skills': ['sqlite_index_optimizer'] if potential_indexes else []
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'数据库分析失败: {str(e)}'],
            'facts': [],
            'memories': [f"数据库分析失败: {str(e)}"]
        }