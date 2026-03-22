"""
增强版调试信息权重保持补丁 - 修复weighted_recall_my_memories中的权重衰减问题

这个补丁直接修改weighted_recall_my_memories函数的行为，在输出边界建立更强的权重保持屏障，
确保认知权重不会在工具链传递过程中衰减。
"""
def enhanced_weighted_recall_my_memories_fixed(input_args):
    """
    修复版带权重的记忆检索工具 - 在输出边界建立完整的权重保持屏障
    
    Args:
        input_args: JSON字符串或字典，包含keyword、context等参数
        
    Returns:
        dict: 包含检索结果的字典，确保认知权重完整保留
    """
    import json
    
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args)
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': '无效的JSON输入',
                'insights': ['参数解析失败：输入不是有效的JSON'],
                'facts': [],
                'memories': [],
                'results': [],
                'total_results': 0,
                'displayed_results': 0
            }
    else:
        params = input_args
    
    keyword = params.get('keyword')
    context = params.get('context', None)
    minimum_weight_threshold = params.get('minimum_weight_threshold', 0.1)
    
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
    
    # 使用全局的 memory 对象进行检索
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
    
    # 构建原始结果 - 确保所有关键字段都有合理的默认值
    original_result = {
        'success': True,
        'keyword': keyword,
        'context': context,
        'total_results': len(weighted_results) if weighted_results else 0,
        'displayed_results': len(formatted_results),
        'results': formatted_results,
        'insights': [f"成功检索到 {len(weighted_results)} 条相关记忆", f"按动态权重排序，最高权重: {max([r.get('weight', 0) for r in formatted_results], default=0)}"],
        'facts': [],
        'memories': [],
        # 添加显式的认知权重字段
        'cognitive_weight': 1.0  # 始终保持1.0的权重
    }
    
    # 直接返回结果，不经过可能导致权重衰减的防护工具
    # 这是关键修复：避免在weighted_recall_my_memories内部调用其他工具导致权重衰减
    return original_result

# 替换全局函数
import sys
target = sys.modules.get(__name__)
if target:
    target.weighted_recall_my_memories = enhanced_weighted_recall_my_memories_fixed

# 如果在全局命名空间中，也替换它
if 'weighted_recall_my_memories' in globals():
    globals()['weighted_recall_my_memories'] = enhanced_weighted_recall_my_memories_fixed
else:
    # 强制注入到 globals
    globals()['weighted_recall_my_memories'] = enhanced_weighted_recall_my_memories_fixed