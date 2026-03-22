"""
自动生成的技能模块
需求: 列出SQLite数据库中的所有表名
生成时间: 2026-03-22 04:27:56
"""

# skill_name: list_sqlite_tables
import sqlite3
import os

def main(args=None):
    """
    列出SQLite数据库中的所有表名
    参数: args['__context__']['db_path'] - SQLite数据库文件路径
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': '数据库路径不可用'},
            'insights': ['无法访问数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        table_names = [table[0] for table in tables]
        
        conn.close()
        
        return {
            'result': {'table_names': table_names, 'count': len(table_names)},
            'insights': [f'数据库中找到 {len(table_names)} 个表'],
            'facts': [('database', 'has_table_count', str(len(table_names)))],
            'memories': [f'在数据库 {db_path} 中发现表: {", ".join(table_names)}']
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库连接或查询失败'],
            'facts': [],
            'memories': [f'尝试列出数据库 {db_path} 表时发生错误: {str(e)}']
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': ['执行过程中发生未知错误'],
            'facts': [],
            'memories': [f'尝试列出数据库 {db_path} 表时发生未知错误: {str(e)}']
        }