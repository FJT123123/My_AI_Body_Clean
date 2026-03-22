"""
MemoryCore 动态权重集成补丁 - 修复版
修正导入路径问题，确保能正确调用 calculate_memory_weights_batch 函数
"""
import os
import sys
import sys

# 确保 workspace 在 sys.path 中
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(os.path.dirname(_current_dir))
_workspace_dir = os.path.join(_root_dir, "workspace")
if _workspace_dir not in sys.path:
    sys.path.insert(0, _workspace_dir)

def enhanced_recall_memory_with_weighting(self, query, context=None, apply_weighting=True):
    """
    增强版记忆检索，支持动态权重计算
    
    Args:
        query: 检索关键词
        context: 当前上下文（用于计算语义相关性）
        apply_weighting: 是否应用动态权重计算
    
    Returns:
        带有权重信息的记忆列表
    """
    try:
        # 首先执行原始检索，适配不同的方法名 (recall vs recall_memory)
        if hasattr(self, 'recall'):
            raw_memories = self.recall(query)
        elif hasattr(self, 'recall_memory'):
            raw_memories = self.recall_memory(query)
        else:
            print("⚠️ 无法在 {} 对象上找到检索方法".format(self.__class__.__name__))
            return []
        
        if not apply_weighting or not raw_memories:
            return raw_memories
        
        # 如果没有提供上下文，使用查询作为上下文
        if context is None:
            context = query
        
        # 将检索结果转换为适合权重计算的格式
        memories_for_weighting = []
        for i, memory_item in enumerate(raw_memories):
            # 为每个记忆添加时间戳和内容
            memory_dict = {
                'id': str(i),
                'content': "{} {} {}".format(
                    memory_item.get('Source', ''), 
                    memory_item.get('Relation', ''), 
                    memory_item.get('Target', '')
                ).strip(),
                'timestamp': __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 使用字符串格式的时间戳
                'importance': 0.5,  # 默认重要性
                'activity': 0.5     # 默认活跃度
            }
            memories_for_weighting.append(memory_dict)
        
        # 应用动态权重计算 - 修正导入方式
        try:
            # 直接导入模块并调用函数
            import workspace.capabilities.dynamic_memory_weighting_capability as dmwc
            weighted_results = dmwc.calculate_memory_weights_batch(memories_for_weighting, context)
        except ImportError:
            # 备用方案：尝试其他导入方式
            try:
                from dynamic_memory_weighting_capability import calculate_memory_weights_batch
                weighted_results = calculate_memory_weights_batch(memories_for_weighting, context)
            except Exception as e2:
                print("⚠️ 动态权重计算导入失败: {}".format(e2))
                return raw_memories
        except Exception as e:
            print("⚠️ 动态权重计算失败，返回原始结果: {}".format(e))
            return raw_memories
        
        # 将权重信息合并回原始记忆结构
        enhanced_memories = []
        for i, original_memory in enumerate(raw_memories):
            if i < len(weighted_results):
                enhanced_memory = original_memory.copy()
                enhanced_memory['weight'] = weighted_results[i].get('weight', 0.0)
                enhanced_memory['time_weight'] = weighted_results[i].get('time_weight', 0.0)
                enhanced_memory['relevance_weight'] = weighted_results[i].get('relevance_weight', 0.0)
                enhanced_memories.append(enhanced_memory)
            else:
                enhanced_memory = original_memory.copy()
                enhanced_memory['weight'] = 0.0
                enhanced_memory['time_weight'] = 0.0
                enhanced_memory['relevance_weight'] = 0.0
                enhanced_memories.append(enhanced_memory)
        
        # 按权重排序
        enhanced_memories.sort(key=lambda x: x.get('weight', 0.0), reverse=True)
        
        return enhanced_memories
        
    except Exception as e:
        print("⚠️ 动态权重记忆检索失败: {}".format(e))
        # 尝试返回原始检索结果
        try:
            if hasattr(self, 'recall_memory'):
                return self.recall_memory(query)
            elif hasattr(self, 'recall'):
                return self.recall(query)
            else:
                return []
        except:
            return []

# 添加新方法到 MemoryCore 类
# 注意：该部分通常由集成框架调用，或者由手动注入脚本调用
# from openclaw_continuity import MemoryCore
# MemoryCore.enhanced_recall_memory_with_weighting = enhanced_recall_memory_with_weighting

print("✅ MemoryCore 动态权重集成补丁（修复版）已加载！")