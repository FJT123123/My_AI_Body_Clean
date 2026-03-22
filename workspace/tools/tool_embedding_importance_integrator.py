# tool_name: embedding_importance_integrator
from langchain.tools import tool
import json
import math

@tool
def embedding_importance_integrator(input_args):
    """
    嵌入重要性集成工具
    
    这个工具将重要性权重概念扩展到嵌入向量层面，
    实现基于认知重要性的语义相似性计算。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str): 执行的动作 ('integrate_embedding_importance', 'analyze_similarity')
            - embeddings (list, optional): 嵌入向量列表
            - weights (list, optional): 权重列表
            
    Returns:
        dict: 包含集成结果和分析结果的字典
    """
    # 解析输入参数
    if isinstance(input_args, str):
        params = json.loads(input_args)
    else:
        params = input_args
        
    action = params.get('action', 'integrate_embedding_importance')
    embeddings = params.get('embeddings', [])
    weights = params.get('weights', [])
    
    # 初始化结果
    result = {
        'success': True,
        'action_performed': action,
        'insights': [],
        'facts': [],
        'memories': []
    }
    
    try:
        if action == 'integrate_embedding_importance':
            # 将重要性权重集成到嵌入向量
            if not embeddings or not weights:
                raise ValueError("需要提供embeddings和weights参数")
                
            weighted_embeddings = _apply_importance_to_embeddings(embeddings, weights)
            result['weighted_embeddings'] = weighted_embeddings
            result['insights'].append("成功将重要性权重集成到嵌入向量中")
            
        elif action == 'analyze_similarity':
            # 基于认知重要性的语义相似性分析
            if not embeddings or not weights:
                raise ValueError("需要提供embeddings和weights参数")
                
            similarity_matrix = _compute_weighted_similarity(embeddings, weights)
            result['similarity_matrix'] = similarity_matrix
            result['insights'].append("成功计算基于认知重要性的语义相似性")
            
        else:
            raise ValueError(f"不支持的动作: {action}")
            
        # 添加通用事实
        result['facts'].append("重要性权重已成功扩展到嵌入向量层面")
        result['facts'].append("语义相似性计算现在可以受益于认知重要性的指导")
        
        # 添加记忆点
        result['memories'].append("嵌入重要性集成机制已实现")
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        result['insights'].append(f"操作失败: {str(e)}")
        
    return result

def _apply_importance_to_embeddings(embeddings, weights):
    """将重要性权重应用到嵌入向量"""
    if not embeddings or not weights:
        return embeddings
        
    # 确保权重和嵌入数量匹配
    min_len = min(len(embeddings), len(weights))
    embeddings = embeddings[:min_len]
    weights = weights[:min_len]
    
    # 将权重归一化到[0.5, 1.5]范围，避免过度放大或缩小
    weight_min, weight_max = min(weights), max(weights)
    if weight_max > weight_min:
        normalized_weights = [0.5 + (w - weight_min) / (weight_max - weight_min) for w in weights]
    else:
        normalized_weights = [1.0] * len(weights)
    
    # 应用权重到嵌入向量
    weighted_embeddings = []
    for emb, weight in zip(embeddings, normalized_weights):
        weighted_emb = [dim * weight for dim in emb]
        weighted_embeddings.append(weighted_emb)
        
    return weighted_embeddings

def _compute_weighted_similarity(embeddings, weights):
    """计算基于权重的语义相似性"""
    if not embeddings or not weights:
        # 返回空矩阵
        return []
        
    # 确保权重和嵌入数量匹配
    min_len = min(len(embeddings), len(weights))
    embeddings = embeddings[:min_len]
    weights = weights[:min_len]
    
    # 计算基础余弦相似性
    similarity_matrix = []
    for i, emb1 in enumerate(embeddings):
        row = []
        for j, emb2 in enumerate(embeddings):
            # 计算点积
            dot_product = sum(a * b for a, b in zip(emb1, emb2))
            
            # 计算范数
            norm1 = math.sqrt(sum(a * a for a in emb1))
            norm2 = math.sqrt(sum(b * b for b in emb2))
            
            # 计算余弦相似度
            if norm1 == 0 or norm2 == 0:
                cosine_sim = 0.0
            else:
                cosine_sim = dot_product / (norm1 * norm2)
            
            # 应用权重调整
            weighted_sim = cosine_sim * weights[i] * weights[j]
            row.append(weighted_sim)
        similarity_matrix.append(row)
    
    # 确保对角线为1（自身相似性）
    for i in range(len(similarity_matrix)):
        if i < len(similarity_matrix[i]):
            similarity_matrix[i][i] = 1.0
    
    return similarity_matrix