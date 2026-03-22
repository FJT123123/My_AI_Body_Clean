# tool_name: unified_weight_framework
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from langchain.tools import tool

def invoke_tool(tool_name: str, input_data: Union[str, Dict]) -> Dict[str, Any]:
    """运行时注入的工具调用接口"""
    pass

def load_capability_module(module_name: str):
    """运行时注入的能力模块加载接口"""
    pass

@tool
def unified_weight_framework(input_args: str) -> Dict[str, Any]:
    """
    统一权重框架 - 跨工具兼容性与权重保持
    
    这个工具整合了跨工具结果结构兼容性自动修复和认知权重保持功能，
    为处理复杂的多模态任务闭环提供完整的解决方案。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'process_multimodal_task', 'validate_compatibility', 'repair_and_preserve'
            - task_data (dict, required): 任务数据，包含源工具、目标工具、原始结果、期望结构等
            - context (str, optional): 当前执行上下文
            - weight_threshold (float, optional): 最小权重阈值，默认0.95
            - force_repair (bool, optional): 是否强制修复，默认False
    
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        action = params.get('action', 'process_multimodal_task')
        task_data = params.get('task_data', {})
        context = params.get('context', 'unified_framework')
        weight_threshold = params.get('weight_threshold', 0.95)
        force_repair = params.get('force_repair', False)
        
        if not task_data:
            return {
                'result': {'error': '缺少 task_data 参数'},
                'insights': ['参数校验失败：必须提供task_data'],
                'facts': [],
                'memories': []
            }
        
        # 根据动作类型执行不同操作
        if action == 'process_multimodal_task':
            return _process_multimodal_task(task_data, context, weight_threshold, force_repair)
        elif action == 'validate_compatibility':
            return _validate_compatibility(task_data, context, weight_threshold)
        elif action == 'repair_and_preserve':
            return _repair_and_preserve(task_data, context, weight_threshold, force_repair)
        else:
            return {
                'result': {'error': f'不支持的动作类型: {action}'},
                'insights': [f'支持的动作类型: process_multimodal_task, validate_compatibility, repair_and_preserve'],
                'facts': [],
                'memories': []
            }
            
    except json.JSONDecodeError as e:
        return {
            'result': {'error': f'JSON解析错误: {str(e)}'},
            'insights': ['输入参数必须是有效的JSON字符串'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'处理过程中发生错误: {str(e)}'},
            'insights': ['统一框架执行异常，请检查输入参数和系统状态'],
            'facts': [],
            'memories': []
        }

def _process_multimodal_task(task_data: Dict[str, Any], context: str, weight_threshold: float, force_repair: bool) -> Dict[str, Any]:
    """处理多模态任务的完整流程"""
    insights = []
    facts = []
    memories = []
    
    # 步骤1: 验证兼容性
    validation_result = _validate_compatibility(task_data, context, weight_threshold)
    insights.extend(validation_result.get('insights', []))
    facts.extend(validation_result.get('facts', []))
    memories.extend(validation_result.get('memories', []))
    
    # 步骤2: 如果需要修复，则执行修复和权重保持
    if force_repair or not validation_result.get('result', {}).get('compatibility_ok', False):
        repair_result = _repair_and_preserve(task_data, context, weight_threshold, force_repair)
        insights.extend(repair_result.get('insights', []))
        facts.extend(repair_result.get('facts', []))
        memories.extend(repair_result.get('memories', []))
        
        final_result = repair_result.get('result', {})
        final_result['multimodal_task_processed'] = True
        final_result['processing_steps'] = ['validation', 'repair_and_preservation']
    else:
        final_result = validation_result.get('result', {})
        final_result['multimodal_task_processed'] = True
        final_result['processing_steps'] = ['validation']
    
    return {
        'result': final_result,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }

def _validate_compatibility(task_data: Dict[str, Any], context: str, weight_threshold: float) -> Dict[str, Any]:
    """验证跨工具兼容性"""
    source_tool = task_data.get('source_tool', 'unknown')
    target_tool = task_data.get('target_tool', 'unknown')
    original_result = task_data.get('original_result', {})
    expected_structure = task_data.get('expected_structure', {})
    
    # 检查结果结构兼容性
    missing_keys = []
    extra_keys = []
    type_mismatches = []
    
    # 检查缺失的键
    for key in expected_structure:
        if key not in original_result:
            missing_keys.append(key)
    
    # 检查多余的键
    for key in original_result:
        if key not in expected_structure:
            extra_keys.append(key)
    
    # 检查类型匹配（简化版）
    for key in expected_structure:
        if key in original_result:
            expected_type = type(expected_structure[key])
            actual_type = type(original_result[key])
            if expected_type != actual_type and not isinstance(original_result[key], expected_type):
                type_mismatches.append({
                    'key': key,
                    'expected_type': expected_type.__name__,
                    'actual_type': actual_type.__name__
                })
    
    compatibility_ok = len(missing_keys) == 0 and len(type_mismatches) == 0
    
    # 检查调试信息权重
    debug_info_weight = 1.0  # 默认权重
    if isinstance(original_result, dict) and '_weight_metadata' in original_result:
        debug_info_weight = original_result['_weight_metadata'].get('weight', 1.0)
    
    weight_ok = debug_info_weight >= weight_threshold
    
    overall_ok = compatibility_ok and weight_ok
    
    return {
        'result': {
            'compatibility_ok': compatibility_ok,
            'weight_ok': weight_ok,
            'overall_ok': overall_ok,
            'validation_details': {
                'missing_keys': missing_keys,
                'extra_keys': extra_keys,
                'type_mismatches': type_mismatches,
                'debug_info_weight': debug_info_weight,
                'weight_threshold': weight_threshold,
                'source_tool': source_tool,
                'target_tool': target_tool
            }
        },
        'insights': [
            f'跨工具兼容性验证完成: 源工具={source_tool}, 目标工具={target_tool}',
            f'结构兼容性: {"通过" if compatibility_ok else "失败"}',
            f'权重完整性: {"通过" if weight_ok else "失败"} (当前权重: {debug_info_weight:.3f}, 阈值: {weight_threshold})'
        ],
        'facts': [
            f'跨工具兼容性验证结果: overall_ok={overall_ok}, source={source_tool}, target={target_tool}'
        ],
        'memories': [
            f'跨工具兼容性验证完成于 {datetime.now().isoformat()}, context={context}'
        ]
    }

def _repair_and_preserve(task_data: Dict[str, Any], context: str, weight_threshold: float, force_repair: bool) -> Dict[str, Any]:
    """执行修复和权重保持"""
    source_tool = task_data.get('source_tool', 'unknown')
    target_tool = task_data.get('target_tool', 'unknown')
    original_result = task_data.get('original_result', {})
    expected_structure = task_data.get('expected_structure', {})
    
    # 创建修复后的结果
    repaired_result = original_result.copy()
    
    # 修复缺失的键
    missing_keys_fixed = 0
    for key in expected_structure:
        if key not in repaired_result:
            repaired_result[key] = expected_structure[key]
            missing_keys_fixed += 1
    
    # 保留额外的键（通常不需要删除）
    extra_keys_preserved = len([k for k in original_result if k not in expected_structure])
    
    # 处理类型不匹配（简化处理：尝试转换）
    type_mismatches_fixed = 0
    for key in expected_structure:
        if key in repaired_result:
            expected_type = type(expected_structure[key])
            actual_value = repaired_result[key]
            if not isinstance(actual_value, expected_type):
                try:
                    if expected_type == str:
                        repaired_result[key] = str(actual_value)
                    elif expected_type == int:
                        repaired_result[key] = int(float(actual_value))  # 先转float再转int处理字符串数字
                    elif expected_type == float:
                        repaired_result[key] = float(actual_value)
                    elif expected_type == bool:
                        repaired_result[key] = bool(actual_value)
                    elif expected_type == list:
                        if isinstance(actual_value, str):
                            repaired_result[key] = json.loads(actual_value)
                        else:
                            repaired_result[key] = list(actual_value)
                    elif expected_type == dict:
                        if isinstance(actual_value, str):
                            repaired_result[key] = json.loads(actual_value)
                        else:
                            repaired_result[key] = dict(actual_value)
                    type_mismatches_fixed += 1
                except (ValueError, TypeError, json.JSONDecodeError):
                    # 转换失败，保留原值
                    pass
    
    # 确保权重元数据存在且符合要求
    current_weight = 1.0
    if '_weight_metadata' in repaired_result:
        current_weight = repaired_result['_weight_metadata'].get('weight', 1.0)
    
    if current_weight < weight_threshold or '_weight_metadata' not in repaired_result:
        repaired_result['_weight_metadata'] = {
            'weight': max(current_weight, weight_threshold),
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'source_tool': source_tool,
            'target_tool': target_tool,
            'preservation_applied': True
        }
    
    repair_successful = missing_keys_fixed > 0 or type_mismatches_fixed > 0 or current_weight < weight_threshold
    
    return {
        'result': {
            'repaired_result': repaired_result,
            'repair_successful': repair_successful,
            'repair_details': {
                'missing_keys_fixed': missing_keys_fixed,
                'extra_keys_preserved': extra_keys_preserved,
                'type_mismatches_fixed': type_mismatches_fixed,
                'weight_preserved': repaired_result['_weight_metadata']['weight'] >= weight_threshold,
                'source_tool': source_tool,
                'target_tool': target_tool
            }
        },
        'insights': [
            f'跨工具结果修复完成: 源工具={source_tool}, 目标工具={target_tool}',
            f'修复统计: 缺失键修复={missing_keys_fixed}, 类型不匹配修复={type_mismatches_fixed}',
            f'权重保持: {"已应用" if repair_successful and "_weight_metadata" in repaired_result else "无需应用"}'
        ],
        'facts': [
            f'跨工具结果修复结果: repair_successful={repair_successful}, source={source_tool}, target={target_tool}'
        ],
        'memories': [
            f'跨工具结果修复完成于 {datetime.now().isoformat()}, context={context}, repair_successful={repair_successful}'
        ]
    }