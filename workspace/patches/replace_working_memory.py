# patch_purpose: 替换全局工作记忆对象为基于重要性的实现

# 从之前的补丁导入WorkingMemoryCompatibleDict类
from working_memory_importance_based import WorkingMemoryCompatibleDict

# 创建新的工作记忆实例
new_working_memory = WorkingMemoryCompatibleDict(max_size=200)

# 替换全局的工作记忆对象
global _working_memory
_working_memory = new_working_memory

print("✅ 工作记忆已替换为基于重要性的实现")