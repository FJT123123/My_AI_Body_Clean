"""
自动生成的技能模块
需求: 测试数据库路径是否正确，尝试连接到workspace/v3_episodic_memory.db
生成时间: 2026-03-22 04:31:16
"""

# skill_name: test_database_connection
import os
import sqlite3

def main(args=None):
    """
    测试数据库连接，验证workspace/v3_episodic_memory.db路径是否正确
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = args.get('db_path') or context.get('db_path', '')
    
    # 如果没有提供db_path，尝试使用默认路径
    if not db_path:
        db_path = 'workspace/v3_episodic_memory.db'
    
    result = {
        'db_path': db_path,
        'connection_successful': False,
        'error': None
    }
    
    insights = []
    
    try:
        # 检查文件是否存在
        if not os.path.exists(db_path):
            result['error'] = f"数据库文件不存在: {db_path}"
            insights.append(f"数据库文件不存在: {db_path}")
            return {
                'result': result,
                'insights': insights
            }
        
        # 尝试连接数据库
        conn = sqlite3.connect(db_path)
        
        # 执行一个简单的查询来验证数据库是否可用
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # 获取数据库基本信息
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
        table_count = cursor.fetchone()[0]
        
        # 关闭连接
        conn.close()
        
        result['connection_successful'] = True
        result['table_count'] = table_count
        result['tables'] = [table[0] for table in tables]
        
        insights.append(f"成功连接到数据库: {db_path}")
        insights.append(f"数据库包含 {table_count} 个表")
        
    except Exception as e:
        result['error'] = str(e)
        insights.append(f"数据库连接失败: {str(e)}")
    
    return {
        'result': result,
        'insights': insights
    }