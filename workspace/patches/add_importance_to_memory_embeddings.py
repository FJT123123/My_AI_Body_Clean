# 为记忆嵌入表添加重要性权重列的补丁

import sqlite3
import os

def add_importance_column_to_memory_embeddings():
    """为memory_embeddings表添加importance列"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'v3_episodic_memory.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在importance列
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'importance' not in columns:
            # 添加importance列，默认值为0.5（中等重要性）
            cursor.execute("ALTER TABLE memory_embeddings ADD COLUMN importance REAL DEFAULT 0.5")
            print("成功为memory_embeddings表添加了importance列")
        else:
            print("memory_embeddings表已存在importance列")
            
        # 创建复合索引以优化查询性能
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_embeddings_importance_ts ON memory_embeddings(importance DESC, timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memory_embeddings_importance_source ON memory_embeddings(importance DESC, embedding_source)")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"添加importance列时出错: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

# 执行函数
if __name__ == "__main__":
    add_importance_column_to_memory_embeddings()