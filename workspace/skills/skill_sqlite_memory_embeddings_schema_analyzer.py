"""
自动生成的技能模块
需求: 连接到SQLite数据库并查询memory_embeddings表的结构信息，包括列定义和现有索引
生成时间: 2026-03-22 03:53:24
"""

# skill_name: sqlite_memory_embeddings_schema_analyzer

def main(args=None):
    """
    连接到SQLite数据库并查询memory_embeddings表的结构信息，包括列定义和现有索引
    """
    import sqlite3
    import os
    
    # 获取数据库路径
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或数据库文件不存在'},
            'insights': ['无法访问数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查memory_embeddings表是否存在
        cursor.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name='memory_embeddings'
        """)
        
        table_exists = cursor.fetchone()
        
        if not table_exists:
            conn.close()
            return {
                'result': {'error': 'memory_embeddings表不存在'},
                'insights': ['数据库中未找到memory_embeddings表'],
                'facts': [],
                'memories': []
            }
        
        # 获取表结构信息
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns_info = cursor.fetchall()
        
        # 获取表的索引信息
        cursor.execute("PRAGMA index_list(memory_embeddings)")
        indexes_info = cursor.fetchall()
        
        # 获取每个索引的详细信息
        detailed_indexes = []
        for index in indexes_info:
            index_name = index[1]
            cursor.execute(f"PRAGMA index_info('{index_name}')")
            index_columns = cursor.fetchall()
            
            # 获取索引的创建SQL语句
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name = '{index_name}' AND type = 'index'")
            index_sql = cursor.fetchone()
            
            detailed_indexes.append({
                'name': index_name,
                'unique': bool(index[2]),
                'origin': index[3],
                'columns': [col[2] for col in index_columns],
                'sql': index_sql[0] if index_sql else None
            })
        
        # 格式化列信息
        columns = []
        for col in columns_info:
            columns.append({
                'id': col[0],
                'name': col[1],
                'type': col[2],
                'not_null': bool(col[3]),
                'default_value': col[4],
                'primary_key': bool(col[5])
            })
        
        # 获取表的创建SQL语句
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'memory_embeddings' AND type = 'table'")
        table_sql = cursor.fetchone()
        
        conn.close()
        
        # 构建结果
        schema_info = {
            'table_name': 'memory_embeddings',
            'columns': columns,
            'indexes': detailed_indexes,
            'table_sql': table_sql[0] if table_sql else None
        }
        
        insights = [
            f"memory_embeddings表包含{len(columns)}个列",
            f"memory_embeddings表包含{len(detailed_indexes)}个索引"
        ]
        
        facts = [
            ['memory_embeddings', 'has_column_count', str(len(columns))],
            ['memory_embeddings', 'has_index_count', str(len(detailed_indexes))]
        ]
        
        memories = [
            f"分析了memory_embeddings表结构，包含{len(columns)}个列和{len(detailed_indexes)}个索引"
        ]
        
        return {
            'result': schema_info,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库查询过程中发生错误'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'查询过程中的未知错误: {str(e)}'},
            'insights': ['查询memory_embeddings表结构时发生未知错误'],
            'facts': [],
            'memories': []
        }