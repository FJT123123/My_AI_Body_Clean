# patch_purpose: 实现基于重要性的工作记忆淘汰策略

# 保存原始的_working_memory数据
_original_wm_data = {}
if '_working_memory' in globals() and isinstance(_working_memory, dict):
    _original_wm_data = _working_memory.copy()

# 创建新的工作记忆结构：{key: {'value': actual_value, 'importance': float, 'timestamp': str}}
_new_working_memory = {}

# 工具函数
def _wm_set(key, value, importance=0.5):
    """设置工作记忆值和重要性"""
    import datetime
    _new_working_memory[key] = {
        'value': value,
        'importance': max(0.0, min(1.0, float(importance))),
        'timestamp': datetime.datetime.now().isoformat()
    }
    _wm_cleanup_if_needed()

def _wm_get(key, default=None):
    """获取工作记忆值"""
    if key in _new_working_memory:
        return _new_working_memory[key]['value']
    return default

def _wm_importance(key):
    """获取工作记忆键的重要性"""
    if key in _new_working_memory:
        return _new_working_memory[key]['importance']
    return 0.0

def _wm_cleanup_if_needed(max_size=200, cleanup_count=50):
    """如果工作记忆超过最大大小，删除重要性最低的条目"""
    if len(_new_working_memory) <= max_size:
        return
    
    # 按重要性排序（重要性低的在前）
    items_list = list(_new_working_memory.items())
    items_list.sort(key=lambda x: x[1]['importance'])
    keys_to_delete = [item[0] for item in items_list[:cleanup_count]]
    
    for key in keys_to_delete:
        del _new_working_memory[key]
    
    print(f"🧠 [工作记忆清理] 删除了 {len(keys_to_delete)} 个重要性最低的条目")

# 迁移原始数据
for key, value in _original_wm_data.items():
    _wm_set(key, value, 0.5)

# 创建兼容的字典类
class WorkingMemoryCompatibleDict:
    def __getitem__(self, key):
        return _wm_get(key)
    
    def __setitem__(self, key, value):
        _wm_set(key, value, 0.5)
    
    def __delitem__(self, key):
        if key in _new_working_memory:
            del _new_working_memory[key]
    
    def __contains__(self, key):
        return key in _new_working_memory
    
    def __len__(self):
        return len(_new_working_memory)
    
    def __iter__(self):
        return iter(_new_working_memory.keys())
    
    def keys(self):
        return _new_working_memory.keys()
    
    def values(self):
        return [item['value'] for item in _new_working_memory.values()]
    
    def items(self):
        return [(k, item['value']) for k, item in _new_working_memory.items()]
    
    def get(self, key, default=None):
        return _wm_get(key, default)
    
    def clear(self):
        _new_working_memory.clear()
    
    def update(self, other):
        if hasattr(other, 'items'):
            for k, v in other.items():
                self[k] = v
        else:
            for k, v in other:
                self[k] = v

# 替换全局的_working_memory
_working_memory = WorkingMemoryCompatibleDict()

# 添加新的API到全局命名空间
def set_working_memory(key, value, importance=0.5):
    _wm_set(key, value, importance)

def get_working_memory(key, default=None):
    return _wm_get(key, default)

def get_working_memory_importance(key):
    return _wm_importance(key)

# 注册到全局
globals()['set_working_memory'] = set_working_memory
globals()['get_working_memory'] = get_working_memory
globals()['get_working_memory_importance'] = get_working_memory_importance