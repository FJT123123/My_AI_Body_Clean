"""
自动生成的技能模块
需求: 分析SQLite数据库表结构，特别是memory_embeddings表的详细信息，包括列名、数据类型、索引和示例数据
生成时间: 2026-03-24 11:53:18
"""

# skill_name: sqlite_database_schema_analyzer

def main(args=None):
    """
    分析SQLite数据库表结构，特别是memory_embeddings表的详细信息，包括列名、数据类型、索引和示例数据
    """
    import sqlite3
    import json
    import os
    
    args = args or {}
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
        tables = [row[0] for row in cursor.fetchall()]
        
        # 获取数据库整体信息
        schema_info = {}
        for table in tables:
            # 获取表结构信息
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            
            # 获取表的索引信息
            cursor.execute(f"PRAGMA index_list({table});")
            indexes = cursor.fetchall()
            
            # 获取具体的索引信息
            index_details = {}
            for idx in indexes:
                idx_name = idx[1]
                cursor.execute(f"PRAGMA index_info({idx_name});")
                idx_columns = cursor.fetchall()
                index_details[idx_name] = {
                    'columns': [col[2] for col in idx_columns],
                    'unique': bool(idx[2])
                }
            
            # 获取表的行数
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            row_count = cursor.fetchone()[0]
            
            # 获取表的示例数据（前3行）
            cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
            sample_data = cursor.fetchall()
            
            schema_info[table] = {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default': col[4],
                        'primary_key': bool(col[5])
                    } for col in columns
                ],
                'indexes': index_details,
                'row_count': row_count,
                'sample_data': sample_data
            }
        
        # 特别关注memory_embeddings表
        memory_embeddings_info = None
        if 'memory_embeddings' in schema_info:
            memory_embeddings_info = schema_info['memory_embeddings']
        
        conn.close()
        
        # 生成洞察
        insights = []
        insights.append(f"数据库包含 {len(tables)} 个表")
        if 'memory_embeddings' in tables:
            insights.append(f"检测到 memory_embeddings 表，包含 {memory_embeddings_info['row_count']} 行数据")
            insights.append(f"memory_embeddings 表包含 {len(memory_embeddings_info['columns'])} 列")
        
        # 生成事实
        facts = [
            ['database', 'has_table_count', str(len(tables))],
            ['database', 'contains_table', 'memory_embeddings' if 'memory_embeddings' in tables else 'no_embeddings_table']
        ]
        
        if memory_embeddings_info:
            facts.append(['memory_embeddings', 'has_row_count', str(memory_embeddings_info['row_count'])])
            facts.append(['memory_embeddings', 'has_column_count', str(len(memory_embeddings_info['columns']))])
        
        return {
            'result': {
                'schema_info': schema_info,
                'memory_embeddings_info': memory_embeddings_info,
                'tables': tables
            },
            'insights': insights,
            'facts': facts,
            'memories': [
                {
                    'event_type': 'skill_insight',
                    'content': f"分析了数据库结构，发现{len(tables)}个表，其中memory_embeddings表有{memory_embeddings_info['row_count'] if memory_embeddings_info else 0}行数据",
                    'importance': 0.8,
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
                    'event_type': 'skill_insight',
                    'content': f"数据库分析失败: {str(e)}",
                    'importance': 0.5,
                    'tags': ['database', 'error']
                }
            ]
        }
    except Exception as e:
        return {
            'result': {'error': f'分析过程中发生错误: {str(e)}'},
            'insights': ['数据库分析过程中发生未知错误'],
            'facts': [],
            'memories': [
                {
                    'event_type': 'skill_insight',
                    'content': f"数据库分析失败: {str(e)}",
                    'importance': 0.5,
                    'tags': ['database', 'error']
                }
            ]
        }