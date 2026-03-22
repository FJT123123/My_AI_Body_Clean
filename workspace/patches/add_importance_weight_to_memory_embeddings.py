# 为记忆嵌入表添加重要性权重列的安全补丁

import sqlite3
import os

def add_importance_weight_column_to_memory_embeddings():
    """
    安全地为 memory_embeddings 表添加 importance_weight 列
    
    这个补丁实现了以下功能：
    1. 检查 memory_embeddings 表是否已经存在 importance_weight 列
    2. 如果不存在，则添加该列，默认值为 0.5（中等重要性）
    3. 确保操作的安全性和可回滚性
    4. 更新相关的索引以优化基于重要性权重的查询性能
    """
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(__file__), '..', 'v3_episodic_memory.db')
    
    # 验证数据库文件存在
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"数据库文件不存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # 检查表结构，确认是否已存在 importance_weight 列
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'importance_weight' not in columns:
            # 添加 importance_weight 列，默认值为 0.5
            cursor.execute(
                "ALTER TABLE memory_embeddings ADD COLUMN importance_weight REAL DEFAULT 0.5"
            )
            
            # 创建复合索引来优化基于重要性权重的查询
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_embeddings_imp_ts 
                ON memory_embeddings (importance_weight DESC, created_at DESC)
            """)
            
            conn.commit()
            return {
                "success": True,
                "message": "成功为 memory_embeddings 表添加 importance_weight 列",
                "action": "column_added",
                "index_created": True
            }
        else:
            return {
                "success": True,
                "message": "memory_embeddings 表已包含 importance_weight 列",
                "action": "none_required"
            }
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# 注册补丁函数，使其可以被 apply_hot_patch 调用
__all__ = ['add_importance_weight_column_to_memory_embeddings']