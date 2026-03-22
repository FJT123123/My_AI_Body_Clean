"""
自动生成的技能模块
需求: 连接到SQLite数据库并列出所有表及其结构，特别关注memory_embeddings表是否存在
生成时间: 2026-03-22 04:26:05
"""

# skill_name: sqlite_memory_embeddings_schema_inspector
import sqlite3
import os

def main(args=None):
    """
    连接到SQLite数据库并列出所有表及其结构，特别关注memory_embeddings表是否存在
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_info = {}
        for table in tables:
            table_name = table[0]
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            table_info[table_name] = {
                'columns': [
                    {
                        'id': col[0],
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default_value': col[4],
                        'primary_key': bool(col[5])
                    } for col in columns
                ]
            }
        
        # 检查memory_embeddings表是否存在
        memory_embeddings_exists = 'memory_embeddings' in table_info
        
        # 获取表的创建SQL语句
        create_statements = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
            sql = cursor.fetchone()
            if sql:
                create_statements[table_name] = sql[0]
        
        conn.close()
        
        result = {
            'tables': table_info,
            'create_statements': create_statements,
            'memory_embeddings_exists': memory_embeddings_exists
        }
        
        insights = [f'数据库中共有 {len(tables)} 个表']
        if memory_embeddings_exists:
            insights.append('memory_embeddings表存在')
        else:
            insights.append('memory_embeddings表不存在')
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                ['database', 'has_table_count', str(len(tables))],
                ['database', 'has_memory_embeddings', str(memory_embeddings_exists)]
            ],
            'memories': [
                f"数据库分析结果：{len(tables)}个表，memory_embeddings表{'存在' if memory_embeddings_exists else '不存在'}"
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': ['数据库连接失败'],
            'facts': [],
            'memories': [f"数据库连接失败: {str(e)}"]
        }