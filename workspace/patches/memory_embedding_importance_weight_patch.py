# 为记忆嵌入表添加重要性权重列的安全补丁
# 包含正向迁移和回滚机制

import sqlite3
import json

def apply_importance_weight_column_patch(db_path: str = "workspace/v3_episodic_memory.db"):
    """
    为记忆嵌入表添加重要性权重列，并创建相应的复合索引
    """
    result = {
        'success': False,
        'message': '',
        'changes_applied': [],
        'rollback_info': {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否已经存在 importance_weight 列
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'importance_weight' in column_names:
            result['success'] = True
            result['message'] = '重要性权重列已存在，无需重复添加'
            conn.close()
            return result
        
        # 1. 添加 importance_weight 列，默认值为 0.5（中等重要性）
        cursor.execute("""
            ALTER TABLE memory_embeddings 
            ADD COLUMN importance_weight REAL DEFAULT 0.5 NOT NULL
        """)
        result['changes_applied'].append('添加 importance_weight 列')
        result['rollback_info']['drop_column'] = True
        
        # 2. 创建复合索引以优化查询性能
        # 基于重要性权重和时间戳的复合索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_weight_ts 
            ON memory_embeddings(importance_weight DESC, timestamp DESC)
        """)
        result['changes_applied'].append('创建复合索引 idx_memory_embeddings_weight_ts')
        result['rollback_info']['drop_index_weight_ts'] = True
        
        # 3. 基于重要性权重和源类型的复合索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_weight_source 
            ON memory_embeddings(importance_weight DESC, source_type)
        """)
        result['changes_applied'].append('创建复合索引 idx_memory_embeddings_weight_source')
        result['rollback_info']['drop_index_weight_source'] = True
        
        # 4. 更新现有记录的重要性权重
        cursor.execute("""
            UPDATE memory_embeddings 
            SET importance_weight = CASE 
                WHEN julianday('now') - julianday(timestamp) < 7 THEN 0.8
                WHEN julianday('now') - julianday(timestamp) < 30 THEN 0.6
                ELSE 0.4
            END
        """)
        updated_count = cursor.rowcount
        result['changes_applied'].append(f'更新 {updated_count} 条记录的重要性权重')
        
        conn.commit()
        conn.close()
        
        result['success'] = True
        result['message'] = f'成功应用补丁：{", ".join(result["changes_applied"])}'
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        result['message'] = f'应用补丁失败: {str(e)}'
        result['error'] = str(e)
    
    return result

def rollback_importance_weight_column_patch(db_path: str = "workspace/v3_episodic_memory.db"):
    """
    回滚重要性权重列补丁
    """
    result = {
        'success': False,
        'message': '',
        'changes_reverted': []
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否存在 importance_weight 列
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'importance_weight' not in column_names:
            result['success'] = True
            result['message'] = '重要性权重列不存在，无需回滚'
            conn.close()
            return result
        
        # SQLite 不支持直接删除列，需要重建表
        # 1. 创建新表（不含 importance_weight 列）
        cursor.execute("""
            CREATE TABLE memory_embeddings_new AS 
            SELECT memory_id, source_type, content_text, embedding_json, timestamp, embedding_source
            FROM memory_embeddings
        """)
        
        # 2. 删除旧表
        cursor.execute("DROP TABLE memory_embeddings")
        
        # 3. 重命名新表
        cursor.execute("ALTER TABLE memory_embeddings_new RENAME TO memory_embeddings")
        
        result['changes_reverted'].append('移除 importance_weight 列')
        
        # 4. 删除相关索引
        cursor.execute("DROP INDEX IF EXISTS idx_memory_embeddings_weight_ts")
        cursor.execute("DROP INDEX IF EXISTS idx_memory_embeddings_weight_source")
        result['changes_reverted'].append('删除复合索引')
        
        conn.commit()
        conn.close()
        
        result['success'] = True
        result['message'] = f'成功回滚补丁：{", ".join(result["changes_reverted"])}'
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        result['message'] = f'回滚补丁失败: {str(e)}'
        result['error'] = str(e)
    
    return result

# 主函数：应用补丁
def main(input_args=""):
    """
    应用重要性权重列补丁到记忆嵌入表
    """
    import json
    
    # 解析输入参数
    params = {}
    if input_args:
        if isinstance(input_args, str):
            try:
                params = json.loads(input_args)
            except:
                params = {}
        elif isinstance(input_args, dict):
            params = input_args
    
    db_path = params.get('db_path', 'workspace/v3_episodic_memory.db')
    action = params.get('action', 'apply')
    
    if action == 'rollback':
        return rollback_importance_weight_column_patch(db_path)
    else:
        return apply_importance_weight_column_patch(db_path)