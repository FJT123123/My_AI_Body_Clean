# tool_name: tool_output_semantic_validator

import json
import difflib
from typing import Dict, Any, List, Optional
from langchain.tools import tool

def calculate_structure_similarity(original: Dict, repaired: Dict) -> float:
    """计算两个字典结构的相似性分数"""
    original_keys = set(original.keys())
    repaired_keys = set(repaired.keys())
    
    if not original_keys and not repaired_keys:
        return 1.0
    if not original_keys or not repaired_keys:
        return 0.0
    
    intersection = original_keys.intersection(repaired_keys)
    union = original_keys.union(repaired_keys)
    
    return len(intersection) / len(union)

def calculate_semantic_similarity(original_value: Any, repaired_value: Any) -> float:
    """计算两个值的语义相似性"""
    if type(original_value) != type(repaired_value):
        return 0.0
    
    if isinstance(original_value, str):
        if original_value == repaired_value:
            return 1.0
        else:
            # 使用序列相似度
            similarity = difflib.SequenceMatcher(None, str(original_value), str(repaired_value)).ratio()
            return similarity
    elif isinstance(original_value, (int, float)):
        if original_value == repaired_value:
            return 1.0
        else:
            # 对于数值，计算相对差异
            if original_value == 0:
                return 0.0 if repaired_value != 0 else 1.0
            diff_ratio = abs(original_value - repaired_value) / abs(original_value)
            return max(0.0, 1.0 - diff_ratio)
    elif isinstance(original_value, dict):
        return calculate_structure_similarity(original_value, repaired_value)
    elif isinstance(original_value, list):
        if len(original_value) != len(repaired_value):
            return 0.0
        if len(original_value) == 0:
            return 1.0
        
        total_similarity = 0.0
        for orig_item, rep_item in zip(original_value, repaired_value):
            total_similarity += calculate_semantic_similarity(orig_item, rep_item)
        return total_similarity / len(original_value)
    else:
        # 对于其他类型，简单比较是否相等
        return 1.0 if original_value == repaired_value else 0.0

def calculate_semantic_consistency_score(original: Dict, repaired: Dict) -> float:
    """计算整体语义一致性分数"""
    if not original and not repaired:
        return 1.0
    
    all_keys = set(original.keys()).union(set(repaired.keys()))
    if not all_keys:
        return 1.0
    
    total_similarity = 0.0
    valid_comparisons = 0
    
    for key in all_keys:
        orig_val = original.get(key)
        rep_val = repaired.get(key)
        
        if orig_val is None and rep_val is None:
            key_similarity = 1.0
        elif orig_val is None or rep_val is None:
            key_similarity = 0.0
        else:
            key_similarity = calculate_semantic_similarity(orig_val, rep_val)
        
        total_similarity += key_similarity
        valid_comparisons += 1
    
    return total_similarity / valid_comparisons if valid_comparisons > 0 else 0.0

def extract_key_metrics(output: Dict) -> Dict:
    """提取关键指标用于比较"""
    key_metrics = {}
    for key, value in output.items():
        if isinstance(value, (int, float, str, bool)) or (isinstance(value, dict) and len(value) < 10):
            key_metrics[key] = value
    return key_metrics

@tool
def tool_output_semantic_validator(input_args: str) -> Dict[str, Any]:
    """
    工具输出语义一致性回归验证器
    专门用于验证修复前后工具输出在语义层面的一致性，特别适用于视频处理等复杂多模态场景。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - original_output: 原始工具输出（字典格式）
            - repaired_output: 修复后工具输出（字典格式）
            - validation_criteria: 验证标准列表，如['structure', 'semantics', 'key_metrics']
            - tolerance_threshold: 容忍阈值（0.0-1.0，默认0.95）
            - context: 上下文信息（可选）
    
    Returns:
        Dict[str, Any]: 包含验证结果的字典，包含一致性分数、差异分析和通过/失败状态
    """
    try:
        args = json.loads(input_args)
        original_output = args.get('original_output')
        repaired_output = args.get('repaired_output')
        validation_criteria = args.get('validation_criteria', ['structure', 'semantics', 'key_metrics'])
        tolerance_threshold = args.get('tolerance_threshold', 0.95)
        context = args.get('context', {})
        
        # 参数验证
        if not isinstance(original_output, dict) or not isinstance(repaired_output, dict):
            return {
                "error": "original_output and repaired_output must be dictionaries",
                "status": "error"
            }
        
        if not isinstance(validation_criteria, list):
            return {
                "error": "validation_criteria must be a list",
                "status": "error"
            }
        
        if not isinstance(tolerance_threshold, (int, float)) or not 0.0 <= tolerance_threshold <= 1.0:
            return {
                "error": "tolerance_threshold must be a number between 0.0 and 1.0",
                "status": "error"
            }
        
        # 初始化验证结果
        validation_results = {
            "validation_criteria": validation_criteria,
            "tolerance_threshold": tolerance_threshold,
            "context": context,
            "original_output_summary": {
                "keys_count": len(original_output),
                "keys": list(original_output.keys())
            },
            "repaired_output_summary": {
                "keys_count": len(repaired_output),
                "keys": list(repaired_output.keys())
            },
            "consistency_scores": {},
            "differences": {},
            "overall_score": 0.0,
            "passed": False
        }
        
        total_score = 0.0
        criteria_count = 0
        
        # 结构一致性验证
        if 'structure' in validation_criteria:
            structure_score = calculate_structure_similarity(original_output, repaired_output)
            validation_results["consistency_scores"]["structure"] = structure_score
            
            # 计算结构差异
            orig_keys = set(original_output.keys())
            rep_keys = set(repaired_output.keys())
            validation_results["differences"]["structure"] = {
                "missing_in_repaired": list(orig_keys - rep_keys),
                "extra_in_repaired": list(rep_keys - orig_keys)
            }
            
            total_score += structure_score
            criteria_count += 1
        
        # 语义一致性验证
        if 'semantics' in validation_criteria:
            semantic_score = calculate_semantic_consistency_score(original_output, repaired_output)
            validation_results["consistency_scores"]["semantics"] = semantic_score
            
            # 计算语义差异
            semantic_diffs = {}
            all_keys = set(original_output.keys()).union(set(repaired_output.keys()))
            for key in all_keys:
                orig_val = original_output.get(key)
                rep_val = repaired_output.get(key)
                
                if orig_val != rep_val:
                    semantic_diffs[key] = {
                        "original": orig_val,
                        "repaired": rep_val
                    }
            validation_results["differences"]["semantics"] = semantic_diffs
            
            total_score += semantic_score
            criteria_count += 1
        
        # 关键指标匹配验证
        if 'key_metrics' in validation_criteria:
            orig_metrics = extract_key_metrics(original_output)
            rep_metrics = extract_key_metrics(repaired_output)
            
            metrics_score = calculate_semantic_consistency_score(orig_metrics, rep_metrics)
            validation_results["consistency_scores"]["key_metrics"] = metrics_score
            
            # 计算关键指标差异
            metrics_diffs = {}
            all_metric_keys = set(orig_metrics.keys()).union(set(rep_metrics.keys()))
            for key in all_metric_keys:
                orig_val = orig_metrics.get(key)
                rep_val = rep_metrics.get(key)
                
                if orig_val != rep_val:
                    metrics_diffs[key] = {
                        "original": orig_val,
                        "repaired": rep_val
                    }
            validation_results["differences"]["key_metrics"] = metrics_diffs
            
            total_score += metrics_score
            criteria_count += 1
        
        # 计算整体分数
        if criteria_count > 0:
            overall_score = total_score / criteria_count
            validation_results["overall_score"] = overall_score
            validation_results["passed"] = overall_score >= tolerance_threshold
        else:
            validation_results["overall_score"] = 1.0
            validation_results["passed"] = True
        
        # 总结验证结果
        validation_results["status"] = "passed" if validation_results["passed"] else "failed"
        validation_results["message"] = f"Validation {'passed' if validation_results['passed'] else 'failed'} with overall score {validation_results['overall_score']:.4f}"
        
        return validation_results
    
    except json.JSONDecodeError as e:
        return {
            "error": f"Invalid JSON in input_args: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error during validation: {str(e)}",
            "status": "error"
        }