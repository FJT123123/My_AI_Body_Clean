"""
自动生成的技能模块
需求: 从memory_embeddings表获取数据并计算动态重要性权重，正确处理现有的表结构使用memory_id作为主键
生成时间: 2026-03-22 04:32:31
"""

# skill_name: dynamic_memory_importance_calculator

def main(args=None):
    """
    从memory_embeddings表获取数据并计算动态重要性权重，正确处理现有的表结构使用memory_id作为主键
    """
    import sqlite3
    import math
    import json
    from datetime import datetime
    
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not isinstance(db_path, str):
        return {
            'result': {'error': 'Database path not provided or invalid'},
            'insights': ['无法访问数据库，缺少有效的db_path参数'],
            'facts': [],
            'memories': []
        }
    
    if not isinstance(db_path, str) or not db_path.endswith('.db'):
        return {
            'result': {'error': 'Invalid database path format'},
            'insights': ['数据库路径格式不正确'],
            'facts': [],
            'memories': []
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 首先检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='memory_embeddings';
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            return {
                'result': {'error': 'memory_embeddings table does not exist'},
                'insights': ['memory_embeddings表不存在'],
                'facts': [],
                'memories': []
            }
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(memory_embeddings);")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 验证必需的列是否存在
        required_columns = ['memory_id', 'embedding', 'created_at']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            return {
                'result': {'error': f'Missing required columns: {missing_columns}'},
                'insights': [f'memory_embeddings表缺少必需的列: {missing_columns}'],
                'facts': [],
                'memories': []
            }
        
        # 获取记忆数据
        query = """
        SELECT memory_id, embedding, created_at
        FROM memory_embeddings
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            return {
                'result': {'count': 0, 'weights': []},
                'insights': ['memory_embeddings表中没有数据'],
                'facts': [],
                'memories': []
            }
        
        # 解析数据并计算动态权重
        memory_data = []
        for row in rows:
            memory_id, embedding_str, created_at = row
            try:
                embedding = json.loads(embedding_str) if embedding_str else []
                memory_data.append({
                    'memory_id': memory_id,
                    'embedding': embedding,
                    'created_at': created_at
                })
            except json.JSONDecodeError:
                # 如果解析失败，跳过该条记录
                continue
        
        # 计算动态权重
        calculated_weights = []
        current_time = datetime.now()
        
        for i, memory in enumerate(memory_data):
            # 基础权重：基于嵌入向量的长度
            base_weight = len(memory['embedding']) if memory['embedding'] else 0
            
            # 时间衰减权重：越新的记忆越重要
            try:
                memory_time = datetime.fromisoformat(memory['created_at'].replace('Z', '+00:00'))
                time_diff = (current_time - memory_time).total_seconds()
                # 时间衰减因子，越新越重要
                time_weight = 1.0 / (1.0 + time_diff / 3600)  # 按小时衰减
            except:
                time_weight = 0.5  # 如果时间格式错误，使用默认值
            
            # 综合权重
            total_weight = base_weight * time_weight
            
            calculated_weights.append({
                'memory_id': memory['memory_id'],
                'base_weight': base_weight,
                'time_weight': time_weight,
                'dynamic_weight': total_weight,
                'created_at': memory['created_at']
            })
        
        # 按权重排序
        calculated_weights.sort(key=lambda x: x['dynamic_weight'], reverse=True)
        
        # 计算统计信息
        total_memories = len(calculated_weights)
        avg_weight = sum(w['dynamic_weight'] for w in calculated_weights) / total_memories if total_memories > 0 else 0
        max_weight = max((w['dynamic_weight'] for w in calculated_weights), default=0)
        min_weight = min((w['dynamic_weight'] for w in calculated_weights), default=0)
        
        conn.close()
        
        # 生成洞察
        insights = [
            f'计算了{total_memories}条记忆的动态权重',
            f'平均权重: {avg_weight:.2f}',
            f'最高权重: {max_weight:.2f}',
            f'最低权重: {min_weight:.2f}'
        ]
        
        # 生成事实
        facts = [
            ['memory_embeddings', 'has_entries_count', str(total_memories)],
            ['dynamic_weights', 'average_value', f'{avg_weight:.2f}'],
            ['dynamic_weights', 'max_value', f'{max_weight:.2f}']
        ]
        
        # 生成记忆
        memories = [
            {
                'event_type': 'skill_executed',
                'content': f'动态记忆重要性权重计算完成，处理了{total_memories}条记忆',
                'importance': avg_weight,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return {
            'result': {
                'count': total_memories,
                'weights': calculated_weights,
                'statistics': {
                    'total': total_memories,
                    'average_weight': avg_weight,
                    'max_weight': max_weight,
                    'min_weight': min_weight
                }
            },
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except sqlite3.Error as e:
        return {
            'result': {'error': f'Database error: {str(e)}'},
            'insights': ['数据库访问失败'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'Unexpected error: {str(e)}'},
            'insights': ['计算动态记忆权重时发生错误'],
            'facts': [],
            'memories': []
        }