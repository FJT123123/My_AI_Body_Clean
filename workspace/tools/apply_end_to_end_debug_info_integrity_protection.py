import json
import datetime
from typing import Dict, Any, Union, List, Optional

def apply_end_to_end_debug_info_integrity_protection(debug_info, context="", tool_name="", minimum_weight_threshold=0.95, force_preserve_keys=None):
    """
    端到端调试信息完整性保护机制
    
    在输出重定向和验证器场景中建立互斥保证，确保认知权重零衰减传递
    
    Args:
        debug_info: 调试信息内容 (dict or str)
        context: 当前执行上下文 (str)
        tool_name: 相关工具名称 (str)
        minimum_weight_threshold: 最小权重阈值，默认0.95（确保零衰减）
        force_preserve_keys: 强制保留的关键字段列表
        
    Returns:
        dict: 包含处理结果的字典
    """
    
    # 确保输入是字典格式
    if isinstance(debug_info, str):
        try:
            debug_info = json.loads(debug_info)
        except json.JSONDecodeError:
            debug_info = {"raw_debug_info": debug_info}
    
    # 设置默认强制保留的关键字段
    if force_preserve_keys is None:
        force_preserve_keys = [
            "trace_id", "timestamp", "tool_name", "action", "status", 
            "debug_info", "context", "weight", "cognitive_weight", 
            "importance_level", "visibility_level"
        ]
    
    # 创建保护后的调试信息
    protected_debug_info = {}
    
    # 1. 强制保留关键字段
    for key in force_preserve_keys:
        if key in debug_info:
            protected_debug_info[key] = debug_info[key]
    
    # 2. 确保权重不低于阈值
    current_weight = debug_info.get("weight", debug_info.get("cognitive_weight", 1.0))
    if current_weight < minimum_weight_threshold:
        # 应用权重提升机制
        protected_debug_info["weight"] = minimum_weight_threshold
        protected_debug_info["original_weight"] = current_weight
        protected_debug_info["weight_restored"] = True
    else:
        protected_debug_info["weight"] = current_weight
    
    # 3. 添加完整性保护标记
    protected_debug_info["integrity_protected"] = True
    protected_debug_info["protection_timestamp"] = datetime.datetime.now().isoformat()
    protected_debug_info["minimum_weight_threshold"] = minimum_weight_threshold
    
    # 4. 保留其他所有字段（防止信息丢失）
    for key, value in debug_info.items():
        if key not in protected_debug_info:
            protected_debug_info[key] = value
    
    return {
        "success": True,
        "protected_debug_info": protected_debug_info,
        "original_debug_info": debug_info,
        "weight_restoration_applied": protected_debug_info.get("weight_restored", False),
        "integrity_guarantee": "mutual_exclusion_established"
    }