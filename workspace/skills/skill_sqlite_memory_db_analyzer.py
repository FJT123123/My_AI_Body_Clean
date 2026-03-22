"""
自动生成的技能模块
需求: 分析SQLite数据库结构，包括表结构、索引和查询性能分析，特别关注与记忆权重相关的表和索引
生成时间: 2026-03-21 20:44:16
"""

# skill_name: sqlite_memory_db_analyzer
import sqlite3
import json
import time
from typing import Dict, List, Any

def main(args=None):
    """
    分析SQLite数据库结构，包括表结构、索引和查询性能分析，特别关注与记忆权重相关的表和索引
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', args.get('db_path', ''))
    
    if not db_path or not isinstance(db_path, str):
        return {
            'result': {'error': 'db_path 未提供或格式错误'},
            'insights': ['缺少数据库路径参数'],
            'facts': [],
            'memories': []
        }
    
    if not isinstance(db_path, str) or not db_path.endswith('.db'):
        return {
            'result': {'error': 'db_path 必须是有效的SQLite数据库文件路径'},
            'insights': ['数据库路径格式错误'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = cursor.execute(tables_query).fetchall()
        table_names = [table[0] for table in tables]
        
        # 获取所有索引信息
        indexes_query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';"
        indexes = cursor.execute(indexes_query).fetchall()
        
        # 分析表结构
        table_info = {}
        for table_name in table_names:
            # 获取表结构信息
            table_schema_query = f"PRAGMA table_info('{table_name}');"
            table_schema = cursor.execute(table_schema_query).fetchall()
            
            # 获取表的行数
            row_count_query = f"SELECT COUNT(*) FROM '{table_name}';"
            row_count = cursor.execute(row_count_query).fetchone()[0]
            
            # 获取表的索引
            table_indexes = [idx for idx in indexes if idx[1] == table_name]
            
            table_info[table_name] = {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default_value': col[4],
                        'primary_key': bool(col[5])
                    } for col in table_schema
                ],
                'row_count': row_count,
                'indexes': [idx[0] for idx in table_indexes]
            }
        
        # 分析查询性能 - 检查是否有关于记忆权重的表
        memory_tables = []
        weight_related_tables = []
        for table_name, info in table_info.items():
            if 'memory' in table_name.lower() or 'memories' in table_name.lower():
                memory_tables.append(table_name)
            for col in info['columns']:
                if 'weight' in col['name'].lower() or 'importance' in col['name'].lower():
                    weight_related_tables.append({
                        'table': table_name,
                        'column': col['name']
                    })
        
        # 检查索引是否对内存相关查询进行了优化
        optimized_indexes = []
        for idx in indexes:
            if idx[2] is not None and any(keyword in idx[2].lower() for keyword in ['memory', 'importance', 'weight', 'timestamp', 'event_type']):
                optimized_indexes.append({
                    'name': idx[0],
                    'table': idx[1],
                    'definition': idx[2]
                })
        
        # 性能分析：查看查询执行计划
        performance_analysis = {}
        for table_name in memory_tables:
            if 'timestamp' in [col['name'] for col in table_info[table_name]['columns']]:
                explain_query = f"EXPLAIN QUERY PLAN SELECT * FROM {table_name} ORDER BY timestamp DESC LIMIT 10;"
                try:
                    plan = cursor.execute(explain_query).fetchall()
                    plan_str = ' '.join([str(row) for row in plan])
                    performance_analysis[f'{table_name}_timestamp_query'] = plan_str
                except:
                    performance_analysis[f'{table_name}_timestamp_query'] = '无法生成查询计划'
        
        # 检查是否存在关于重要性(importance)的查询优化
        importance_query_analysis = {}
        for table_name in table_names:
            if any(col['name'].lower() in ['importance', 'weight'] for col in table_info[table_name]['columns']):
                explain_query = f"EXPLAIN QUERY PLAN SELECT * FROM {table_name} ORDER BY importance DESC LIMIT 10;"
                try:
                    plan = cursor.execute(explain_query).fetchall()
                    plan_str = ' '.join([str(row) for row in plan])
                    importance_query_analysis[f'{table_name}_importance_query'] = plan_str
                except:
                    importance_query_analysis[f'{table_name}_importance_query'] = '无法生成查询计划'
        
        # 统计信息
        db_stats = {
            'total_tables': len(table_names),
            'total_indexes': len(indexes),
            'memory_tables': memory_tables,
            'weight_related_tables': weight_related_tables,
            'optimized_indexes': len(optimized_indexes)
        }
        
        conn.close()
        
        result = {
            'database_path': db_path,
            'stats': db_stats,
            'tables': table_info,
            'indexes': [dict(name=idx[0], table=idx[1], definition=idx[2]) for idx in indexes],
            'optimized_indexes': optimized_indexes,
            'performance_analysis': {
                'memory_query_plans': performance_analysis,
                'importance_query_plans': importance_query_analysis
            }
        }
        
        insights = [
            f"数据库包含 {len(table_names)} 个表和 {len(indexes)} 个索引",
            f"发现 {len(memory_tables)} 个与记忆相关的表: {memory_tables}",
            f"发现 {len(weight_related_tables)} 个与权重/重要性相关的列",
            f"存在 {len(optimized_indexes)} 个可能优化的索引"
        ]
        
        facts = [
            ['database', 'has_table_count', str(len(table_names))],
            ['database', 'has_index_count', str(len(indexes))],
            ['database', 'contains_memory_tables', str(len(memory_tables) > 0)],
            ['database', 'contains_importance_columns', str(len(weight_related_tables) > 0)]
        ]
        
        # 生成记忆
        memory_events = [
            f"数据库分析完成: {len(table_names)} 个表, {len(indexes)} 个索引",
            f"记忆相关表: {memory_tables}",
            f"权重相关列: {[item['table']+':'+item['column'] for item in weight_related_tables]}"
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': [{'event_type': 'skill_insight', 'content': event} for event in memory_events],
            'next_skills': [] if len(optimized_indexes) > 0 else ['skill_sqlite_index_optimizer']
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库连接失败'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'分析过程中发生错误: {str(e)}'},
            'insights': ['数据库分析失败'],
            'facts': [],
            'memories': []
        }