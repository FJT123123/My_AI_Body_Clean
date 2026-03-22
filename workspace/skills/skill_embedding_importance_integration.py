"""
自动生成的技能模块
需求: 嵌入重要性集成技能：将重要性权重概念扩展到嵌入向量层面，实现基于认知重要性的语义相似性计算。使用纯数学计算，不依赖外部数据库。支持两种操作：1) integrate_embedding_importance - 将权重集成到嵌入向量；2) analyze_similarity - 计算基于权重的语义相似性。
生成时间: 2026-03-22 02:07:37
"""

# skill_name: embedding_importance_integration
import numpy as np
from typing import List, Dict, Any, Optional
import json

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot_product / (norm1 * norm2))

def integrate_embedding_importance(embeddings: List[List[float]], weights: List[float]) -> List[List[float]]:
    """
    将重要性权重集成到嵌入向量中
    
    Args:
        embeddings: 原始嵌入向量列表，每个向量为 float 列表
        weights: 每个向量对应的重要性权重列表
    
    Returns:
        集成权重后的嵌入向量列表
    """
    if len(embeddings) != len(weights):
        raise ValueError("嵌入向量和权重列表长度不匹配")
    
    weighted_embeddings = []
    for embedding, weight in zip(embeddings, weights):
        embedding_array = np.array(embedding)
        weighted_embedding = embedding_array * weight
        weighted_embeddings.append(weighted_embedding.tolist())
    
    return weighted_embeddings

def analyze_similarity(base_embeddings: List[List[float]], 
                      target_embeddings: List[List[float]], 
                      base_weights: List[float], 
                      target_weights: List[float]) -> Dict[str, Any]:
    """
    计算基于权重的语义相似性
    
    Args:
        base_embeddings: 基础嵌入向量列表
        target_embeddings: 目标嵌入向量列表
        base_weights: 基础向量权重列表
        target_weights: 目标向量权重列表
    
    Returns:
        包含相似性分析结果的字典
    """
    if len(base_embeddings) != len(base_weights) or len(target_embeddings) != len(target_weights):
        raise ValueError("嵌入向量和权重列表长度不匹配")
    
    # 计算原始相似性矩阵
    base_weighted = integrate_embedding_importance(base_embeddings, base_weights)
    target_weighted = integrate_embedding_importance(target_embeddings, target_weights)
    
    similarity_matrix = []
    for base_emb in base_weighted:
        row = []
        for target_emb in target_weighted:
            sim = cosine_similarity(np.array(base_emb), np.array(target_emb))
            row.append(sim)
        similarity_matrix.append(row)
    
    # 计算平均相似度
    avg_similarities = []
    for row in similarity_matrix:
        avg_similarities.append(sum(row) / len(row) if row else 0.0)
    
    # 找到最相似的配对
    all_similarities = [sim for row in similarity_matrix for sim in row]
    max_similarity = max(all_similarities) if all_similarities else 0.0
    min_similarity = min(all_similarities) if all_similarities else 0.0
    
    # 计算总体相似度（考虑权重）
    overall_similarity = sum(avg_similarities) / len(avg_similarities) if avg_similarities else 0.0
    
    return {
        'similarity_matrix': similarity_matrix,
        'average_similarities': avg_similarities,
        'overall_similarity': overall_similarity,
        'max_similarity': max_similarity,
        'min_similarity': min_similarity,
        'base_count': len(base_embeddings),
        'target_count': len(target_embeddings)
    }

def main(args=None):
    """
    嵌入重要性集成技能：将重要性权重概念扩展到嵌入向量层面，
    实现基于认知重要性的语义相似性计算。
    
    支持两种操作：
    1) integrate_embedding_importance - 将权重集成到嵌入向量
    2) analyze_similarity - 计算基于权重的语义相似性
    """
    if args is None:
        args = {}
    
    operation = args.get('operation', 'integrate_embedding_importance')
    result = None
    insights = []
    
    try:
        if operation == 'integrate_embedding_importance':
            embeddings = args.get('embeddings', [])
            weights = args.get('weights', [])
            
            if not embeddings or not weights:
                return {
                    'result': {'error': '缺少必要的 embeddings 或 weights 参数'},
                    'insights': ['输入参数不完整'],
                    'capabilities': [],
                    'next_skills': []
                }
            
            result = integrate_embedding_importance(embeddings, weights)
            insights.append(f"成功将权重集成到 {len(embeddings)} 个嵌入向量")
            
        elif operation == 'analyze_similarity':
            base_embeddings = args.get('base_embeddings', [])
            target_embeddings = args.get('target_embeddings', [])
            base_weights = args.get('base_weights', [])
            target_weights = args.get('target_weights', [])
            
            if not base_embeddings or not target_embeddings or not base_weights or not target_weights:
                return {
                    'result': {'error': '缺少必要的相似性分析参数'},
                    'insights': ['输入参数不完整'],
                    'capabilities': [],
                    'next_skills': []
                }
            
            result = analyze_similarity(base_embeddings, target_embeddings, 
                                       base_weights, target_weights)
            overall_sim = result.get('overall_similarity', 0)
            insights.append(f"基于权重的语义相似性分析完成，总体相似度: {overall_sim:.4f}")
            
        else:
            return {
                'result': {'error': f'不支持的操作: {operation}，仅支持 integrate_embedding_importance 或 analyze_similarity'},
                'insights': ['操作类型错误'],
                'capabilities': [],
                'next_skills': []
            }
        
        return {
            'result': result,
            'insights': insights,
            'capabilities': ['embedding_importance_integration', 'semantic_similarity_analysis'],
            'next_skills': []
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'执行过程中发生错误: {str(e)}'],
            'capabilities': [],
            'next_skills': []
        }