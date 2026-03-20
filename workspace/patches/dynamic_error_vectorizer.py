# 动态错误语义向量化补丁（集成版）
# 为现有的自我修复协调器添加基于语义向量的错误分类能力
# 修复了两个关键问题：
# 1. 将 enhanced_classify_error_with_semantics 函数注入到全局命名空间
# 2. 使用单例模式避免模型重复初始化的性能问题

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Optional

class DynamicErrorVectorizerSingleton:
    """动态错误语义向量化单例类，避免重复初始化模型"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DynamicErrorVectorizerSingleton, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        if not self._initialized:
            self.model = SentenceTransformer(model_name)
            self.error_type_vectors = {}
            self.similarity_threshold = 0.7
            self._initialized = True
            # 初始化已知错误类型
            self._initialize_error_types()
    
    def _initialize_error_types(self):
        """初始化已知错误类型及其示例"""
        self.add_error_type("dependency_missing", [
            "No module named", "ModuleNotFoundError", "command not found", 
            "ImportError", "failed to import", "dependency missing",
            "cannot import name", "No command found", "FileNotFoundError"
        ])
        self.add_error_type("parameter_error", [
            "missing required", "缺少必需", "invalid parameter", 
            "参数验证失败", "required field missing", "argument required",
            "缺少字段", "missing argument", "required parameter"
        ])
        self.add_error_type("path_error", [
            "file not found", "directory does not exist", "path does not exist",
            "文件不存在", "目录不存在", "路径无效", "no such file"
        ])
        
    def add_error_type(self, error_type: str, examples: List[str]):
        """添加新的错误类型及其示例消息"""
        if not examples:
            return
            
        # 计算该错误类型的平均向量
        vectors = self.model.encode(examples)
        avg_vector = np.mean(vectors, axis=0)
        self.error_type_vectors[error_type] = avg_vector
        
    def vectorize_error(self, error_message: str) -> np.ndarray:
        """将错误消息转换为向量"""
        return self.model.encode([error_message])[0]
        
    def classify_error(self, error_message: str) -> Tuple[str, float]:
        """分类错误消息，返回最匹配的错误类型和置信度"""
        if not self.error_type_vectors:
            return "unknown_error", 0.0
            
        error_vector = self.vectorize_error(error_message)
        best_match = "unknown_error"
        best_similarity = 0.0
        
        for error_type, type_vector in self.error_type_vectors.items():
            similarity = np.dot(error_vector, type_vector) / (
                np.linalg.norm(error_vector) * np.linalg.norm(type_vector)
            )
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = error_type
                
        if best_similarity < self.similarity_threshold:
            return "unknown_error", 0.0
            
        return best_match, best_similarity

def enhanced_classify_error_with_semantics(error_info):
    """增强版错误分类函数，结合语义向量化（单例模式）"""
    # 首先处理不同类型的error_info输入
    if isinstance(error_info, dict):
        error_message = error_info.get('error_message', '')
    elif isinstance(error_info, str):
        error_message = error_info
    else:
        error_message = str(error_info)
    
    if not error_message.strip():
        return 'unknown_error'
    
    # 使用单例模式的向量化器进行分类
    vectorizer = DynamicErrorVectorizerSingleton()
    error_type, confidence = vectorizer.classify_error(error_message)
    return error_type

# 将函数注入到全局命名空间，确保在 skill_self_healing_coordinator 中可以调用
import builtins
builtins.enhanced_classify_error_with_semantics = enhanced_classify_error_with_semantics

# 同时也确保在当前模块的全局命名空间中可用
globals()['enhanced_classify_error_with_semantics'] = enhanced_classify_error_with_semantics

# 为了确保在所有上下文中都可用，也尝试注入到 __main__ 模块
try:
    import __main__
    __main__.enhanced_classify_error_with_semantics = enhanced_classify_error_with_semantics
except:
    pass

print("✅ enhanced_classify_error_with_semantics 已成功注入到全局命名空间")
print("✅ 使用单例模式避免了模型重复初始化的性能问题")

# 测试函数
def test_dynamic_error_classification():
    """测试动态错误分类功能"""
    test_cases = [
        ("No module named 'requests'", "dependency_missing"),
        ("缺少必需参数 'input_file'", "parameter_error"),
        ("文件不存在: /tmp/nonexistent.txt", "path_error"),
        ("This is a completely unknown error message", "unknown_error")
    ]
    
    results = []
    for error_msg, expected_type in test_cases:
        predicted_type = enhanced_classify_error_with_semantics(error_msg)
        results.append({
            'error_message': error_msg,
            'expected_type': expected_type,
            'predicted_type': predicted_type,
            'match': expected_type == predicted_type
        })
    
    return results