"""
自动生成的技能模块
需求: 检查SQLite数据库中指定表的结构，包括列信息和索引。接受db_path和table_name参数，返回表的详细结构信息。
生成时间: 2026-03-22 04:13:23
"""

# skill_name: sqlite_table_structure_analyzer

def main(args=None):
    """
    检查SQLite数据库中指定表的结构，包括列信息和索引
    参数：
    - db_path: SQLite数据库文件路径
    - table_name: 要分析的表名
    返回：表的详细结构信息，包括列定义和索引信息
    """
    import sqlite3
    import os
    
    if args is None:
        args = {}
    
    db_path = args.get('db_path', '')
    table_name = args.get('table_name', '')
    
    # 验证输入参数
    if not db_path:
        return {
            'result': {'error': 'db_path 参数缺失'},
            'insights': ['缺少数据库路径参数'],
            'facts': [],
            'memories': []
        }
    
    if not table_name:
        return {
            'result': {'error': 'table_name 参数缺失'},
            'insights': ['缺少表名参数'],
            'facts': [],
            'memories': []
        }
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        return {
            'result': {'error': f'数据库文件不存在: {db_path}'},
            'insights': [f'指定的数据库文件不存在: {db_path}'],
            'facts': [],
            'memories': []
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表的列信息
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns_info = cursor.fetchall()
        
        # 获取表的索引信息
        cursor.execute(f"PRAGMA index_list('{table_name}')")
        indexes_info = cursor.fetchall()
        
        # 获取每个索引的详细信息
        detailed_indexes = []
        for index in indexes_info:
            index_name = index[1]
            cursor.execute(f"PRAGMA index_info('{index_name}')")
            index_details = cursor.fetchall()
            detailed_indexes.append({
                'index_name': index_name,
                'index_details': index_details,
                'is_unique': index[2]  # unique flag
            })
        
        # 构建列信息列表
        columns = []
        for col in columns_info:
            column_info = {
                'cid': col[0],  # column id
                'name': col[1],  # column name
                'type': col[2],  # data type
                'not_null': bool(col[3]),  # not null constraint
                'default_value': col[4],  # default value
                'primary_key': bool(col[5])  # primary key flag
            }
            columns.append(column_info)
        
        # 获取表的创建语句
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        create_statement = cursor.fetchone()
        create_sql = create_statement[0] if create_statement else None
        
        # 获取表的行数
        cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
        row_count = cursor.fetchone()[0]
        
        # 关闭连接
        conn.close()
        
        # 构建结果
        result = {
            'table_name': table_name,
            'row_count': row_count,
            'create_sql': create_sql,
            'columns': columns,
            'indexes': detailed_indexes
        }
        
        insights = [
            f"成功分析表 {table_name} 的结构",
            f"表包含 {len(columns)} 个列",
            f"表包含 {len(indexes_info)} 个索引",
            f"表当前有 {row_count} 行数据"
        ]
        
        facts = [
            ['table', 'name', table_name],
            ['table', 'row_count', str(row_count)],
            ['table', 'column_count', str(len(columns))]
        ]
        
        for col in columns:
            facts.append([table_name, f'column_{col["name"]}_type', col['type']])
            if col['primary_key']:
                facts.append([table_name, f'column_{col["name"]}_primary_key', 'true'])
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': []
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': [f'数据库操作失败: {str(e)}'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': [f'分析表结构时发生未知错误: {str(e)}'],
            'facts': [],
            'memories': []
        }