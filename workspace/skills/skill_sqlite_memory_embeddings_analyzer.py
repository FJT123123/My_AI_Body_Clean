"""
自动生成的技能模块
需求: 查询SQLite数据库中memory_embeddings表的详细结构，包括所有列名、数据类型和约束条件
生成时间: 2026-03-22 02:55:31
"""

# skill_name: sqlite_memory_embeddings_analyzer

import sqlite3
import os

def main(args=None):
    """
    查询SQLite数据库中memory_embeddings表的详细结构，包括所有列名、数据类型和约束条件
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或文件不存在'},
            'insights': ['无法访问数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 检查表是否存在
        table_exists_query = """
        SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings';
        """
        table_result = conn.execute(table_exists_query).fetchone()
        
        if not table_result:
            conn.close()
            return {
                'result': {'error': 'memory_embeddings表不存在'},
                'insights': ['数据库中未找到memory_embeddings表'],
                'facts': [('memory_embeddings表', '存在状态', '不存在')],
                'memories': []
            }
        
        # 获取表结构信息
        pragma_query = "PRAGMA table_info(memory_embeddings);"
        columns_info = conn.execute(pragma_query).fetchall()
        
        # 获取表的创建SQL语句
        create_sql_query = "SELECT sql FROM sqlite_master WHERE type='table' AND name='memory_embeddings';"
        create_sql_result = conn.execute(create_sql_query).fetchone()
        create_sql = create_sql_result[0] if create_sql_result else None
        
        # 获取索引信息
        indexes_query = "SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='memory_embeddings';"
        indexes_info = conn.execute(indexes_query).fetchall()
        
        conn.close()
        
        # 解析列信息
        columns_details = []
        for col in columns_info:
            cid, name, data_type, not_null, default_value, pk = col
            column_detail = {
                'cid': cid,
                'name': name,
                'type': data_type,
                'not_null': bool(not_null),
                'default_value': default_value,
                'primary_key': bool(pk)
            }
            columns_details.append(column_detail)
        
        # 解析约束信息
        constraints = []
        if create_sql:
            # 提取外键约束
            import re
            foreign_key_matches = re.findall(r'FOREIGN KEY\s*\(([^)]+)\)\s*REFERENCES\s+([^\(]+)\s*\(([^)]+)\)', create_sql, re.IGNORECASE)
            for match in foreign_key_matches:
                constraints.append({
                    'type': 'FOREIGN KEY',
                    'source_column': match[0].strip(),
                    'referenced_table': match[1].strip(),
                    'referenced_column': match[2].strip()
                })
            
            # 提取唯一约束
            unique_matches = re.findall(r'UNIQUE\s*\(([^)]+)\)', create_sql, re.IGNORECASE)
            for match in unique_matches:
                constraints.append({
                    'type': 'UNIQUE',
                    'columns': [col.strip() for col in match.split(',')]
                })
        
        result_data = {
            'table_exists': True,
            'columns': columns_details,
            'create_sql': create_sql,
            'indexes': [{'name': idx[0], 'sql': idx[1]} for idx in indexes_info],
            'constraints': constraints
        }
        
        insights = [
            f"memory_embeddings表包含{len(columns_details)}个列",
            f"发现{len(indexes_info)}个索引",
            f"发现{len(constraints)}个约束条件"
        ]
        
        facts = [
            ('memory_embeddings表', '列数量', str(len(columns_details))),
            ('memory_embeddings表', '索引数量', str(len(indexes_info))),
            ('memory_embeddings表', '约束数量', str(len(constraints)))
        ]
        
        memories = [f"分析了memory_embeddings表结构，包含{len(columns_details)}个列"]
        
        return {
            'result': result_data,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'SQLite错误: {str(e)}'},
            'insights': ['数据库连接或查询过程中发生错误'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': ['执行过程中发生未知错误'],
            'facts': [],
            'memories': []
        }