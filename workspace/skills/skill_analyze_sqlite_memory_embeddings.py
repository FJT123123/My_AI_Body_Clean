"""
自动生成的技能模块
需求: 检查SQLite数据库中的记忆嵌入表结构，返回表的列信息和索引信息
生成时间: 2026-03-22 03:52:58
"""

# skill_name: analyze_sqlite_memory_embeddings
import sqlite3
import os
import json

def main(args=None):
    """
    检查SQLite数据库中的记忆嵌入表结构，返回表的列信息和索引信息
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库文件']
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = cursor.execute(tables_query).fetchall()
        table_names = [table[0] for table in tables]
        
        # 检查可能的嵌入相关表
        embedding_tables = []
        for table_name in table_names:
            if 'embedding' in table_name.lower() or 'embeddings' in table_name.lower():
                embedding_tables.append(table_name)
        
        # 如果没有找到嵌入相关表，查找可能的嵌入列
        if not embedding_tables:
            for table_name in table_names:
                columns_query = f"PRAGMA table_info({table_name});"
                columns = cursor.execute(columns_query).fetchall()
                for col in columns:
                    if 'embedding' in col[1].lower():
                        embedding_tables.append(table_name)
                        break
        
        # 获取表结构信息
        table_info = {}
        for table_name in embedding_tables:
            # 获取列信息
            columns_query = f"PRAGMA table_info({table_name});"
            columns = cursor.execute(columns_query).fetchall()
            
            # 获取索引信息
            indexes_query = f"PRAGMA index_list({table_name});"
            indexes = cursor.execute(indexes_query).fetchall()
            
            # 获取每个索引的详细信息
            index_details = {}
            for idx in indexes:
                index_name = idx[1]
                index_info_query = f"PRAGMA index_info({index_name});"
                index_cols = cursor.execute(index_info_query).fetchall()
                index_details[index_name] = {
                    'columns': [col[2] for col in index_cols],
                    'unique': bool(idx[2])
                }
            
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
                ],
                'indexes': index_details
            }
        
        # 获取数据库的总体信息
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
        total_tables = cursor.fetchone()[0]
        
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='index';")
        total_indexes = cursor.fetchone()[0]
        
        # 获取完整表结构
        all_table_info = {}
        for table_name in table_names:
            columns_query = f"PRAGMA table_info({table_name});"
            columns = cursor.execute(columns_query).fetchall()
            
            indexes_query = f"PRAGMA index_list({table_name});"
            indexes = cursor.execute(indexes_query).fetchall()
            
            # 获取每个索引的详细信息
            index_details = {}
            for idx in indexes:
                index_name = idx[1]
                try:
                    index_info_query = f"PRAGMA index_info({index_name});"
                    index_cols = cursor.execute(index_info_query).fetchall()
                    index_details[index_name] = {
                        'columns': [col[2] for col in index_cols],
                        'unique': bool(idx[2])
                    }
                except:
                    # 处理无法获取索引信息的情况
                    index_details[index_name] = {'columns': [], 'unique': bool(idx[2])}
            
            all_table_info[table_name] = {
                'columns': [
                    {
                        'id': col[0],
                        'name': col[1],
                        'type': col[2],
                        'not_null': bool(col[3]),
                        'default_value': col[4],
                        'primary_key': bool(col[5])
                    } for col in columns
                ],
                'indexes': index_details
            }
        
        conn.close()
        
        # 构建返回结果
        result = {
            'database_path': db_path,
            'total_tables': total_tables,
            'total_indexes': total_indexes,
            'embedding_tables': embedding_tables,
            'embedding_table_info': table_info,
            'all_table_info': all_table_info
        }
        
        insights = []
        if embedding_tables:
            insights.append(f"发现 {len(embedding_tables)} 个嵌入相关表: {embedding_tables}")
        else:
            insights.append("未发现嵌入相关表")
        
        insights.append(f"数据库中共有 {total_tables} 个表和 {total_indexes} 个索引")
        
        return {
            'result': result,
            'insights': insights,
            'facts': [
                ['database', 'has_path', db_path],
                ['database', 'total_tables', str(total_tables)],
                ['database', 'total_indexes', str(total_indexes)]
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': ['数据库分析过程中发生错误']
        }