# Patch to add missing module-level functions to dynamic_memory_weighting_capability

def calculate_time_decay_weight(timestamp, current_time=None, decay_rate=0.1):
    """Calculate time decay weight for a memory"""
    from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
    capability = DynamicMemoryWeightingCapability()
    return capability.calculate_time_decay_weight(timestamp, current_time)

def calculate_semantic_similarity(text1, text2):
    """Calculate semantic similarity between two texts"""
    from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
    capability = DynamicMemoryWeightingCapability()
    return capability.calculate_semantic_similarity(text1, text2)

def cluster_similar_memories(memories, threshold=0.5):
    """Cluster similar memories (simplified implementation)"""
    # For now, just return each memory as its own cluster
    return [[memory] for memory in memories]