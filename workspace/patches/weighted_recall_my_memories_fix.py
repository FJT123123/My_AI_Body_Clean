# weighted_recall_my_memories参数契约修复补丁

def apply_weighted_recall_my_memories_fix():
    """
    修复weighted_recall_my_memories工具的参数契约，使其与认知权重框架兼容
    """
    import json
    from typing import Dict, Any
    
    def fixed_weighted_recall_my_memories(input_args: str) -> Dict[str, Any]:
        """
        修复版带权重的记忆检索工具 - 符合认知权重框架集成要求
        
        Args:
            input_args (str): JSON字符串，包含以下参数:
                - keyword (str, required): 检索关键词
                - context (str, optional): 当前上下文，用于计算语义相关性
        
        Returns:
            dict: 包含检索结果的字典，直接返回结果结构（不包装在'result'键中）
        """
        try:
            # 解析输入参数
            if isinstance(input_args, str):
                params = json.loads(input_args)
            else:
                params = input_args
            
            keyword = params.get('keyword')
            context = params.get('context', None)
            
            if not keyword:
                return {
                    'success': False,
                    'error': '缺少 keyword 参数',
                    'insights': ['参数校验失败：必须提供keyword'],
                    'facts': [],
                    'memories': [],
                    'results': [],
                    'total_results': 0,
                    'displayed_results': 0
                }
            
            # 使用全局的 memory 对象
            global memory
            if hasattr(memory, 'enhanced_recall_memory_with_weighting'):
                weighted_results = memory.enhanced_recall_memory_with_weighting(
                    keyword,
                    context=context,
                    apply_weighting=True
                )
            else:
                # 回退到普通检索
                raw_results = memory.recall_memory(keyword)
                weighted_results = []
                for i, item in enumerate(raw_results or []):
                    item_copy = item.copy()
                    item_copy['weight'] = 0.5  # 默认权重
                    item_copy['time_weight'] = 0.5
                    item_copy['relevance_weight'] = 0.5
                    weighted_results.append(item_copy)
            
            # 格式化结果
            formatted_results = []
            if weighted_results:
                for i, result in enumerate(weighted_results[:10]):  # 限制显示前10个
                    weight = result.get('weight', 0.0)
                    source = result.get('Source', 'Unknown')
                    relation = result.get('Relation', 'MENTIONS')
                    target = result.get('Target', 'Unknown')
                    
                    formatted_results.append({
                        'rank': i + 1,
                        'source': source,
                        'relation': relation,
                        'target': target,
                        'weight': round(weight, 3),
                        'time_weight': round(result.get('time_weight', 0.0), 3),
                        'relevance_weight': round(result.get('relevance_weight', 0.0), 3)
                    })
            
            return {
                'success': True,
                'keyword': keyword,
                'context': context,
                'total_results': len(weighted_results) if weighted_results else 0,
                'displayed_results': len(formatted_results),
                'results': formatted_results,
                'insights': [f"成功检索到 {len(weighted_results)} 条相关记忆", f"按动态权重排序，最高权重: {max([r.get('weight', 0) for r in formatted_results], default=0)}"],
                'facts': [],
                'memories': []
            }
        
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': '输入参数必须是有效的JSON字符串',
                'insights': ['参数解析失败：输入不是有效的JSON'],
                'facts': [],
                'memories': [],
                'results': [],
                'total_results': 0,
                'displayed_results': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'weighted_recall_my_memories执行失败: {str(e)}',
                'insights': [f'weighted_recall_my_memories异常: {str(e)}'],
                'facts': [],
                'memories': [],
                'results': [],
                'total_results': 0,
                'displayed_results': 0
            }
    
    # 替换全局函数
    import sys
    
    # 获取目标命名空间（尝试当前模块，否则回退到全局命名空间）
    target = sys.modules.get(__name__)
    if target:
        target.weighted_recall_my_memories = fixed_weighted_recall_my_memories
    
    # 如果在全局命名空间中，也替换它
    if 'weighted_recall_my_memories' in globals():
        globals()['weighted_recall_my_memories'] = fixed_weighted_recall_my_memories
    else:
        # 强制注入到 globals
        globals()['weighted_recall_my_memories'] = fixed_weighted_recall_my_memories
    
    return "weighted_recall_my_memories参数契约修复完成"

# 应用修复
apply_weighted_recall_my_memories_fix()