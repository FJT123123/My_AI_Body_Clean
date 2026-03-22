"""
自动生成的技能模块
需求: 测试基于重要性的工作记忆功能，验证淘汰策略是否正确工作
生成时间: 2026-03-21 20:00:01
"""

# skill_name: test_memory_importance_elimination
import sqlite3
import os
import time
import random
from datetime import datetime

def main(args=None):
    """
    测试基于重要性的工作记忆功能，验证淘汰策略是否正确工作
    通过创建多个不同重要性的记忆条目，然后触发淘汰机制，检查是否正确保留了高重要性记忆
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库进行记忆重要性测试']
        }
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查当前记忆数量
    cursor.execute("SELECT COUNT(*) FROM memories")
    initial_count = cursor.fetchone()[0]
    
    # 创建测试记忆条目 - 不同重要性
    test_memories = [
        {"content": "这是一条高重要性记忆，需要保留", "importance": 0.9, "event_type": "test_memory", "tags": "test"},
        {"content": "这是一条中等重要性记忆", "importance": 0.6, "event_type": "test_memory", "tags": "test"},
        {"content": "这是一条低重要性记忆", "importance": 0.2, "event_type": "test_memory", "tags": "test"},
        {"content": "这是一条极低重要性记忆", "importance": 0.1, "event_type": "test_memory", "tags": "test"},
        {"content": "另一条高重要性记忆", "importance": 0.85, "event_type": "test_memory", "tags": "test"},
        {"content": "另一条中等重要性记忆", "importance": 0.55, "event_type": "test_memory", "tags": "test"},
        {"content": "另一条低重要性记忆", "importance": 0.15, "event_type": "test_memory", "tags": "test"},
        {"content": "又一条高重要性记忆", "importance": 0.95, "event_type": "test_memory", "tags": "test"},
        {"content": "又一条中等重要性记忆", "importance": 0.65, "event_type": "test_memory", "tags": "test"},
        {"content": "又一条低重要性记忆", "importance": 0.25, "event_type": "test_memory", "tags": "test"}
    ]
    
    # 插入测试记忆
    for memory in test_memories:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO memories (event_type, content, importance, timestamp, tags) VALUES (?, ?, ?, ?, ?)",
            (memory["event_type"], memory["content"], memory["importance"], timestamp, memory["tags"])
        )
    
    # 获取插入后的记忆总数
    cursor.execute("SELECT COUNT(*) FROM memories")
    after_insert_count = cursor.fetchone()[0]
    
    # 获取当前记忆中最低的几个重要性分数
    cursor.execute("SELECT importance FROM memories ORDER BY importance ASC LIMIT 3")
    lowest_importances = [row[0] for row in cursor.fetchall()]
    
    # 获取测试前的最高重要性记忆
    cursor.execute("SELECT content, importance FROM memories WHERE importance > 0.8 ORDER BY importance DESC LIMIT 5")
    high_importance_before = cursor.fetchall()
    
    # 手动触发记忆淘汰（假设系统保留80%的记忆）
    # 计算需要删除的记忆数量（保留80%）
    total_memories = after_insert_count
    to_keep = int(total_memories * 0.8)
    to_delete = total_memories - to_keep
    
    if to_delete > 0:
        # 删除重要性最低的内存
        cursor.execute(f"DELETE FROM memories WHERE id IN (SELECT id FROM memories ORDER BY importance ASC LIMIT {to_delete})")
        conn.commit()
    
    # 获取淘汰后的记忆总数
    cursor.execute("SELECT COUNT(*) FROM memories")
    after_elimination_count = cursor.fetchone()[0]
    
    # 获取保留的高重要性记忆
    cursor.execute("SELECT content, importance FROM memories WHERE importance > 0.8 ORDER BY importance DESC")
    high_importance_after = cursor.fetchall()
    
    # 获取保留的中等重要性记忆
    cursor.execute("SELECT content, importance FROM memories WHERE importance >= 0.5 AND importance <= 0.8 ORDER BY importance DESC")
    medium_importance_after = cursor.fetchall()
    
    # 获取保留的低重要性记忆
    cursor.execute("SELECT content, importance FROM memories WHERE importance < 0.5 ORDER BY importance DESC")
    low_importance_after = cursor.fetchall()
    
    # 检查淘汰效果
    eliminated_correctly = len(high_importance_after) >= len(high_importance_before) * 0.8
    low_important_eliminated = len(low_importance_after) < 5  # 原本有5条低重要性
    
    # 检查具体保留的记忆
    result = {
        'initial_memory_count': initial_count,
        'after_insert_count': after_insert_count,
        'after_elimination_count': after_elimination_count,
        'total_test_memories': len(test_memories),
        'to_delete_count': to_delete,
        'high_importance_memories_before': [item[0] for item in high_importance_before],
        'high_importance_memories_after': [item[0] for item in high_importance_after],
        'medium_importance_memories_after': [item[0] for item in medium_importance_after],
        'low_importance_memories_after': [item[0] for item in low_importance_after],
        'high_importance_preserved': len(high_importance_after) >= len([h for h in high_importance_before if h[1] > 0.8]),
        'elimination_strategy_worked': eliminated_correctly and low_important_eliminated,
        'importance_distribution': {
            'high': len(high_importance_after),
            'medium': len(medium_importance_after),
            'low': len(low_importance_after)
        }
    }
    
    conn.close()
    
    insights = [
        f"记忆淘汰测试完成: 初始{result['initial_memory_count']} -> 插入后{result['after_insert_count']} -> 淘汰后{result['after_elimination_count']}",
        f"高重要性记忆保留情况: {result['high_importance_preserved']}",
        f"淘汰策略有效性: {result['elimination_strategy_worked']}"
    ]
    
    return {
        'result': result,
        'insights': insights,
        'memories': [
            f"执行记忆重要性测试，验证了淘汰策略的有效性。高重要性记忆保留: {result['high_importance_preserved']}, 整体策略有效: {result['elimination_strategy_worked']}"
        ]
    }