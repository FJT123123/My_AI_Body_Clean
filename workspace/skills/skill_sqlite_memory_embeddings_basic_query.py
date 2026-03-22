"""
自动生成的技能模块
需求: 测试连接到workspace/v3_episodic_memory.db并查询memory_embeddings表的基本数据
生成时间: 2026-03-22 04:28:28
"""

# skill_name: sqlite_memory_embeddings_basic_query
import sqlite3
import os

def main(args=None):
    """
    测试连接到workspace/v3_episodic_memory.db并查询memory_embeddings表的基本数据
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 如果没有提供db_path，尝试构建默认路径
    if not db_path:
        workspace_dir = os.path.join(os.getcwd(), 'workspace')
        db_path = os.path.join(workspace_dir, 'v3_episodic_memory.db')
    elif os.path.isdir(db_path):
        # 如果传入的是目录，构建完整的数据库路径
        db_path = os.path.join(db_path, 'v3_episodic_memory.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        return {
            'result': {'error': f'数据库文件不存在: {db_path}'},
            'insights': [f'尝试连接的数据库文件不存在: {db_path}'],
            'facts': [('database', 'exists', False)],
            'memories': [f'连接数据库失败: {db_path} 不存在']
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查memory_embeddings表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='memory_embeddings';
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            conn.close()
            return {
                'result': {'error': 'memory_embeddings表不存在'},
                'insights': ['数据库中不存在memory_embeddings表'],
                'facts': [('table', 'memory_embeddings_exists', False)],
                'memories': ['memory_embeddings表不存在于数据库中']
            }
        
        # 查询表结构
        cursor.execute("PRAGMA table_info(memory_embeddings);")
        table_info = cursor.fetchall()
        
        # 查询表中记录数
        cursor.execute("SELECT COUNT(*) FROM memory_embeddings;")
        record_count = cursor.fetchone()[0]
        
        # 如果有记录，获取前几条记录
        sample_records = []
        if record_count > 0:
            cursor.execute("SELECT * FROM memory_embeddings LIMIT 5;")
            sample_records = cursor.fetchall()
        
        conn.close()
        
        return {
            'result': {
                'database_path': db_path,
                'table_exists': True,
                'record_count': record_count,
                'table_structure': table_info,
                'sample_records': sample_records
            },
            'insights': [
                f'成功连接到数据库: {db_path}',
                f'memory_embeddings表存在，包含{record_count}条记录'
            ],
            'facts': [
                ('database', 'path', db_path),
                ('table', 'memory_embeddings_exists', True),
                ('table', 'record_count', record_count)
            ],
            'memories': [
                f'成功查询memory_embeddings表，共有{record_count}条记录'
            ]
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'数据库错误: {str(e)}'},
            'insights': [f'数据库连接或查询失败: {str(e)}'],
            'facts': [('database', 'connection_status', 'error')],
            'memories': [f'数据库操作失败: {str(e)}']
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': [f'执行过程中发生未知错误: {str(e)}'],
            'facts': [('database', 'execution_status', 'error')],
            'memories': [f'技能执行失败: {str(e)}']
        }