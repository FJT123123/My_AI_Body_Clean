"""
自动生成的技能模块
需求: 动态数据库结构发现与验证系统：自动检测SQLite数据库的实际表结构，包括列名、数据类型、索引等，并提供结构验证功能，能够适应真实的数据库结构而不是假设固定的结构
生成时间: 2026-03-22 07:29:37
"""

# skill_name: sqlite_dynamic_schema_discoverer

import sqlite3
import os
import json
from typing import Dict, List, Any

def main(args=None):
    """
    动态数据库结构发现与验证系统：自动检测SQLite数据库的实际表结构，包括列名、数据类型、索引等，并提供结构验证功能，能够适应真实的数据库结构而不是假设固定的结构
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径是否存在
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用或数据库文件不存在'},
            'insights': ['无法访问数据库文件'],
            'facts': [],
            'memories': []
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        schema_info = {}
        
        # 获取每张表的详细信息
        for table_name in table_names:
            table_info = {}
            
            # 获取表的列信息
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_info = []
            for col in columns:
                column_info.append({
                    'id': col[0],
                    'name': col[1],
                    'type': col[2],
                    'not_null': bool(col[3]),
                    'default_value': col[4],
                    'primary_key': bool(col[5])
                })
            table_info['columns'] = column_info
            
            # 获取表的索引信息
            cursor.execute(f"PRAGMA index_list({table_name});")
            indexes = cursor.fetchall()
            index_info = []
            for idx in indexes:
                index_name = idx[1]
                cursor.execute(f"PRAGMA index_info({index_name});")
                index_cols = cursor.fetchall()
                index_info.append({
                    'name': index_name,
                    'unique': bool(idx[2]),
                    'columns': [col[2] for col in index_cols]
                })
            table_info['indexes'] = index_info
            
            # 获取表的外键信息
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            fk_info = []
            for fk in foreign_keys:
                fk_info.append({
                    'id': fk[0],
                    'seq': fk[1],
                    'table': fk[2],
                    'from': fk[3],
                    'to': fk[4],
                    'on_update': fk[5],
                    'on_delete': fk[6],
                    'match': fk[7]
                })
            table_info['foreign_keys'] = fk_info
            
            schema_info[table_name] = table_info
        
        # 获取数据库的其他信息
        # 获取所有索引（不仅仅是表的索引）
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index';")
        all_indexes = cursor.fetchall()
        database_indexes = []
        for idx in all_indexes:
            database_indexes.append({
                'name': idx[0],
                'table': idx[1],
                'definition': idx[2]
            })
        
        # 获取触发器信息
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger';")
        triggers = cursor.fetchall()
        trigger_info = []
        for trigger in triggers:
            trigger_info.append({
                'name': trigger[0],
                'table': trigger[1],
                'definition': trigger[2]
            })
        
        # 获取视图信息
        cursor.execute("SELECT name, tbl_name, sql FROM sqlite_master WHERE type='view';")
        views = cursor.fetchall()
        view_info = []
        for view in views:
            view_info.append({
                'name': view[0],
                'table': view[1],
                'definition': view[2]
            })
        
        # 关闭数据库连接
        conn.close()
        
        # 构建返回结果
        result = {
            'database_path': db_path,
            'tables': schema_info,
            'table_names': table_names,
            'database_indexes': database_indexes,
            'triggers': trigger_info,
            'views': view_info,
            'total_tables': len(table_names),
            'total_indexes': len(database_indexes),
            'total_triggers': len(trigger_info),
            'total_views': len(view_info)
        }
        
        # 生成洞察
        insights = [
            f"发现数据库包含 {len(table_names)} 个表",
            f"数据库中包含 {len(database_indexes)} 个索引",
            f"数据库中包含 {len(trigger_info)} 个触发器",
            f"数据库中包含 {len(view_info)} 个视图"
        ]
        
        # 生成事实三元组
        facts = [
            ["database", "has_path", db_path],
            ["database", "has_table_count", str(len(table_names))],
            ["database", "has_index_count", str(len(database_indexes))],
            ["database", "has_trigger_count", str(len(trigger_info))],
            ["database", "has_view_count", str(len(view_info))]
        ]
        
        for table_name in table_names:
            facts.append(["database", "contains_table", table_name])
            table_info = schema_info[table_name]
            facts.append([table_name, "has_column_count", str(len(table_info['columns']))])
            facts.append([table_name, "has_index_count", str(len(table_info['indexes']))])
        
        # 生成记忆记录
        memories = [
            {
                "event_type": "skill_executed",
                "content": f"数据库结构发现完成，共发现 {len(table_names)} 个表",
                "tags": ["schema", "database"]
            }
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': memories,
            'capabilities': ['database_schema_analysis']
        }
        
    except Exception as e:
        return {
            'result': {'error': f'数据库分析失败: {str(e)}'},
            'insights': ['数据库分析过程中发生错误'],
            'facts': [],
            'memories': [
                {
                    "event_type": "skill_executed",
                    "content": f"数据库结构发现失败: {str(e)}",
                    "tags": ["schema", "database", "error"]
                }
            ]
        }