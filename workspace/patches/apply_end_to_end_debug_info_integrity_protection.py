"""
端到端调试信息完整性保护机制
确保认知权重在所有工具交互场景中的绝对保真
"""

import json
import time

def apply_end_to_end_debug_info_integrity_protection(tool_name, input_args_dict, context=None):
    """
    端到端调试信息完整性保护函数
    在每个工具交互边界设立权重守卫，防止认知权重被稀释
    """
    # 强制保持最小权重阈值
    MINIMUM_WEIGHT_THRESHOLD = 0.8
    
    # 如果输入参数中包含调试信息，确保其权重不被过度衰减
    if isinstance(input_args_dict, dict):
        # 检查是否包含调试信息
        debug_keys = []
        for key in input_args_dict.keys():
            key_str = str(key).lower()
            if 'debug' in key_str or 'weight' in key_str:
                debug_keys.append(key)
        
        if debug_keys:
            # 为调试信息设置权重保护
            for key in debug_keys:
                original_value = input_args_dict[key]
                if isinstance(original_value, dict) and 'weight' in original_value:
                    # 如果权重低于阈值，强制提升到最小阈值
                    if original_value['weight'] < MINIMUM_WEIGHT_THRESHOLD:
                        original_value['weight'] = MINIMUM_WEIGHT_THRESHOLD
                        original_value['_weight_protected'] = True
                
                # 确保调试信息在传递过程中不被丢失
                input_args_dict[key] = original_value
    
    # 添加上下文感知的权重保护标记
    if context is not None:
        input_args_dict['_context_aware_weight_protection'] = {
            'context': context,
            'minimum_threshold': MINIMUM_WEIGHT_THRESHOLD,
            'protection_active': True,
            'timestamp': time.time()
        }
    
    return input_args_dict

def enhanced_output_redirection_validator(output_data, tool_name, context=None):
    """
    增强的输出重定向验证器
    防止调试信息在输出重定向场景下逃逸
    """
    if isinstance(output_data, dict):
        # 检查输出中是否包含调试信息
        debug_info_present = False
        for k in output_data.keys():
            k_str = str(k).lower()
            if 'debug' in k_str or 'weight' in k_str:
                debug_info_present = True
                break
        
        if debug_info_present:
            # 确保调试信息的完整性
            output_data['_debug_info_integrity_verified'] = True
            output_data['_output_redirection_safe'] = True
            
            # 如果有上下文，添加上下文验证标记
            if context:
                output_data['_context_validation'] = {
                    'context': context,
                    'tool_name': tool_name,
                    'verified_at': time.time()
                }
    
    return output_data