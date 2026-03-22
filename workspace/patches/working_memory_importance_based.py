# patch_purpose: 实现基于重要性的工作记忆淘汰策略

class WorkingMemoryCompatibleDict:
    """
    基于重要性的工作记忆实现，支持最多200个键。
    当超过限制时，会删除重要性最低的条目，而不是最旧的条目。
    保持与dict的兼容性。
    """
    def __init__(self, max_size=200):
        self.max_size = max_size
        self._data = {}
        self._importance = {}  # 存储每个键的重要性分数
        self._access_count = {}  # 存储每个键的访问次数
        
    def __setitem__(self, key, value):
        """设置键值对"""
        # 默认重要性为0.5
        self._data[key] = value
        self._importance[key] = 0.5
        self._access_count[key] = self._access_count.get(key, 0)
        
        # 如果超过最大大小，删除重要性最低的项
        if len(self._data) > self.max_size:
            self._evict_least_important()
            
    def __getitem__(self, key):
        """获取键值，增加访问计数"""
        if key not in self._data:
            raise KeyError(key)
            
        # 增加访问计数
        self._access_count[key] = self._access_count.get(key, 0) + 1
        
        return self._data[key]
        
    def __delitem__(self, key):
        """删除键"""
        del self._data[key]
        del self._importance[key]
        del self._access_count[key]
        
    def __contains__(self, key):
        """检查键是否存在"""
        return key in self._data
        
    def __len__(self):
        """返回当前大小"""
        return len(self._data)
        
    def __iter__(self):
        """迭代键"""
        return iter(self._data)
        
    def keys(self):
        """返回所有键"""
        return self._data.keys()
        
    def values(self):
        """返回所有值"""
        return self._data.values()
        
    def items(self):
        """返回所有键值对"""
        return self._data.items()
        
    def get(self, key, default=None):
        """安全获取值"""
        try:
            return self[key]
        except KeyError:
            return default
            
    def _evict_least_important(self):
        """删除重要性最低的项"""
        if not self._importance:
            return
            
        # 找到重要性最低的键
        least_important_key = min(self._importance, key=self._importance.get)
        
        # 删除该键
        del self._data[least_important_key]
        del self._importance[least_important_key]
        del self._access_count[least_important_key]
        
    def set_importance(self, key, importance):
        """显式设置某个键的重要性"""
        if key in self._importance:
            self._importance[key] = max(0.0, min(1.0, importance))
            
    def get_importance(self, key):
        """获取某个键的重要性"""
        return self._importance.get(key, 0.0)
        
    def clear(self):
        """清空所有数据"""
        self._data.clear()
        self._importance.clear()
        self._access_count.clear()

# 替换全局工作记忆对象
_working_memory = WorkingMemoryCompatibleDict(max_size=200)