"""
自动生成的技能模块
需求: 检查SQLite数据库中memory_chunks表的结构
生成时间: 2026-03-22 04:08:59
"""

# skill_name: sqlite_memory_chunks_schema_inspector

def main(args=None):
    """
    检查SQLite数据库中memory_chunks表的结构信息
    """
    import sqlite3
    import os
    
    args = args or {}
    context = args.get('__context__', {})
    db_path = args.get('db', context.get('db_path', ''))
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库文件路径不存在'},
            'insights': ['无法访问指定的数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='memory_chunks'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return {
                'result': {'error': 'memory_chunks表不存在'},
                'insights': ['数据库中未找到memory_chunks表'],
                'facts': [
                    ['database', 'contains_table', 'memory_chunks'],
                    ['memory_chunks_table', 'existence', 'false']
                ],
                'memories': []
            }
        
        # 获取表结构信息
        cursor.execute("PRAGMA table_info(memory_chunks)")
        columns_info = cursor.fetchall()
        
        # 获取表的索引信息
        cursor.execute("PRAGMA index_list(memory_chunks)")
        indexes_info = cursor.fetchall()
        
        # 获取表的统计信息
        cursor.execute("SELECT COUNT(*) FROM memory_chunks")
        row_count = cursor.fetchone()[0]
        
        # 构建列信息
        columns = []
        for col in columns_info:
            col_dict = {
                'id': col[0],
                'name': col[1],
                'type': col[2],
                'not_null': bool(col[3]),
                'default_value': col[4],
                'primary_key': bool(col[5])
            }
            columns.append(col_dict)
        
        # 构建索引信息
        indexes = []
        for idx in indexes_info:
            index_dict = {
                'id': idx[0],
                'name': idx[1],
                'unique': bool(idx[2]),
                'origin': idx[3],
                'partial': idx[4]
            }
            indexes.append(index_dict)
        
        schema_info = {
            'table_name': 'memory_chunks',
            'exists': True,
            'columns': columns,
            'indexes': indexes,
            'row_count': row_count
        }
        
        conn.close()
        
        # 准备洞察信息
        insights = [
            f"memory_chunks表包含{len(columns)}个列",
            f"表中现有{row_count}条记录",
            f"共有{len(indexes)}个索引"
        ]
        
        # 准备事实三元组
        facts = [
            ['memory_chunks_table', 'row_count', str(row_count)],
            ['memory_chunks_table', 'column_count', str(len(columns))],
            ['memory_chunks_table', 'index_count', str(len(indexes))]
        ]
        
        for col in columns:
            facts.append(['memory_chunks_table', 'has_column', col['name']])
            facts.append([col['name'], 'data_type', col['type']])
        
        return {
            'result': schema_info,
            'insights': insights,
            'facts': facts,
            'memories': []
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['访问数据库时发生错误'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': ['执行检查时发生未知错误'],
            'facts': [],
            'memories': []
        }