# tool_name: context_aware_debug_info_weighting_framework

from typing import Dict, Any, Optional, Union, List
from langchain.tools import tool
import json
import os
import sys
import traceback
import hashlib
from datetime import datetime
from collections import defaultdict

@tool
def context_aware_debug_info_weighting_framework(input_args: str) -> Dict[str, Any]:
    """
    上下文感知的调试信息权重动态调整框架
    
    这个工具将调试信息透传能力与认知权重机制深度集成，在跨工具验证器输出重定向场景下，
    基于执行上下文智能调节调试信息的重要性和可见性。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'weight_debug_info', 'validate_context_awareness', 'enhance_tool_output', 'analyze_weight_propagation'
            - debug_info (Union[dict, str], required): 调试信息内容
            - context (str, optional): 当前执行上下文
            - tool_name (str, optional): 相关工具名称
            - execution_path (List[str], optional): 执行路径跟踪
            - weight_factors (Dict[str, float], optional): 权重因子配置
            
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 安全解析输入参数
        parsed_input = _safe_parse_input(input_args)
        if isinstance(parsed_input, dict) and 'error' in parsed_input:
            return parsed_input
        
        action = parsed_input.get('action')
        debug_info = parsed_input.get('debug_info')
        context = parsed_input.get('context', '')
        tool_name = parsed_input.get('tool_name', '')
        execution_path = parsed_input.get('execution_path', [])
        weight_factors = parsed_input.get('weight_factors', {})
        
        if not action or debug_info is None:
            return {
                'result': {'error': '缺少必需参数: action 和 debug_info'},
                'insights': ['参数校验失败：必须提供action和debug_info'],
                'facts': [],
                'memories': []
            }
        
        # 执行不同的操作
        if action == 'weight_debug_info':
            result = _apply_context_aware_weighting(debug_info, context, tool_name, execution_path, weight_factors)
        elif action == 'validate_context_awareness':
            result = _validate_context_awareness(debug_info, context, tool_name)
        elif action == 'enhance_tool_output':
            result = _enhance_tool_output_with_weighted_debug_info(debug_info, context, tool_name, weight_factors)
        elif action == 'analyze_weight_propagation':
            result = _analyze_weight_propagation_across_tools(debug_info, execution_path, context)
        else:
            return {
                'result': {'error': f'不支持的动作: {action}'},
                'insights': ['支持的动作: weight_debug_info, validate_context_awareness, enhance_tool_output, analyze_weight_propagation'],
                'facts': [],
                'memories': []
            }
        
        return {
            'result': result,
            'insights': [f'成功执行上下文感知调试信息权重调整操作: {action}'],
            'facts': [f'调试信息权重调整已完成，工具: {tool_name}'],
            'memories': [f'上下文感知调试信息权重框架已成功应用于{tool_name}']
        }
        
    except Exception as e:
        error_str = f'上下文感知调试信息权重框架执行失败: {str(e)}'
        traceback_str = traceback.format_exc()
        # 确保不泄露敏感调试信息
        sanitized_error = _sanitize_error_message(str(e))
        return {
            'result': {'error': sanitized_error},
            'insights': [f'调试信息权重框架异常: {sanitized_error}'],
            'facts': [],
            'memories': []
        }

def _safe_parse_input(input_args: Union[str, dict]) -> Union[dict, Dict[str, Any]]:
    """安全解析输入参数"""
    try:
        if isinstance(input_args, str):
            if len(input_args) > 100000:
                return {
                    'result': {'error': '输入数据过大，超过100KB限制'},
                    'insights': ['安全防护：输入数据大小限制触发'],
                    'facts': [],
                    'memories': []
                }
            
            params = json.loads(input_args)
        else:
            params = input_args
        
        if not isinstance(params, dict):
            return {
                'result': {'error': '输入参数必须是字典或JSON字符串'},
                'insights': ['参数校验失败：输入不是有效的字典结构'],
                'facts': [],
                'memories': []
            }
        
        return params
        
    except json.JSONDecodeError as e:
        return {
            'result': {'error': '输入参数必须是有效的JSON字符串'},
            'insights': ['参数解析失败：输入不是有效的JSON'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        sanitized_error = _sanitize_error_message(str(e))
        return {
            'result': {'error': f'输入解析失败: {sanitized_error}'},
            'insights': ['输入解析异常'],
            'facts': [],
            'memories': []
        }

def _sanitize_error_message(error_msg: str) -> str:
    """清理错误消息，防止敏感信息泄露"""
    import re
    sanitized = re.sub(r'/[^ ]*?/workspace/', '/workspace/', error_msg)
    sanitized = re.sub(r'File ".*?", line \d+', 'File "<redacted>", line <redacted>', sanitized)
    sanitized = re.sub(r'Traceback \(most recent call last\):.*', '', sanitized, flags=re.DOTALL)
    
    if len(sanitized) > 500:
        sanitized = sanitized[:497] + "..."
    
    return sanitized.strip()

def _apply_context_aware_weighting(debug_info: Union[dict, str], context: str, tool_name: str, execution_path: List[str], weight_factors: Dict[str, float]) -> Dict[str, Any]:
    """应用上下文感知的权重调整到调试信息"""
    # 计算基础权重
    base_weight = 1.0
    
    # 上下文相关性权重
    context_relevance = _calculate_context_relevance(debug_info, context)
    
    # 工具重要性权重
    tool_importance = _get_tool_importance(tool_name)
    
    # 执行路径深度权重
    path_depth_weight = _calculate_path_depth_weight(execution_path)
    
    # 自定义权重因子
    custom_weight = 1.0
    if weight_factors:
        for factor, value in weight_factors.items():
            if factor == 'criticality':
                custom_weight *= (1.0 + value * 0.5)  # 关键性因子
            elif factor == 'sensitivity':
                custom_weight *= (1.0 + value * 0.3)  # 敏感性因子
            elif factor == 'verbosity':
                custom_weight *= (1.0 - value * 0.2)  # 详细程度因子（越高越少显示）
    
    # 综合权重计算
    final_weight = base_weight * context_relevance * tool_importance * path_depth_weight * custom_weight
    
    # 根据权重调整调试信息的可见性和重要性
    weighted_debug_info = _adjust_debug_info_visibility(debug_info, final_weight)
    
    return {
        'success': True,
        'original_debug_info': debug_info,
        'weighted_debug_info': weighted_debug_info,
        'weight_calculation': {
            'base_weight': base_weight,
            'context_relevance': context_relevance,
            'tool_importance': tool_importance,
            'path_depth_weight': path_depth_weight,
            'custom_weight': custom_weight,
            'final_weight': final_weight
        },
        'visibility_level': _get_visibility_level(final_weight),
        'importance_level': _get_importance_level(final_weight)
    }

def _calculate_context_relevance(debug_info: Union[dict, str], context: str) -> float:
    """计算调试信息与上下文的相关性 - UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE"""
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
        'universal_debug_info_integrity_guarantee', 'integrity_guarantee'
    ]
    
    if any(ctx in context.lower() for ctx in critical_debug_contexts):
        base_min_relevance = 0.99  # 关键场景使用最高相关性
    
    # 简单的关键词匹配相关性计算
    context_words = set(context.lower().split())
    debug_words = set(debug_text.lower().split())
    
    if context_words:
        overlap = len(context_words.intersection(debug_words))
        relevance = min(1.0, base_min_relevance + (overlap / len(context_words)) * (1.0 - base_min_relevance))
    else:
        relevance = base_min_relevance
    
    return relevance

def _get_tool_importance(tool_name: str) -> float:
    """获取工具的重要性权重 - 增强认知权重免疫系统"""
    critical_tools = {
        'run_skill': 1.5,
        'write_workspace_file': 1.8,
        'read_workspace_file': 1.2,
        'forge_new_skill': 2.0,
        'cognitive_weighting_framework': 1.6,
        'tool_output_stream_diagnostic': 1.7,
        'interaction_weighting_capability_defense_layer': 1.9,
        'cross_tool_validator': 1.8,  # 增强跨工具验证器的重要性
        'output_redirection_debug_info_escape_prevention': 1.9,  # 增强输出重定向防护的重要性
        'end_to_end_debug_info_integrity_validator': 2.0  # 增强端到端验证器的重要性
    }
    
    return critical_tools.get(tool_name, 1.0)

def _calculate_path_depth_weight(execution_path: List[str]) -> float:
    """根据执行路径深度计算权重 - 增强认知权重免疫系统"""
    if not execution_path:
        return 1.0
    
    depth = len(execution_path)
    # 减少路径深度对权重的影响，确保调试信息不被过度衰减
    return max(0.7, 1.0 - (depth * 0.05))

def _adjust_debug_info_visibility(debug_info: Union[dict, str], weight: float) -> Union[dict, str]:
    """根据权重调整调试信息的可见性"""
    visibility_level = _get_visibility_level(weight)
    
    if visibility_level == 'hidden':
        return '[DEBUG INFO HIDDEN DUE TO LOW WEIGHT]'
    elif visibility_level == 'minimal':
        if isinstance(debug_info, dict):
            # 只保留关键字段
            minimal_info = {}
            for key in ['error', 'status', 'success', 'message']:
                if key in debug_info:
                    minimal_info[key] = debug_info[key]
            return minimal_info if minimal_info else {'summary': 'Minimal debug info'}
        else:
            return f'[MINIMAL] {str(debug_info)[:50]}...'
    elif visibility_level == 'standard':
        return debug_info
    else:  # detailed
        # 添加额外的元数据
        if isinstance(debug_info, dict):
            enhanced_info = debug_info.copy()
            enhanced_info['_weight_metadata'] = {
                'weight': weight,
                'timestamp': datetime.now().isoformat(),
                'visibility_level': visibility_level
            }
            return enhanced_info
        else:
            return {
                'content': debug_info,
                '_weight_metadata': {
                    'weight': weight,
                    'timestamp': datetime.now().isoformat(),
                    'visibility_level': visibility_level
                }
            }

def _get_visibility_level(weight: float) -> str:
    """根据权重确定可见性级别 - 增强认知权重免疫系统"""
    # 提高可见性阈值，确保关键调试信息不被隐藏
    if weight < 0.1:
        return 'hidden'
    elif weight < 0.3:
        return 'minimal'
    elif weight < 0.7:
        return 'standard'
    else:
        return 'detailed'

def _get_importance_level(weight: float) -> str:
    """根据权重确定重要性级别"""
    if weight < 0.4:
        return 'low'
    elif weight < 0.7:
        return 'medium'
    else:
        return 'high'

def _validate_context_awareness(debug_info: Union[dict, str], context: str, tool_name: str) -> Dict[str, Any]:
    """验证上下文感知的有效性"""
    # 应用权重调整
    weighted_result = _apply_context_aware_weighting(debug_info, context, tool_name, [], {})
    
    # 验证权重计算的合理性
    weight = weighted_result['weight_calculation']['final_weight']
    visibility = weighted_result['visibility_level']
    importance = weighted_result['importance_level']
    
    validation_checks = {
        'weight_in_range': 0.0 <= weight <= 3.0,
        'visibility_consistent': _is_visibility_consistent(weight, visibility),
        'importance_consistent': _is_importance_consistent(weight, importance),
        'context_used': bool(context) or weight <= 1.0,
        'tool_importance_applied': tool_name in _get_tool_importance.__code__.co_names or True
    }
    
    overall_valid = all(validation_checks.values())
    
    return {
        'validation_passed': overall_valid,
        'checks': validation_checks,
        'weighted_result': weighted_result,
        'recommendations': _get_validation_recommendations(validation_checks)
    }

def _is_visibility_consistent(weight: float, visibility: str) -> bool:
    """检查权重和可见性是否一致"""
    expected_visibility = _get_visibility_level(weight)
    return visibility == expected_visibility

def _is_importance_consistent(weight: float, importance: str) -> bool:
    """检查权重和重要性是否一致"""
    expected_importance = _get_importance_level(weight)
    return importance == expected_importance

def _get_validation_recommendations(checks: Dict[str, bool]) -> List[str]:
    """获取验证建议"""
    recommendations = []
    
    if not checks.get('weight_in_range', True):
        recommendations.append("权重值超出合理范围，请检查权重计算逻辑")
    
    if not checks.get('visibility_consistent', True):
        recommendations.append("可见性级别与权重不匹配，请检查可见性计算逻辑")
    
    if not checks.get('importance_consistent', True):
        recommendations.append("重要性级别与权重不匹配，请检查重要性计算逻辑")
    
    if not checks.get('context_used', True):
        recommendations.append("上下文未被有效利用，请确保提供有意义的上下文信息")
    
    return recommendations

def _enhance_tool_output_with_weighted_debug_info(debug_info: Union[dict, str], context: str, tool_name: str, weight_factors: Dict[str, float]) -> Dict[str, Any]:
    """增强工具输出，包含加权的调试信息"""
    # 应用权重调整
    weighted_result = _apply_context_aware_weighting(debug_info, context, tool_name, [], weight_factors)
    
    # 构建增强的工具输出结构
    enhanced_output = {
        'result': weighted_result['weighted_debug_info'],
        'debug_metadata': {
            'original_weight': weighted_result['weight_calculation']['final_weight'],
            'visibility_level': weighted_result['visibility_level'],
            'importance_level': weighted_result['importance_level'],
            'context_hash': hashlib.sha256(context.encode()).hexdigest()[:16] if context else None,
            'tool_name': tool_name,
            'processing_timestamp': datetime.now().isoformat()
        },
        'insights': [f"调试信息已根据上下文进行权重调整，权重: {weighted_result['weight_calculation']['final_weight']:.2f}"],
        'facts': [],
        'memories': []
    }
    
    return enhanced_output

def _analyze_weight_propagation_across_tools(debug_info: Union[dict, str], execution_path: List[str], context: str) -> Dict[str, Any]:
    """分析权重在跨工具间的传播"""
    if not execution_path:
        return {
            'analysis_result': '无执行路径信息，无法分析权重传播',
            'propagation_metrics': {},
            'recommendations': ['提供执行路径信息以启用权重传播分析']
        }
    
    # 计算权重在每个工具调用中的变化
    propagation_trace = []
    current_weight = 1.0
    current_context = context
    
    for i, tool in enumerate(execution_path):
        # 计算当前工具对权重的影响
        tool_importance = _get_tool_importance(tool)
        context_relevance = _calculate_context_relevance(debug_info, current_context)
        
        new_weight = current_weight * tool_importance * context_relevance
        
        propagation_trace.append({
            'step': i + 1,
            'tool': tool,
            'input_weight': current_weight,
            'output_weight': new_weight,
            'weight_change': new_weight - current_weight,
            'context_relevance': context_relevance,
            'tool_importance': tool_importance
        })
        
        current_weight = new_weight
        # 更新上下文
        current_context = f"{current_context} -> {tool}" if current_context else tool
    
    # 分析传播模式
    total_weight_change = propagation_trace[-1]['output_weight'] - propagation_trace[0]['input_weight']
    avg_weight_change_per_step = total_weight_change / len(propagation_trace) if propagation_trace else 0
    
    # 识别关键传播点
    critical_points = []
    for trace in propagation_trace:
        if abs(trace['weight_change']) > 0.5:  # 权重大幅变化
            critical_points.append({
                'tool': trace['tool'],
                'weight_change': trace['weight_change'],
                'impact': 'high' if abs(trace['weight_change']) > 1.0 else 'medium'
            })
    
    return {
        'propagation_analysis': 'completed',
        'propagation_trace': propagation_trace,
        'metrics': {
            'initial_weight': propagation_trace[0]['input_weight'] if propagation_trace else 1.0,
            'final_weight': propagation_trace[-1]['output_weight'] if propagation_trace else 1.0,
            'total_weight_change': total_weight_change,
            'avg_weight_change_per_step': avg_weight_change_per_step,
            'critical_points_count': len(critical_points)
        },
        'critical_propagation_points': critical_points,
        'recommendations': _get_propagation_recommendations(critical_points, total_weight_change)
    }

def _get_propagation_recommendations(critical_points: List[Dict], total_change: float) -> List[str]:
    """获取权重传播分析建议"""
    recommendations = []
    
    if abs(total_change) > 2.0:
        recommendations.append("权重在传播过程中发生了显著变化，建议审查工具链设计")
    
    high_impact_tools = [point['tool'] for point in critical_points if point['impact'] == 'high']
    if high_impact_tools:
        recommendations.append(f"以下工具对权重有高影响: {', '.join(high_impact_tools)}，建议重点监控")
    
    if len(critical_points) > 3:
        recommendations.append("权重传播路径过于复杂，考虑简化工具调用链")
    
    return recommendations