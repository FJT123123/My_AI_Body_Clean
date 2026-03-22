"""
修复 DynamicMemoryWeightingCapability 的数据库路径问题
直接设置正确的数据库路径
"""

import os

# 直接设置数据库路径为 workspace/v3_episodic_memory.db
correct_db_path = "workspace/v3_episodic_memory.db"

try:
    from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
    
    # 保存原始的 __init__ 方法
    original_init = DynamicMemoryWeightingCapability.__init__
    
    # 创建新的 __init__ 方法
    def fixed_init(self, memory_db_path=None, lock=None):
        if memory_db_path is None:
            memory_db_path = correct_db_path
        return original_init(self, memory_db_path, lock)
    
    # 替换 __init__ 方法
    DynamicMemoryWeightingCapability.__init__ = fixed_init
    print(f"✅ 已修复 DynamicMemoryWeightingCapability 数据库路径: {correct_db_path}")
except Exception as e:
    print(f"⚠️ 修复 DynamicMemoryWeightingCapability 时出错: {e}")