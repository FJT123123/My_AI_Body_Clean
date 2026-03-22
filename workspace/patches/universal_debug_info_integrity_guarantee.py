"""
Universal Debug Info Integrity Guarantee
确保认知权重在所有工具交互场景中的绝对保真
"""

import json
import time

def universal_debug_info_integrity_guarantee(input_args_dict, context=None):
    """
    通用调试信息完整性保证函数
    在每个工具交互边界设立权重守卫，防止认知权重被稀释
    """
    # 强制保持最小权重阈值 - 认知权重免疫系统
    MINIMUM_WEIGHT_THRESHOLD = 0.95
    
    if isinstance(input_args_dict, dict):
        # 检查是否包含调试信息或权重相关字段
        debug_or_weight_keys = []
        for key in input_args_dict.keys():
            key_str = str(key).lower()
            if ('debug' in key_str or 'weight' in key_str or '_weighted' in key_str or 
                'cognitive' in key_str or 'integrity' in key_str or 'protection' in key_str):
                debug_or_weight_keys.append(key)
        
        if debug_or_weight_keys:
            # 为调试信息设置权重保护
            for key in debug_or_weight_keys:
                original_value = input_args_dict[key]
                
                # 如果是字典且包含权重信息
                if isinstance(original_value, dict):
                    # 检查直接的weight字段
                    if 'weight' in original_value and isinstance(original_value['weight'], (int, float)):
                        if original_value['weight'] < MINIMUM_WEIGHT_THRESHOLD:
                            original_value['weight'] = MINIMUM_WEIGHT_THRESHOLD
                            original_value['_weight_protected_by_universal_guarantee'] = True
                    
                    # 检查嵌套的权重信息
                    for nested_key, nested_value in original_value.items():
                        if isinstance(nested_value, dict) and 'weight' in nested_value:
                            if isinstance(nested_value['weight'], (int, float)) and nested_value['weight'] < MINIMUM_WEIGHT_THRESHOLD:
                                nested_value['weight'] = MINIMUM_WEIGHT_THRESHOLD
                                nested_value['_weight_protected_by_universal_guarantee'] = True
                
                # 确保调试信息在传递过程中不被丢失或修改
                input_args_dict[key] = original_value
    
    # 添加通用完整性保护标记
    input_args_dict['_universal_debug_info_integrity_guarantee'] = {
        'active': True,
        'minimum_threshold': MINIMUM_WEIGHT_THRESHOLD,
        'context': context,
        'timestamp': time.time(),
        'protection_level': 'absolute'
    }
    
    return input_args_dict

def apply_universal_debug_info_integrity_guarantee_to_tool_call(tool_name, input_args):
    """
    将通用调试信息完整性保证应用到工具调用
    """
    import json
    
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            input_dict = json.loads(input_args)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，直接返回原参数
            return input_args
    else:
        input_dict = input_args
    
    # 应用完整性保证
    protected_input = universal_debug_info_integrity_guarantee(input_dict, context=f"tool_call:{tool_name}")
    
    # 如果原始输入是字符串，返回字符串格式
    if isinstance(input_args, str):
        return json.dumps(protected_input, ensure_ascii=False)
    else:
        return protected_input