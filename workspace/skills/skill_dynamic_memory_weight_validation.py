"""
自动生成的技能模块
需求: 创建能够自动发现并适应数据库实际结构的动态验证系统，用于验证动态记忆权重与SQLite索引的协同优化
生成时间: 2026-03-22 07:24:30
"""

# skill_name: dynamic_memory_weight_validation
import sqlite3
import json
import os
from datetime import datetime

def main(args=None):
    """
    创建能够自动发现并适应数据库实际结构的动态验证系统，
    用于验证动态记忆权重与SQLite索引的协同优化
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库'],
            'next_skills': ['skill_create_memory_db']
        }
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取数据库表结构信息
    tables_info = {}
    try:
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            # 获取表的列信息
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # 获取表的索引信息
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()
            
            tables_info[table_name] = {
                'columns': [{'name': col[1], 'type': col[2], 'not_null': col[3], 'default': col[4], 'primary_key': col[5]} for col in columns],
                'indexes': [{'name': idx[1], 'unique': idx[2], 'origin': idx[3]} for idx in indexes]
            }
        
        # 验证memories表的结构
        memories_validation = _validate_memories_table(cursor)
        
        # 分析索引效率
        index_analysis = _analyze_index_usage(cursor, tables_info)
        
        # 检查权重相关字段
        weight_analysis = _analyze_weight_fields(cursor, tables_info)
        
        # 生成验证报告
        validation_report = {
            'database_structure': tables_info,
            'memories_table_validation': memories_validation,
            'index_analysis': index_analysis,
            'weight_fields_analysis': weight_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        conn.close()
        
        # 生成洞察
        insights = _generate_insights(validation_report)
        
        return {
            'result': validation_report,
            'insights': insights,
            'facts': _generate_facts(validation_report),
            'memories': [
                {
                    'event_type': 'skill_insight',
                    'content': f"数据库结构验证完成，发现{len(tables_info)}个表",
                    'importance': 0.8,
                    'timestamp': datetime.now().isoformat(),
                    'tags': ['database', 'validation', 'analysis']
                }
            ]
        }
        
    except Exception as e:
        conn.close()
        return {
            'result': {'error': str(e)},
            'insights': [f'数据库验证过程中发生错误: {str(e)}'],
            'next_skills': ['skill_create_memory_db']
        }

def _validate_memories_table(cursor):
    """验证memories表的结构是否符合预期"""
    try:
        # 检查memories表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories';")
        if not cursor.fetchone():
            return {'exists': False, 'error': 'memories表不存在'}
        
        # 获取列信息
        cursor.execute("PRAGMA table_info(memories);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 检查必需的列
        required_columns = ['id', 'event_type', 'content', 'importance', 'timestamp', 'tags']
        missing_columns = [col for col in required_columns if col not in column_names]
        
        # 检查importance列的统计信息
        if 'importance' in column_names:
            cursor.execute("SELECT MIN(importance), MAX(importance), AVG(importance) FROM memories WHERE importance IS NOT NULL;")
            stats = cursor.fetchone()
            importance_stats = {
                'min': stats[0] if stats[0] is not None else None,
                'max': stats[1] if stats[1] is not None else None,
                'avg': stats[2] if stats[2] is not None else None
            }
        else:
            importance_stats = None
        
        return {
            'exists': True,
            'missing_columns': missing_columns,
            'total_columns': len(column_names),
            'importance_stats': importance_stats,
            'valid': len(missing_columns) == 0
        }
    except Exception as e:
        return {'error': str(e)}

def _analyze_index_usage(cursor, tables_info):
    """分析数据库索引的使用情况"""
    try:
        index_analysis = {}
        
        # 获取所有索引信息
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        
        for index_name, table_name, sql in indexes:
            if sql:  # 跳过自动生成的索引
                # 分析索引的列
                # 简化的SQL解析，提取ON部分和列名
                index_info = {
                    'table': table_name,
                    'sql': sql,
                    'is_used': True  # 索引存在且定义明确
                }
                
                # 检查索引是否在关键查询列上
                if table_name in tables_info:
                    index_columns = _extract_index_columns(sql)
                    key_columns = ['importance', 'timestamp', 'event_type']
                    covering_key_columns = [col for col in index_columns if col in key_columns]
                    
                    index_info['covers_key_columns'] = covering_key_columns
                    index_info['index_columns'] = index_columns
        
        # 检查是否缺少关键索引
        missing_indexes = []
        if 'memories' in tables_info:
            # 检查是否有关于importance和timestamp的索引
            importance_index_exists = any('importance' in idx.get('index_columns', []) for idx in index_analysis.values())
            timestamp_index_exists = any('timestamp' in idx.get('index_columns', []) for idx in index_analysis.values())
            
            if not importance_index_exists:
                missing_indexes.append('importance')
            if not timestamp_index_exists:
                missing_indexes.append('timestamp')
        
        return {
            'total_indexes': len(indexes),
            'index_details': index_analysis,
            'missing_indexes': missing_indexes,
            'recommendations': _generate_index_recommendations(missing_indexes)
        }
    except Exception as e:
        return {'error': str(e)}

def _extract_index_columns(sql):
    """从CREATE INDEX语句中提取列名"""
    import re
    # 简单的正则表达式提取列名
    # 查找 ON table_name (column1, column2) 或 (column1, column2) 的模式
    match = re.search(r'\(([^)]+)\)', sql)
    if match:
        columns_part = match.group(1)
        # 简单分割，去除函数调用等
        columns = [col.strip().split()[0] for col in columns_part.split(',')]
        return [col for col in columns if col and not col.startswith('(')]
    return []

def _analyze_weight_fields(cursor, tables_info):
    """分析权重相关字段的分布和有效性"""
    try:
        weight_analysis = {}
        
        # 检查所有表中的权重相关列
        for table_name, table_info in tables_info.items():
            weight_columns = []
            for col in table_info['columns']:
                col_name = col['name']
                if 'weight' in col_name.lower() or 'importance' in col_name.lower():
                    weight_columns.append(col_name)
            
            if weight_columns:
                table_stats = []
                for col_name in weight_columns:
                    try:
                        # 获取该列的统计信息
                        cursor.execute(f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}), COUNT({col_name}) FROM {table_name} WHERE {col_name} IS NOT NULL;")
                        stats = cursor.fetchone()
                        if stats[0] is not None:  # 确保有数据
                            col_stats = {
                                'column': col_name,
                                'min': stats[0],
                                'max': stats[1],
                                'avg': stats[2],
                                'count': stats[3],
                                'type': col['type']
                            }
                            table_stats.append(col_stats)
                    except:
                        continue  # 如果查询失败，跳过该列
                
                if table_stats:
                    weight_analysis[table_name] = table_stats
        
        # 分析memories表的importance字段
        if 'memories' in tables_info:
            try:
                # 获取importance分布
                cursor.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance ORDER BY importance;")
                importance_dist = cursor.fetchall()
                
                # 获取时间范围
                cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM memories;")
                time_range = cursor.fetchone()
                
                weight_analysis['memories'] = {
                    'importance_distribution': importance_dist,
                    'time_range': time_range,
                    'total_records': len(importance_dist)
                }
            except:
                pass
        
        return weight_analysis
    except Exception as e:
        return {'error': str(e)}

def _generate_index_recommendations(missing_indexes):
    """生成索引建议"""
    recommendations = []
    if 'importance' in missing_indexes:
        recommendations.append("CREATE INDEX idx_memories_importance ON memories(importance);")
    if 'timestamp' in missing_indexes:
        recommendations.append("CREATE INDEX idx_memories_timestamp ON memories(timestamp);")
    if 'event_type' in missing_indexes:
        recommendations.append("CREATE INDEX idx_memories_event_type ON memories(event_type);")
    
    return recommendations

def _generate_insights(analysis_result):
    """生成分析洞察"""
    insights = []
    
    # 数据库结构洞察
    total_tables = len(analysis_result['database_structure'])
    insights.append(f"数据库包含 {total_tables} 个表")
    
    # memories表验证洞察
    mem_validation = analysis_result['memories_table_validation']
    if mem_validation['exists']:
        if mem_validation['valid']:
            insights.append("memories表结构完整，包含所有必需字段")
        else:
            missing_cols = mem_validation['missing_columns']
            insights.append(f"memories表缺少字段: {', '.join(missing_cols)}")
    
    # 索引分析洞察
    index_analysis = analysis_result['index_analysis']
    if index_analysis.get('missing_indexes'):
        missing_idx = index_analysis['missing_indexes']
        insights.append(f"建议创建索引以优化权重和时间相关查询: {', '.join(missing_idx)}")
    else:
        insights.append("现有索引已覆盖关键查询字段")
    
    # 权重分布洞察
    weight_analysis = analysis_result['weight_fields_analysis']
    if 'memories' in weight_analysis and 'importance_distribution' in weight_analysis['memories']:
        importance_dist = weight_analysis['memories']['importance_distribution']
        if len(importance_dist) > 1:
            insights.append(f"importance字段分布良好，有{len(importance_dist)}个不同权重值")
        else:
            insights.append("importance字段分布可能需要优化")
    
    return insights

def _generate_facts(validation_report):
    """生成知识三元组"""
    facts = []
    
    # 数据库基本信息
    facts.append(('database', 'has_tables_count', str(len(validation_report['database_structure']))))
    
    # memories表信息
    mem_validation = validation_report['memories_table_validation']
    if mem_validation['exists']:
        facts.append(('memories_table', 'is_valid', str(mem_validation['valid'])))
        if mem_validation['importance_stats']:
            stats = mem_validation['importance_stats']
            if stats['min'] is not None:
                facts.append(('memories_importance', 'min_value', str(stats['min'])))
                facts.append(('memories_importance', 'max_value', str(stats['max'])))
    
    # 索引信息
    index_analysis = validation_report['index_analysis']
    facts.append(('database', 'has_indexes_count', str(index_analysis['total_indexes'])))
    
    return facts