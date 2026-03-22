# tool_name: get_memory_embeddings_with_importance_weight
from typing import Any, Dict, List, Optional
import json
from datetime import datetime
from langchain.tools import tool
import sqlite3
import os

@tool
def get_memory_embeddings_with_importance_weight(
    query: Optional[str] = None,
    limit: Optional[int] = 10,
    time_decay_rate: Optional[float] = 0.1,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    从memory_embeddings表获取数据并计算动态重要性权重的工具函数
    
    这个工具正确处理现有的表结构:
    - 使用 memory_id 作为唯一标识符 (而不是 id)
    - 使用 embedding_json 列存储嵌入向量 (而不是 embedding)
    - 使用 timestamp 列存储时间戳 (而不是 created_at)
    - 使用 content_text 列存储内容 (而不是 content)
    
    Args:
        query: 可选的查询字符串，用于语义相关性计算
        limit: 返回的记忆条目数量限制，默认10
        time_decay_rate: 时间衰减率，默认0.1
        context: 可选的上下文信息，用于权重计算
        
    Returns:
        包含记忆嵌入数据和计算后重要性权重的字典列表
    """
    try:
        # 数据库路径 - 使用绝对路径
        db_path = "/Users/zhufeng/My_AI_Body_Clean/workspace/v3_episodic_memory.db"
        
        # 连接数据库并获取记忆数据
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取记忆数据 - 使用正确的列名
        if limit and limit > 0:
            cursor.execute(f"""
                SELECT memory_id, source_type, content_text, embedding_json, timestamp, embedding_source 
                FROM memory_embeddings 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """)
        else:
            cursor.execute("""
                SELECT memory_id, source_type, content_text, embedding_json, timestamp, embedding_source 
                FROM memory_embeddings 
                ORDER BY timestamp DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                'status': 'success',
                'message': '记忆嵌入表为空',
                'data': []
            }
        
        # 计算动态重要性权重
        memories_with_weights = []
        current_time = datetime.now()
        
        for row in rows:
            memory_id, source_type, content_text, embedding_json, timestamp_str, embedding_source = row
            
            # 解析时间戳
            try:
                if timestamp_str.endswith('Z'):
                    timestamp = datetime.fromisoformat(timestamp_str[:-1] + '+00:00')
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)
                time_diff = (current_time - timestamp).total_seconds()
                # 时间衰减权重 (越近的权重越高)
                time_weight = max(0.1, 1.0 / (1.0 + time_decay_rate * time_diff / 3600))  # 衰减基于小时
            except Exception as e:
                time_weight = 0.5  # 默认时间权重
            
            # 语义相关性权重
            semantic_weight = 1.0
            if query and content_text:
                query_lower = str(query).lower()
                content_lower = str(content_text).lower()
                if query_lower in content_lower:
                    semantic_weight = 1.5
                elif any(word in content_lower for word in query_lower.split()):
                    semantic_weight = 1.2
            
            # 上下文权重
            context_weight = 1.0
            if context and content_text:
                context_lower = str(context).lower()
                content_lower = str(content_text).lower()
                if context_lower in content_lower:
                    context_weight = 1.3
                elif any(word in content_lower for word in context_lower.split()):
                    context_weight = 1.1
            
            # 综合权重计算
            importance_weight = time_weight * semantic_weight * context_weight
            
            # 解析嵌入向量
            embedding = None
            if embedding_json:
                try:
                    embedding = json.loads(embedding_json)
                except:
                    embedding = None
            
            memory_entry = {
                'memory_id': memory_id,
                'source_type': source_type,
                'content_text': content_text,
                'embedding': embedding,
                'timestamp': timestamp_str,
                'embedding_source': embedding_source,
                'importance_weight': importance_weight,
                'weight_components': {
                    'time_weight': time_weight,
                    'semantic_weight': semantic_weight,
                    'context_weight': context_weight
                }
            }
            
            memories_with_weights.append(memory_entry)
        
        # 按重要性权重排序
        memories_with_weights.sort(key=lambda x: x['importance_weight'], reverse=True)
        
        return {
            'status': 'success',
            'message': f'成功计算了{len(memories_with_weights)}个记忆条目的动态重要性权重',
            'data': memories_with_weights
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'查询记忆嵌入时出错: {str(e)}',
            'data': []
        }