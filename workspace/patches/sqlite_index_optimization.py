# patch_purpose: 为SQLite数据库添加更多性能优化索引

import sqlite3
import os

def add_sqlite_indexes():
    """为SQLite数据库添加更多性能优化索引"""
    # 使用全局DB_PATH变量
    global DB_PATH
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 为memories表添加更多索引
        # 1. 按event_type和importance的复合索引（加速按事件类型和重要性查询）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_event_type_imp 
            ON memories(event_type, importance DESC)
        """)
        
        # 2. 按timestamp的索引（加速时间范围查询）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_timestamp 
            ON memories(timestamp DESC)
        """)
        
        # 3. 按tags的索引（加速按标签查询）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_tags 
            ON memories(tags)
        """)
        
        # 为skill_results表添加更多索引
        # 1. 按execution_time_ms的索引（加速按执行时间查询）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_results_exec_time 
            ON skill_results(execution_time_ms DESC)
        """)
        
        # 2. 按result_summary的索引（加速按结果摘要搜索）
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skill_results_summary 
            ON skill_results(result_summary)
        """)
        
        # 为knowledge_triples表添加索引
        # 1. 按subject和relation的复合索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_triples_subject_rel 
            ON knowledge_triples(subject, relation)
        """)
        
        # 2. 按object的索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_triples_object 
            ON knowledge_triples(object)
        """)
        
        # 3. 按timestamp的索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_knowledge_triples_timestamp 
            ON knowledge_triples(timestamp DESC)
        """)
        
        # 为memory_embeddings表添加索引
        # 1. 按source_type的索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_source_type 
            ON memory_embeddings(source_type)
        """)
        
        # 2. 按embedding_source的索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_embeddings_embedding_source 
            ON memory_embeddings(embedding_source)
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ 已成功添加SQLite性能优化索引")
        return True
        
    except Exception as e:
        print(f"❌ 添加SQLite索引时出错: {e}")
        return False

# 执行索引优化
add_sqlite_indexes()