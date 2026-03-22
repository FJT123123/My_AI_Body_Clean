# Dynamic Weight Compensation Mechanism Patch
# This patch fixes the missing 're' import issue and implements dynamic weight compensation

import re
import json
from typing import Dict, Any, Union

def apply_dynamic_weight_compensation(debug_info: Union[Dict, str], context: str, tool_name: str, minimum_threshold: float = 0.98) -> Dict[str, Any]:
    """
    动态权重补偿机制 - 防止跨工具边界调试信息权重衰减
    
    Args:
        debug_info: 调试信息字典或JSON字符串
        context: 当前执行上下文
        tool_name: 目标工具名称
        minimum_threshold: 最小权重阈值
        
    Returns:
        补偿后的调试信息字典
    """
    # 确保debug_info是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            debug_info = {"content": debug_info}
    elif not isinstance(debug_info, dict):
        debug_info = {"content": str(debug_info)}
    
    # 获取当前权重
    current_weight = debug_info.get('weight', 1.0)
    
    # 如果权重低于阈值，应用补偿
    if current_weight < minimum_threshold:
        # 基于上下文相关性和工具重要性计算补偿因子
        context_relevance = calculate_context_relevance(context, tool_name)
        tool_importance = get_tool_importance(tool_name)
        
        # 动态补偿公式：确保权重不低于阈值
        compensation_factor = max(minimum_threshold / current_weight, 1.0)
        new_weight = min(current_weight * compensation_factor, 1.0)
        
        # 应用补偿
        debug_info['weight'] = new_weight
        debug_info['compensation_applied'] = True
        debug_info['original_weight'] = current_weight
        debug_info['context_relevance'] = context_relevance
        debug_info['tool_importance'] = tool_importance
        
    return debug_info

def calculate_context_relevance(context: str, tool_name: str) -> float:
    """计算上下文与工具的相关性"""
    if not context:
        return 0.5
    
    # 使用正则表达式检查工具名是否在上下文中
    pattern = re.compile(r'\b' + re.escape(tool_name) + r'\b', re.IGNORECASE)
    if pattern.search(str(context)):
        return 1.0
    
    # 检查工具名的部分匹配
    tool_parts = tool_name.split('_')
    matches = sum(1 for part in tool_parts if re.search(r'\b' + re.escape(part) + r'\b', str(context), re.IGNORECASE))
    if matches > 0:
        return 0.8
    
    return 0.5

def get_tool_importance(tool_name: str) -> float:
    """获取工具重要性级别"""
    critical_tools = [
        'weighted_recall_my_memories', 
        'context_aware_debug_info_weighting_framework',
        'end_to_end_debug_info_integrity_validator',
        'debug_info_integrity_validator',
        'output_redirection_debug_info_escape_prevention'
    ]
    
    high_importance_tools = [
        'cross_tool_weight_propagation_validator',
        'dynamic_memory_weighting_validator',
        'tool_output_semantic_validator'
    ]
    
    if tool_name in critical_tools:
        return 1.0
    elif tool_name in high_importance_tools:
        return 0.9
    else:
        return 0.7

# Integration function to be used by debug_info_integrity_validator
def integrate_weight_compensation(original_result: Dict[str, Any], context: str, tool_name: str) -> Dict[str, Any]:
    """
    将动态权重补偿集成到验证结果中
    """
    if 'result' in original_result and isinstance(original_result['result'], dict):
        # Apply compensation to the result's debug info
        compensated_result = apply_dynamic_weight_compensation(
            original_result['result'], 
            context, 
            tool_name
        )
        original_result['result'] = compensated_result
        
        # Add compensation metadata
        if 'insights' not in original_result:
            original_result['insights'] = []
        original_result['insights'].append(f"动态权重补偿已应用于工具 {tool_name}")
    
    return original_result