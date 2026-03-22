"""
自动生成的技能模块
需求: 检查SQLite数据库的表结构和索引，分析性能瓶颈并建议优化
生成时间: 2026-03-21 20:01:25
"""

# skill_name: sqlite_database_analyzer
import sqlite3
import os
import time
from typing import Dict, List, Any

def main(args=None) -> Dict[str, Any]:
    """
    分析SQLite数据库的表结构和索引，识别性能瓶颈并提供优化建议
    
    Args:
        args: 包含数据库路径的参数字典
              args['__context__']['db_path'] - SQLite数据库文件路径
              
    Returns:
        dict: 包含表结构分析、索引分析、性能建议和优化方案的详细报告
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或文件不存在'},
            'insights': ['无法访问数据库文件'],
            'facts': [('db_path', '存在性检查', '失败')],
            'memories': []
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        tables = cursor.execute(tables_query).fetchall()
        
        tables_info = {}
        indexes_info = {}
        
        # 分析每个表的结构
        for table in tables:
            table_name = table[0]
            
            # 获取表结构信息
            table_info = cursor.execute(f"PRAGMA table_info('{table_name}')").fetchall()
            tables_info[table_name] = {
                'columns': [{'name': col[1], 'type': col[2], 'not_null': bool(col[3]), 'default': col[4], 'primary_key': bool(col[5])} for col in table_info]
            }
            
            # 获取表的索引信息
            indexes = cursor.execute(f"PRAGMA index_list('{table_name}')").fetchall()
            table_indexes = []
            for idx in indexes:
                idx_name = idx[1]
                # 获取索引详情
                index_info = cursor.execute(f"PRAGMA index_info('{idx_name}')").fetchall()
                table_indexes.append({
                    'name': idx_name,
                    'unique': bool(idx[2]),
                    'columns': [info[2] for info in index_info]
                })
            indexes_info[table_name] = table_indexes
        
        # 获取数据库统计信息
        stats = {}
        for table_name in tables_info:
            # 获取行数
            row_count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            stats[table_name] = {'row_count': row_count}
        
        # 获取所有索引
        all_indexes = cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%';").fetchall()
        all_indexes = [idx[0] for idx in all_indexes]
        
        # 分析性能瓶颈
        performance_analysis = analyze_performance_bottlenecks(conn, tables_info, indexes_info)
        
        # 生成优化建议
        optimization_suggestions = generate_optimization_suggestions(tables_info, indexes_info, performance_analysis)
        
        conn.close()
        
        result = {
            'database_path': db_path,
            'tables': tables_info,
            'indexes': indexes_info,
            'stats': stats,
            'performance_analysis': performance_analysis,
            'optimization_suggestions': optimization_suggestions
        }
        
        insights = [
            f"分析了数据库: {db_path}",
            f"发现 {len(tables_info)} 个表",
            f"发现 {len(all_indexes)} 个索引"
        ]
        
        # 如果有性能建议，添加到insights
        for suggestion in optimization_suggestions:
            insights.append(suggestion['summary'])
        
        facts = [
            ('database_path', '存在', db_path),
            ('table_count', '总计', len(tables_info)),
            ('index_count', '总计', len(all_indexes))
        ]
        
        for table_name, info in tables_info.items():
            facts.append((table_name, 'column_count', len(info['columns'])))
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': [
                f"数据库分析完成: {db_path}",
                f"表结构: {list(tables_info.keys())}",
                f"优化建议: {[s['summary'] for s in optimization_suggestions]}"
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'数据库分析失败: {str(e)}'],
            'facts': [('db_analysis', 'status', 'failed')],
            'memories': [f'数据库分析失败: {str(e)}']
        }

def analyze_performance_bottlenecks(conn, tables_info, indexes_info):
    """分析性能瓶颈"""
    analysis = []
    
    cursor = conn.cursor()
    
    # 检查是否有未使用索引的表
    for table_name, indexes in indexes_info.items():
        if not indexes:
            analysis.append({
                'type': 'missing_index',
                'table': table_name,
                'severity': 'high',
                'description': f'表 {table_name} 没有索引，可能影响查询性能'
            })
        
        # 检查是否有重复索引
        index_columns = [idx['columns'] for idx in indexes]
        for idx in indexes:
            if index_columns.count(idx['columns']) > 1:
                analysis.append({
                    'type': 'duplicate_index',
                    'table': table_name,
                    'severity': 'medium',
                    'description': f'表 {table_name} 存在重复索引: {idx["name"]}'
                })
    
    # 检查是否有大表（行数超过100,000）
    for table_name in tables_info:
        row_count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        if row_count > 100000:
            analysis.append({
                'type': 'large_table',
                'table': table_name,
                'severity': 'medium',
                'description': f'表 {table_name} 包含 {row_count} 行数据，可能需要优化索引'
            })
    
    return analysis

def generate_optimization_suggestions(tables_info, indexes_info, performance_analysis):
    """生成优化建议"""
    suggestions = []
    
    # 根据性能分析生成建议
    for issue in performance_analysis:
        if issue['type'] == 'missing_index':
            suggestions.append({
                'type': 'index_creation',
                'table': issue['table'],
                'summary': f'为表 {issue["table"]} 建议创建索引',
                'details': f'由于表 {issue["table"]} 没有索引，建议为其主键或常用查询字段创建索引以提高查询性能'
            })
        elif issue['type'] == 'duplicate_index':
            suggestions.append({
                'type': 'index_cleanup',
                'table': issue['table'],
                'summary': f'清理表 {issue["table"]} 的重复索引',
                'details': f'检测到表 {issue["table"]} 存在重复索引，建议删除重复的索引以节省存储空间'
            })
        elif issue['type'] == 'large_table':
            suggestions.append({
                'type': 'large_table_optimization',
                'table': issue['table'],
                'summary': f'优化大表 {issue["table"]} 的索引',
                'details': f'表 {issue["table"]} 包含大量数据，建议检查并优化查询索引'
            })
    
    # 检查是否有单列主键的表，建议添加索引
    for table_name, info in tables_info.items():
        has_primary_key = any(col['primary_key'] for col in info['columns'])
        has_index = len(indexes_info.get(table_name, [])) > 0
        if not has_index and has_primary_key:
            suggestions.append({
                'type': 'index_recommendation',
                'table': table_name,
                'summary': f'为表 {table_name} 的主键创建索引',
                'details': f'表 {table_name} 有主键但没有索引，建议为常用查询字段创建索引'
            })
    
    # 检查是否有自增主键
    for table_name, info in tables_info.items():
        auto_increment_cols = [col for col in info['columns'] if col['type'].upper() == 'INTEGER' and col['primary_key']]
        if auto_increment_cols:
            suggestions.append({
                'type': 'primary_key_optimization',
                'table': table_name,
                'summary': f'表 {table_name} 使用整数主键，性能良好',
                'details': f'表 {table_name} 的主键 {auto_increment_cols[0]["name"]} 是整数类型，这通常有良好的性能'
            })
    
    return suggestions