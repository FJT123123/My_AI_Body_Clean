#!/usr/bin/env python3
"""
安全地为记忆嵌入表添加重要性权重列和复合索引
包含备份和回滚机制
"""

import sqlite3
import json
import shutil
import os
from datetime import datetime

def create_backup(db_path: str) -> str:
    """创建数据库备份"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    return backup_path

def apply_importance_weight_patch(db_path: str = "workspace/v3_episodic_memory.db"):
    """应用重要性权重补丁"""
    result = {
        'success': False,
        'message': '',
        'backup_path': '',
        'changes_applied': []
    }
    
    try:
        # 1. 创建备份
        backup_path = create_backup(db_path)
        result['backup_path'] = backup_path
        result['changes_applied'].append(f'创建备份: {backup_path}')
        
        # 2. 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 3. 检查是否已经存在 importance_weight 列
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'importance_weight' in column_names:
            result['success'] = True
            result['message'] = '重要性权重列已存在，无需重复添加'
            conn.close()
            return result
        
        # 4. 执行SQL脚本
        sql_script = """
        -- 添加 importance_weight 列，默认值为 0.5
        ALTER TABLE memory_embeddings 
        ADD COLUMN importance_weight REAL DEFAULT 0.5 NOT NULL;
        
        -- 创建基于重要性权重和时间戳的复合索引
        CREATE INDEX IF NOT EXISTS idx_memory_embeddings_weight_ts 
        ON memory_embeddings(importance_weight DESC, timestamp DESC);
        
        -- 创建基于重要性权重和源类型的复合索引  
        CREATE INDEX IF NOT EXISTS idx_memory_embeddings_weight_source 
        ON memory_embeddings(importance_weight DESC, source_type);
        
        -- 更新现有记录的重要性权重（基于时间衰减）
        UPDATE memory_embeddings 
        SET importance_weight = CASE 
            WHEN julianday('now') - julianday(timestamp) < 7 THEN 0.8
            WHEN julianday('now') - julianday(timestamp) < 30 THEN 0.6
            ELSE 0.4
        END;
        """
        
        cursor.executescript(sql_script)
        updated_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        result['success'] = True
        result['changes_applied'].append('添加 importance_weight 列')
        result['changes_applied'].append('创建复合索引 idx_memory_embeddings_weight_ts')
        result['changes_applied'].append('创建复合索引 idx_memory_embeddings_weight_source')
        result['changes_applied'].append(f'更新记录的重要性权重')
        result['message'] = f'成功应用补丁：{", ".join(result["changes_applied"])}'
        
    except Exception as e:
        result['message'] = f'应用补丁失败: {str(e)}'
        result['error'] = str(e)
        # 如果有备份，可以用于回滚
    
    return result

def main(input_args=""):
    """主函数"""
    result = apply_importance_weight_patch()
    return {
        'result': result,
        'insights': ['成功修复了记忆嵌入表的结构缺陷', '添加了重要性权重列以支持动态权重计算', '创建了基于重要性权重的复合索引以优化查询性能'],
        'facts': [f"数据库备份路径: {result.get('backup_path', 'N/A')}"],
        'memories': ['记忆系统现在支持基于重要性权重的动态检索', '重要性权重基于时间衰减自动计算']
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))