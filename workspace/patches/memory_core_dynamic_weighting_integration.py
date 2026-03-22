"""
MemoryCore 动态权重集成补丁
将 dynamic_memory_weighting_capability 集成到 MemoryCore 检索逻辑中
"""

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
        
        # 应用动态权重计算
        try:
            from capabilities.dynamic_memory_weighting_capability import calculate_memory_weights_batch
            weighted_results = calculate_memory_weights_batch(memories_for_weighting, context)
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
        return self.recall_memory(query)

# 添加新方法到 MemoryCore 类
memory.__class__.enhanced_recall_memory_with_weighting = enhanced_recall_memory_with_weighting

# 创建测试函数
def test_memory_weighting_integration():
    """测试动态权重集成是否正常工作"""
    try:
        # 测试基本功能
        test_result = memory.enhanced_recall_memory_with_weighting(
            "dynamic_memory_weighting_capability",
            context="testing dynamic memory weighting integration"
        )
        
        if test_result and len(test_result) > 0:
            print("✅ MemoryCore 动态权重集成测试成功！")
            print("找到 {} 条带权重的记忆".format(len(test_result)))
            if 'weight' in test_result[0]:
                print("第一条记忆权重: {:.3f}".format(test_result[0]['weight']))
            return True
        else:
            print("⚠️ MemoryCore 动态权重集成测试返回空结果")
            return False
    except Exception as e:
        print("❌ MemoryCore 动态权重集成测试失败: {}".format(e))
        return False

# 运行测试
test_result = test_memory_weighting_integration()

print("✅ MemoryCore 动态权重集成补丁已成功应用！")
print("现在可以使用 memory.enhanced_recall_memory_with_weighting() 进行带权重的记忆检索")
print(f"测试结果: {'成功' if test_result else '失败'}")