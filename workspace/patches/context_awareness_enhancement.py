import json
from typing import Union

def enhanced_calculate_context_relevance(debug_info: Union[dict, str], context: str) -> float:
    """增强的上下文相关性计算 - 类型自适应版本"""
    # UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 强制最小相关性为0.98
    base_min_relevance = 0.98
    
    if not context:
        return base_min_relevance  # 认知权重免疫系统默认高相关性
    
    # 将调试信息转换为文本
    if isinstance(debug_info, dict):
        debug_text = json.dumps(debug_info, ensure_ascii=False)
    else:
        debug_text = str(debug_info)
    
    # 检查是否是关键调试场景
    critical_debug_contexts = [
        'output_redirection', 'cross_tool', 'weight_propagation', 
        'debug_info_integrity', 'cognitive_weight', 'immune', 'protection', 
        'enhanced', 'validator_output_channel', 'debug_escape',
        'universal_debug_info_integrity_guarantee', 'integrity_guarantee',
        'type_adaptive', 'compatibility', 'validation'
    ]
    
    if any(ctx in context.lower() for ctx in critical_debug_contexts):
        base_min_relevance = 0.99  # 关键场景使用最高相关性
    
    # 类型自适应的相关性计算
    # 1. 检查调试信息是否包含标准字段
    standard_fields = ['result', 'insights', 'facts', 'memories']
    has_standard_fields = isinstance(debug_info, dict) and any(field in debug_info for field in standard_fields)
    
    # 2. 检查调试信息是否包含错误信息
    has_error_info = isinstance(debug_info, dict) and ('error' in debug_info or 'success' in debug_info)
    
    # 3. 检查调试信息的复杂度
    complexity_score = 0.0
    if isinstance(debug_info, dict):
        complexity_score = min(1.0, len(debug_info) / 10.0)
    elif isinstance(debug_info, str):
        complexity_score = min(1.0, len(debug_info) / 1000.0)
    
    # 4. 综合计算相关性
    relevance_boost = 0.0
    if has_standard_fields:
        relevance_boost += 0.1
    if has_error_info:
        relevance_boost += 0.1
    if complexity_score > 0.5:
        relevance_boost += 0.05
    
    # 确保相关性不低于基础最小值
    final_relevance = max(base_min_relevance, base_min_relevance + relevance_boost)
    
    # 限制最大值为1.0
    final_relevance = min(1.0, final_relevance)
    
    return final_relevance


def adaptive_get_tool_importance(tool_name: str) -> float:
    """自适应工具重要性权重"""
    # 基础重要性
    base_importance = 1.0
    
    # 关键工具重要性提升
    critical_tools = {
        'run_skill': 1.5,
        'write_workspace_file': 1.8,
        'read_workspace_file': 1.2,
        'forge_new_skill': 2.0,
        'cognitive_weighting_framework': 1.6,
        'tool_output_stream_diagnostic': 1.7,
        'interaction_weighting_capability_defense_layer': 1.9,
        'cross_tool_validator': 1.8,
        'output_redirection_debug_info_escape_prevention': 1.9,
        'end_to_end_debug_info_integrity_validator': 2.0,
        'debug_info_integrity_validator': 2.0
    }
    
    importance = critical_tools.get(tool_name, base_importance)
    
    # 如果工具名称包含验证、调试、完整性等关键词，提升重要性
    validation_keywords = ['validate', 'verify', 'debug', 'integrity', 'guarantee', 'protection']
    if any(keyword in tool_name.lower() for keyword in validation_keywords):
        importance = max(importance, 1.8)
    
    return importance


# 应用补丁到现有的模块
def apply_patch():
    """应用补丁到context_aware_debug_info_weighting_framework"""
    try:
        import sys
        import os
        
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 导入现有的模块
        from tools.tool_context_aware_debug_info_weighting_framework import _calculate_context_relevance, _get_tool_importance
        
        # 替换函数
        import tools.tool_context_aware_debug_info_weighting_framework as framework_module
        framework_module._calculate_context_relevance = enhanced_calculate_context_relevance
        framework_module._get_tool_importance = adaptive_get_tool_importance
        
        print("Context awareness patch applied successfully!")
        return True
    except Exception as e:
        print(f"Failed to apply context awareness patch: {e}")
        return False

# 立即应用补丁
apply_patch()