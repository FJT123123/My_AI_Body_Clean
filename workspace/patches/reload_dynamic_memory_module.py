import importlib
import sys

# 重新加载 dynamic_memory_weighting_capability 模块
module_name = 'capabilities.dynamic_memory_weighting_capability'
if module_name in sys.modules:
    importlib.reload(sys.modules[module_name])