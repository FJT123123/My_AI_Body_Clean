"""
自动生成的技能模块
需求: 连接到v3_episodic_memory.db数据库，检查memory_embeddings表的结构，包括所有列名和数据类型
生成时间: 2026-03-22 04:26:38
"""

# skill_name: sqlite_memory_embeddings_schema_query
import sqlite3
import os

def main(args=None):
    """
    连接到v3_episodic_memory.db数据库，检查memory_embeddings表的结构，包括所有列名和数据类型
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 如果没有提供db_path，尝试使用默认路径
    if not db_path:
        db_path = 'v3_episodic_memory.db'
    
    if not os.path.exists(db_path):
        return {
            'result': {'error': f'数据库文件不存在: {db_path}'},
            'insights': [f'无法找到数据库文件 {db_path}'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查memory_embeddings表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings';")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return {
                'result': {'error': 'memory_embeddings表不存在'},
                'insights': ['数据库中未找到memory_embeddings表'],
                'facts': [],
                'memories': []
            }
        
        # 获取表的结构信息
        cursor.execute("PRAGMA table_info(memory_embeddings);")
        columns_info = cursor.fetchall()
        
        # 格式化列信息
        columns = []
        for col_info in columns_info:
            col_dict = {
                'id': col_info[0],
                'name': col_info[1],
                'type': col_info[2],
                'not_null': bool(col_info[3]),
                'default_value': col_info[4],
                'primary_key': bool(col_info[5])
            }
            columns.append(col_dict)
        
        # 构建表结构信息
        schema_info = {
            'table_name': 'memory_embeddings',
            'columns': columns,
            'total_columns': len(columns)
        }
        
        conn.close()
        
        # 生成洞察
        insights = [f"memory_embeddings表包含{len(columns)}个列"]
        for col in columns:
            null_status = "非空" if col['not_null'] else "可空"
            pk_status = "主键" if col['primary_key'] else ""
            insights.append(f"列 '{col['name']}' 类型: {col['type']}, {null_status} {pk_status}".strip())
        
        return {
            'result': schema_info,
            'insights': insights,
            'facts': [
                ['memory_embeddings', 'has_column_count', str(len(columns))],
                ['memory_embeddings', 'exists_in_database', 'true']
            ],
            'memories': []
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': [f'数据库访问错误: {str(e)}'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': [f'执行过程中发生错误: {str(e)}'],
            'facts': [],
            'memories': []
        }