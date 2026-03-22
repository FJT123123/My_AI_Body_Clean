"""
修复DynamicMemoryWeightingCapability的enhanced_recall_memory_with_weighting方法
"""

# 修复导入路径
import os
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")
if WORKSPACE_DIR not in sys.path:
    sys.path.insert(0, WORKSPACE_DIR)

# 重新导入
import importlib
module_name = 'capabilities.dynamic_memory_weighting_capability'
if module_name in sys.modules:
    del sys.modules[module_name]

from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability

print("✅ DynamicMemoryWeightingCapability模块已重新加载")
print(f"方法存在: {hasattr(DynamicMemoryWeightingCapability, 'enhanced_recall_memory_with_weighting')}")