import os
import sys
import sqlite3
import json
import uuid
from datetime import datetime

# 确保能找到 capabilities
_file_path = os.path.abspath(__file__)
_patches_dir = os.path.dirname(_file_path)
_workspace_dir = os.path.dirname(_patches_dir)
ROOT_DIR = os.path.dirname(_workspace_dir)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if _workspace_dir not in sys.path:
    sys.path.insert(0, _workspace_dir)

# 模拟环境
import tempfile
_tmp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
DB_PATH = _tmp_db.name
_tmp_db.close()

class MemoryCore:
    def __init__(self, db_path):
        self.db_path = db_path
        # 初始化表结构
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                event_type TEXT,
                content TEXT,
                importance REAL,
                timestamp TEXT,
                tags TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def recall(self, query):
        # 模拟原始检索结果
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_type, content, importance, timestamp, tags FROM memories WHERE content LIKE ?", (f'%{query}%',))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'event_type': row[1],
                'content': row[2],
                'importance': row[3],
                'timestamp': row[4],
                'tags': json.loads(row[5]) if row[5] else []
            })
        return results

def setup_dummy_data(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 插入一些测试记忆
    test_memories = [
        ("learning_001", "learning", "I learned that dynamic weighting is important.", 0.8, datetime.now().isoformat(), '["system", "test"]'),
        ("thought_001", "autonomous_thought", "I think memory retrieval needs to be optimized.", 0.6, datetime.now().isoformat(), '["system", "test"]'),
        ("mission_001", "user_mission_started", "The user asked me to fix the memory system.", 0.9, datetime.now().isoformat(), '["system", "test"]')
    ]
    
    for m in test_memories:
        cursor.execute(
            "INSERT OR REPLACE INTO memories (id, event_type, content, importance, timestamp, tags) VALUES (?,?,?,?,?,?)",
            m
        )
    
    conn.commit()
    conn.close()
    print(f"✅ 已插入 {len(test_memories)} 条测试数据")

def run_verification():
    print("=== 内存权重集成验证 (带数据) ===")
    
    # 1. 确保补丁已应用 (手动模拟 patch 的作用)
    from workspace.patches.memory_core_dynamic_weighting_integration_fix import enhanced_recall_memory_with_weighting
    
    memory_core = MemoryCore(DB_PATH)
    # 手动注入方法（模拟补丁行为）
    memory_core.__class__.enhanced_recall_memory_with_weighting = enhanced_recall_memory_with_weighting
    
    # 2. 准备数据
    setup_dummy_data(DB_PATH)
    
    # 3. 测试检索
    query = "memory"
    print(f"🔍 正在检索关键词: '{query}'")
    
    results = memory_core.enhanced_recall_memory_with_weighting(query, context="optimizing memory retrieval")
    
    if results:
        print(f"✅ 找到 {len(results)} 条结果")
        for i, res in enumerate(results):
            weight = res.get('weight', 'N/A')
            content = res.get('content', '')
            print(f"  [{i+1}] Weight: {weight:.4f} | Content: {str(content)[:50]}...")
            
        if any('weight' in r for r in results):
            print("\n🎉 验证成功：动态权重已成功计算并应用于检索结果！")
        else:
            print("\n❌ 验证失败：结果中缺少权重信息。")
    else:
        print("\n❌ 验证失败：未找到任何结果。")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"\n❌ 验证过程中出错: {e}")
        import traceback
        traceback.print_exc()
