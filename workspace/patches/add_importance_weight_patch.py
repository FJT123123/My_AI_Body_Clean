def add_importance_weight_to_memory_embeddings():
    """
    为memory_embeddings表添加importance_weight列的安全补丁
    """
    import sqlite3
    import os
    
    db_path = "workspace/v3_episodic_memory.db"
    
    # 验证数据库文件是否存在
    if not os.path.exists(db_path):
        return {"success": False, "message": f"数据库文件不存在: {db_path}"}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings'")
        if not cursor.fetchone():
            conn.close()
            return {"success": False, "message": "memory_embeddings表不存在"}
        
        # 检查importance_weight列是否已存在
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "importance_weight" in columns:
            conn.close()
            return {"success": True, "message": "importance_weight列已存在，无需添加"}
        
        # 添加importance_weight列
        cursor.execute("ALTER TABLE memory_embeddings ADD COLUMN importance_weight REAL DEFAULT 1.0")
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "成功添加importance_weight列", "columns_before": columns}
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return {"success": False, "message": f"操作失败: {str(e)}"}