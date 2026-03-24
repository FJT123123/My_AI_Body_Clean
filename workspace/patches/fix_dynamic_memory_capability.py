"""
修复DynamicMemoryWeightingCapability的enhanced_recall_memory_with_weighting方法
"""

# 重新导入模块以确保更改生效
import importlib
import sys

# 清除模块缓存
module_name = 'capabilities.dynamic_memory_weighting_capability'
if module_name in sys.modules:
    del sys.modules[module_name]

# 重新导入
from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability

print("✅ DynamicMemoryWeightingCapability模块已重新加载")
print(f"方法存在: {hasattr(DynamicMemoryWeightingCapability, 'enhanced_recall_memory_with_weighting')}")