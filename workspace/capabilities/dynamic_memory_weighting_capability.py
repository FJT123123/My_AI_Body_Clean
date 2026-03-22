# Dynamic Memory Weighting Capability

import json
import math
import os
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np

__contract__ = {
    "interface_type": "class_based",
    "primary_class": "DynamicMemoryWeightingCapability",
    "entry_points": ["calculate_memory_weights_batch", "run_dynamic_memory_weighting_cycle"],
    "version": "1.1.0"
}

class DynamicMemoryWeightingCapability:
    def __init__(self, memory_db_path: str = None, lock: threading.Lock = None):
        if memory_db_path is None:
            # 尝试找到正确的数据库路径
            current_dir = os.path.dirname(__file__)
            workspace_dir = os.path.join(current_dir, '..')
            possible_paths = [
                os.path.join(workspace_dir, "v3_episodic_memory.db"),
                os.path.join(workspace_dir, "memory_graph.db"),
                os.path.join(workspace_dir, "memory.db"),
                os.path.join(workspace_dir, "memories.db"),
                os.path.join(current_dir, "../v3_episodic_memory.db"),
                os.path.join(current_dir, "../memory_graph.db"),
                os.path.join(current_dir, "../workspace/memory.db"),
                os.path.join(current_dir, "../memories.db"),
                os.path.join(current_dir, "../workspace/v3_episodic_memory.db")
            ]
            
            self.db_path = None
            for path in possible_paths:
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    self.db_path = path
                    break
            
            if self.db_path is None:
                # 如果没有找到现有数据库，使用默认路径
                self.db_path = os.path.join(os.path.dirname(__file__), "../memory_graph.db")
        else:
            self.db_path = memory_db_path
        
        self.lock = lock if lock is not None else threading.Lock()
    
    def _calculate_time_decay_weight(self, timestamp_str: str, current_time: datetime = None) -> float:
        """计算基于时间衰减的权重"""
        return self.calculate_time_decay_weight(timestamp_str, current_time)
    
    def calculate_time_decay_weight(self, timestamp_str: str, current_time: datetime = None) -> float:
        """公共接口：计算基于时间衰减的权重"""
        if current_time is None:
            current_time = datetime.now()
        
        try:
            # 解析时间戳
            if isinstance(timestamp_str, str):
                if len(timestamp_str) == 19:  # YYYY-MM-DD HH:MM:SS
                    memory_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                elif len(timestamp_str) == 10:  # YYYY-MM-DD
                    memory_time = datetime.strptime(timestamp_str, "%Y-%m-%d")
                else:
                    # 尝试其他格式
                    memory_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif isinstance(timestamp_str, (int, float)):
                # Handle epoch timestamp floats
                memory_time = datetime.fromtimestamp(float(timestamp_str))
            else:
                memory_time = timestamp_str
            
            # 确保 memory_time 是带时区的或者都是无时区的，防止 offset-naive 和 offset-aware 报错
            if memory_time.tzinfo is not None and current_time.tzinfo is None:
                current_time = current_time.replace(tzinfo=memory_time.tzinfo)
            elif memory_time.tzinfo is None and current_time.tzinfo is not None:
                memory_time = memory_time.replace(tzinfo=current_time.tzinfo)
            
            # 计算时间差（天数）
            time_diff = (current_time - memory_time).total_seconds() / 86400.0
            
            # 使用指数衰减函数，半衰期设为30天
            half_life_days = 30.0
            decay_factor = math.log(2) / half_life_days
            time_weight = math.exp(-decay_factor * time_diff)
            
            # 确保权重在0-1范围内
            return max(0.0, min(1.0, time_weight))
            
        except Exception as e:
            print(f"⚠️ 时间权重计算错误: {e}")
            return 0.5  # 默认权重
    
    def _calculate_semantic_similarity(self, query: str, memory_content: str) -> float:
        """计算语义相似度（简化版，不依赖外部模型）"""
        return self.calculate_semantic_similarity(query, memory_content)
    
    def calculate_semantic_similarity(self, query: str, memory_content: str) -> float:
        """公共接口：计算语义相似度（简化版，不依赖外部模型）"""
        try:
            # 简单的关键词匹配相似度
            query_words = set(query.lower().split())
            content_words = set(memory_content.lower().split())
            
            if not query_words or not content_words:
                return 0.0
            
            # 计算Jaccard相似度
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            jaccard_sim = len(intersection) / len(union) if union else 0.0
            
            return jaccard_sim
            
        except Exception as e:
            print(f"⚠️ 语义相似度计算错误: {e}")
            return 0.5
    
    def _get_memory_timestamp(self, memory_item: Dict[str, Any]) -> str:
        """从记忆项中提取时间戳"""
        # 优先从专门的时间字段获取
        for time_field in ['timestamp', 'last_seen', 'created_at', 'time']:
            if time_field in memory_item:
                return memory_item[time_field]
        
        # 如果没有时间字段，返回当前时间的字符串表示
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_memory_content_for_similarity(self, memory_item: Dict[str, Any]) -> str:
        """从记忆项中提取用于语义相似度计算的内容"""
        # 优先使用内容字段
        content_fields = ['content', 'text', 'Target', 'Source']
        for field in content_fields:
            if field in memory_item and memory_item[field]:
                return str(memory_item[field])
        
        # 如果都没有，组合所有字段
        return " ".join([str(v) for v in memory_item.values() if v])
    
    def _recall_basic_memories_from_sqlite(self, query: str) -> List[Dict[str, Any]]:
        """从SQLite数据库执行基本的记忆检索"""
        results = []
        
        # 调试信息
        print(f"🔍 尝试访问数据库: {self.db_path}")
        print(f"📁 数据库存在: {os.path.exists(self.db_path) if self.db_path else False}")
        
        if not self.db_path or not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            # 尝试其他可能的路径
            alt_paths = [
                os.path.join(os.path.dirname(__file__), "../workspace/v3_episodic_memory.db"),
                os.path.join(os.path.dirname(__file__), "../v3_episodic_memory.db"),
                os.path.join(os.path.dirname(__file__), "../workspace/memory_graph.db"),
                os.path.join(os.path.dirname(__file__), "../workspace/memory.db")
            ]
            
            for alt_path in alt_paths:
                if os.path.exists(alt_path) and os.path.getsize(alt_path) > 0:
                    self.db_path = alt_path
                    print(f"✅ 找到替代且非空的数据库: {self.db_path}")
                    break
            
            if not os.path.exists(self.db_path):
                print(f"❌ 未找到任何数据库文件")
                return results
        
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 尝试不同的表结构
                tables_to_try = [
                    # memory_graph.db 结构
                    ("nodes", "relationships", "SELECT n1.id AS Source, r.type AS Relation, n2.id AS Target, n1.last_seen AS timestamp, n1.content AS content FROM nodes n1 LEFT JOIN relationships r ON n1.id = r.source LEFT JOIN nodes n2 ON r.target = n2.id WHERE n1.id LIKE ? OR n1.type LIKE ? OR n1.content LIKE ? ORDER BY n1.last_seen DESC LIMIT 20"),
                    # v3_episodic_memory.db 结构
                    ("memories", None, "SELECT id AS Source, 'MENTIONS' AS Relation, content AS Target, timestamp, content FROM memories WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 20")
                ]
                
                for table_info in tables_to_try:
                    try:
                        if len(table_info) == 3:
                            table_name, rel_table, query_sql = table_info
                            
                            # 检查表是否存在
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                            if cursor.fetchone():
                                if table_name == "memories":
                                    cursor.execute(query_sql, (f'%{query}%',))
                                else:
                                    cursor.execute(query_sql, (f'%{query}%', f'%{query}%', f'%{query}%'))
                                
                                for row in cursor.fetchall():
                                    if row[0]:  # 如果有源节点
                                        result = {
                                            "Source": row[0],
                                            "Relation": row[1] if row[1] else "MENTIONS",
                                            "Target": row[2] if row[2] else "Unknown",
                                            "timestamp": row[3] if row[3] else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                            "content": row[4] if row[4] else f"{row[0]} {row[1] if row[1] else ''} {row[2] if row[2] else ''}"
                                        }
                                        results.append(result)
                                
                                if results:
                                    break
                    except Exception as e:
                        continue
                
                conn.close()
                
            except Exception as e:
                print(f"⚠️ SQLite检索错误: {e}")
        
        return results
    
    def calculate_memory_weights(self, memories: List[Dict[str, Any]], 
                               query: str = None, 
                               context: str = None) -> List[Dict[str, Any]]:
        """为记忆列表计算动态权重"""
        if not memories:
            return []
        
        current_time = datetime.now()
        weighted_memories = []
        
        for memory in memories:
            # 计算时间衰减权重
            timestamp = self._get_memory_timestamp(memory)
            time_weight = self._calculate_time_decay_weight(timestamp, current_time)
            
            # 计算语义相关性权重
            memory_content = self._get_memory_content_for_similarity(memory)
            semantic_weight = 0.5  # 默认值
            
            if query:
                semantic_weight = self._calculate_semantic_similarity(query, memory_content)
            elif context:
                semantic_weight = self._calculate_semantic_similarity(context, memory_content)
            
            # 组合权重（可以调整权重比例）
            final_weight = (time_weight * 0.4) + (semantic_weight * 0.6)
            
            # 添加权重信息到记忆项
            weighted_memory = memory.copy()
            weighted_memory['weight'] = final_weight
            weighted_memory['time_weight'] = time_weight
            weighted_memory['relevance_weight'] = semantic_weight
            
            weighted_memories.append(weighted_memory)
        
        # 按权重降序排序
        weighted_memories.sort(key=lambda x: x['weight'], reverse=True)
        
        return weighted_memories
    
    def enhanced_recall_memory_with_weighting(self, query: str, 
                                            context: str = None,
                                            apply_weighting: bool = True) -> List[Dict[str, Any]]:
        """增强版记忆检索，带动态权重计算"""
        # 首先执行基本的记忆检索
        basic_memories = self._recall_basic_memories_from_sqlite(query)
        
        if not apply_weighting or not basic_memories:
            return basic_memories
        
        # 应用动态权重计算
        weighted_memories = self.calculate_memory_weights(
            basic_memories, 
            query=query, 
            context=context
        )
        
        return weighted_memories

# --- 模块级包装函数 (用于向后兼容和补丁调用) ---

def calculate_time_decay_weight(timestamp, current_time=None, decay_rate=0.1):
    """Calculate time decay weight for a memory"""
    capability = DynamicMemoryWeightingCapability()
    return capability.calculate_time_decay_weight(timestamp, current_time)

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity between two texts"""
    capability = DynamicMemoryWeightingCapability()
    return capability.calculate_semantic_similarity(text1, text2)

def cluster_similar_memories(memories, threshold=0.5):
    """Cluster similar memories (simplified implementation)"""
    # For now, just return each memory as its own cluster
    return [[memory] for memory in memories]

def calculate_memory_weights_batch(memories, context=None, current_time=None, time_decay_rate=0.1):
    """
    为补丁 memory_core_dynamic_weighting_integration.py 提供的接口
    """
    capability = DynamicMemoryWeightingCapability()
    return capability.calculate_memory_weights(memories, context=context)

def run_dynamic_memory_weighting_cycle(memories: List[Dict[str, Any]], query: str = None, context: str = None, **kwargs):
    """
    执行动态记忆权重计算周期的通用入口
    """
    capability = DynamicMemoryWeightingCapability()
    # 注意：这里的参数适配原有的 run_dynamic_memory_weighting_cycle 逻辑
    weighted_memories = capability.calculate_memory_weights(memories, query=query, context=context)
    
    # 添加聚类（简化实现）
    memory_clusters = [[memory] for memory in weighted_memories]
    
    # 计算连续性得分（简化实现）
    continuity_score = sum(memory['weight'] for memory in weighted_memories) / len(weighted_memories) if weighted_memories else 0.0
    
    return {
        "success": True,
        "weighted_memories": weighted_memories,
        "memory_clusters": memory_clusters,
        "continuity_score": continuity_score,
        "metadata": {
            "total_memories": len(memories),
            "query_used": bool(query),
            "context_used": bool(context)
        }
    }