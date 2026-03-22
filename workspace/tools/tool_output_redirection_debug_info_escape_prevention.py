# tool_name: output_redirection_debug_info_escape_prevention

import json
import os
from typing import Dict, Any, List, Union
from langchain.tools import tool

def _extract_debug_weight(debug_info: Dict[str, Any]) -> float:
    """从调试信息中提取权重值"""
    # 尝试从不同可能的位置提取权重
    weight_paths = [
        "weight_calculation.final_weight",
        "final_weight", 
        "weight", 
        "importance_level",
        "visibility_level"
    ]
    
    for path in weight_paths:
        try:
            current = debug_info
            for key in path.split('.'):
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    raise KeyError(f"Key {key} not found")
            
            if isinstance(current, (int, float)) and 0 <= current <= 1:
                return float(current)
        except (KeyError, TypeError, ValueError):
            continue
    
    # 如果找不到明确的权重，检查weighted_debug_info结构
    if "weighted_debug_info" in debug_info:
        weighted_info = debug_info["weighted_debug_info"]
        if isinstance(weighted_info, dict):
            # 根据内容推断权重
            if "summary" in weighted_info and weighted_info["summary"] == "Minimal debug info":
                return 0.1  # minimal级别通常对应低权重
            elif "summary" in weighted_info and weighted_info["summary"] == "Full debug info":
                return 1.0  # full级别对应高权重
    
    # 默认返回1.0（假设完整信息）
    return 1.0

def _apply_weight_compensation(debug_info: Dict[str, Any], 
                              target_weight: float, 
                              preserve_keys: List[str]) -> Dict[str, Any]:
    """应用权重补偿机制"""
    # 创建调试信息的副本
    compensated_info = _deep_copy_dict(debug_info)
    
    # 强制保留关键字段
    for key in preserve_keys:
        if key in debug_info:
            compensated_info[key] = debug_info[key]
    
    # 更新权重相关信息
    if "weight_calculation" in compensated_info:
        compensated_info["weight_calculation"]["final_weight"] = target_weight
        compensated_info["weight_calculation"]["compensation_applied"] = True
    else:
        compensated_info["weight_calculation"] = {
            "final_weight": target_weight,
            "compensation_applied": True,
            "reason": "output_redirection_protection"
        }
    
    # 确保visibility_level和importance_level适当
    if "visibility_level" in compensated_info:
        compensated_info["visibility_level"] = "full" if target_weight >= 0.5 else "detailed"
    
    if "importance_level" in compensated_info:
        compensated_info["importance_level"] = "high" if target_weight >= 0.5 else "medium"
    
    # 如果存在weighted_debug_info，确保其包含完整信息
    if "weighted_debug_info" in compensated_info:
        original_debug = debug_info.get("original_debug_info", debug_info)
        compensated_info["weighted_debug_info"] = {
            "summary": "Full debug info (compensated)",
            "original_summary": compensated_info["weighted_debug_info"].get("summary", "unknown"),
            "compensated": True,
            "preserved_content": {k: v for k, v in original_debug.items() if k in preserve_keys}
        }
    
    return compensated_info

def _deep_copy_dict(obj: Dict[str, Any]) -> Dict[str, Any]:
    """深度复制字典"""
    if isinstance(obj, dict):
        return {k: _deep_copy_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_deep_copy_dict(item) for item in obj]
    else:
        return obj

@tool
def output_redirection_debug_info_escape_prevention(input_args: str) -> Dict[str, Any]:
    """
    防止输出重定向场景下调试信息逃逸的核心函数
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - debug_info: 调试信息内容 (dict or str)
            - context: 当前执行上下文 (str, optional)
            - tool_name: 相关工具名称 (str, optional)
            - minimum_weight_threshold: 最小权重阈值，默认0.1 (float, optional)
            - force_preserve_keys: 强制保留的关键字段列表 (list, optional)
    
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            try:
                params = json.loads(input_args)
            except json.JSONDecodeError:
                params = {"debug_info": input_args}
        else:
            params = input_args
        
        debug_info = params.get("debug_info", {})
        context = params.get("context", "")
        tool_name = params.get("tool_name", "unknown_tool")
        minimum_weight_threshold = params.get("minimum_weight_threshold", 0.5)  # 增强认知权重免疫系统，默认阈值提高到0.5
        force_preserve_keys = params.get("force_preserve_keys", ["error", "trace_id", "timestamp", "status", "result", "insights", "facts", "memories"])
        
        # 确保debug_info是字典格式
        if isinstance(debug_info, str):
            try:
                debug_info = json.loads(debug_info)
            except json.JSONDecodeError:
                debug_info = {"raw_debug_info": debug_info}
        
        # 检查当前调试信息的权重状态
        current_weight = _extract_debug_weight(debug_info)
        
        # 如果权重低于阈值，应用补偿机制
        if current_weight < minimum_weight_threshold:
            # 应用权重补偿
            compensated_debug_info = _apply_weight_compensation(
                debug_info, 
                minimum_weight_threshold, 
                force_preserve_keys
            )
            
            result = {
                "success": True,
                "original_debug_info": debug_info,
                "compensated_debug_info": compensated_debug_info,
                "weight_before": current_weight,
                "weight_after": minimum_weight_threshold,
                "compensation_applied": True,
                "preserved_keys": force_preserve_keys,
                "context": context,
                "tool_name": tool_name
            }
            
            insights = [
                f"检测到调试信息权重过低 ({current_weight:.3f} < {minimum_weight_threshold}), 已应用补偿机制",
                f"强制保留关键字段: {', '.join(force_preserve_keys)}",
                f"工具 {tool_name} 的调试信息完整性已恢复"
            ]
        else:
            # 权重正常，直接返回
            result = {
                "success": True,
                "original_debug_info": debug_info,
                "compensated_debug_info": debug_info,
                "weight_before": current_weight,
                "weight_after": current_weight,
                "compensation_applied": False,
                "context": context,
                "tool_name": tool_name
            }
            
            insights = [
                f"调试信息权重正常 ({current_weight:.3f} >= {minimum_weight_threshold}), 无需补偿",
                f"工具 {tool_name} 的调试信息完整性保持良好"
            ]
        
        return {
            "result": result,
            "insights": insights,
            "facts": [
                f"输出重定向调试信息逃逸防护已执行，工具: {tool_name}",
                f"最小权重阈值: {minimum_weight_threshold}"
            ],
            "memories": [
                f"在上下文 '{context}' 中成功防止了调试信息逃逸"
            ]
        }
    except Exception as e:
        return {
            "result": {
                "success": False,
                "error": str(e),
                "compensation_applied": False
            },
            "insights": [f"处理调试信息时发生错误: {str(e)}"],
            "facts": ["输出重定向调试信息逃逸防护执行失败"],
            "memories": [f"调试信息处理失败: {str(e)}"]
        }