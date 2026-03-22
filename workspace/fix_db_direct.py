import os
import sqlite3

# 直接修复数据库
db_path = "/Users/zhufeng/My_AI_Body/workspace/v3_episodic_memory.db"

# 检查数据库是否存在
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

# 连接数据库并添加列
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查列是否存在
    cursor.execute("PRAGMA table_info(memory_embeddings)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'importance' not in columns:
        cursor.execute("ALTER TABLE memory_embeddings ADD COLUMN importance REAL DEFAULT 0.5")
        conn.commit()
        print("Successfully added importance column!")
    else:
        print("Importance column already exists!")
    
    conn.close()
    exit(0)
except Exception as e:
    print(f"Error: {e}")
    exit(1)