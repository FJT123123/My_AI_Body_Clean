# tool_name: weighted_recall_my_memories

from typing import Dict, Any
from langchain.tools import tool
import json
import traceback
import sys
import os

@tool
def weighted_recall_my_memories(input_args: str) -> Dict[str, Any]:
    """
    带权重的记忆检索工具 - 与认知权重框架深度集成
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - keyword (str, required): 检索关键词
            - context (str, optional): 当前上下文，用于计算语义相关性
            - _weighted_context (dict, optional): 来自认知权重框架的加权上下文
            
    Returns:
        dict: 包含检索结果的字典
    """
    
    try:
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 导入动态记忆权重能力
        from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
        
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        keyword = params.get('keyword')
        context = params.get('context', None)
        weighted_context = params.get('_weighted_context', None)
        
        if not keyword:
            return {
                'result': {'error': '缺少 keyword 参数'},
                'insights': ['参数校验失败：必须提供keyword'],
                'facts': [],
                'memories': []
            }
        
        # 初始化动态记忆权重能力
        dynamic_weighting = DynamicMemoryWeightingCapability()
        
        # 如果有加权上下文，可以用来增强检索
        enhanced_context = context
        if weighted_context and isinstance(weighted_context, dict):
            # 从加权上下文中提取有用信息来增强当前上下文
            memories = weighted_context.get('memories', [])
            if memories and context:
                # 结合原始上下文和高权重记忆中的相关信息
                high_weight_memories = [m for m in memories if m.get('weight', 0) > 0.3]
                if high_weight_memories:
                    memory_contexts = [str(m.get('Target', '') or m.get('content', ''))[:50] 
                                     for m in high_weight_memories[:3]]
                    enhanced_context = f"{context} {' '.join(memory_contexts)}"
        
        # 执行增强版记忆检索
        weighted_results = dynamic_weighting.enhanced_recall_memory_with_weighting(
            keyword,
            context=enhanced_context,
            apply_weighting=True
        )
        
        # 安全处理 None 返回值
        if weighted_results is None:
            weighted_results = []
        elif not isinstance(weighted_results, list):
            weighted_results = []
            
        # 格式化结果
        formatted_results = []
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
        
        actual_result = {
            'success': True,
            'keyword': keyword,
            'context': context,
            'enhanced_context': enhanced_context,
            'weighted_context_used': bool(weighted_context),
            'total_results': len(weighted_results),
            'displayed_results': len(formatted_results),
            'results': formatted_results
        }
        insights = [
            f'成功检索到 {len(weighted_results)} 条相关记忆',
            f'按动态权重排序，最高权重: {formatted_results[0]["weight"] if formatted_results else 0.0}',
            f'使用了认知权重框架的加权上下文: {bool(weighted_context)}'
        ]
        
        return {
            'result': actual_result,
            'insights': insights,
            'facts': [],
            'memories': []
        }
        
    except json.JSONDecodeError as e:
        return {
            'result': {'error': '输入参数必须是有效的JSON字符串'},
            'insights': ['参数解析失败：输入不是有效的JSON'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        error_str = f'记忆检索失败: {str(e)}'
        traceback_str = traceback.format_exc()
        return {
            'result': {'error': error_str},
            'insights': [f'记忆检索异常: {str(e)}', f'Traceback: {traceback_str}'],
            'facts': [],
            'memories': []
        }