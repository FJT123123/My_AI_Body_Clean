# tool_name: cognitive_weighting_framework

from typing import Dict, Any
from langchain.tools import tool
import json
import os
import sys
import traceback

@tool
def cognitive_weighting_framework(input_args: str) -> Dict[str, Any]:
    """
    统一的认知权重框架工具，将动态记忆权重机制深度集成到所有工具交互契约中
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'apply_context', 'validate_parameters', 'enhance_tool_call'
            - tool_name (str, required): 目标工具名称
            - input_args_dict (dict, required): 工具输入参数字典
            - context (str, optional): 当前上下文
            
    Returns:
        dict: 包含处理结果的字典
    """
    try:
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        action = params.get('action')
        tool_name = params.get('tool_name')
        input_args_dict = params.get('input_args_dict', {})
        context = params.get('context', None)
        
        if not action or not tool_name:
            return {
                'result': {'error': '缺少必需参数: action 和 tool_name'},
                'insights': ['参数校验失败：必须提供action和tool_name'],
                'facts': [],
                'memories': []
            }
        
        # 导入动态记忆权重能力
        from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
        dynamic_weighting = DynamicMemoryWeightingCapability()
        
        if action == 'apply_context':
            # 应用加权上下文到工具调用
            if context:
                weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                    context, 
                    context=context,
                    apply_weighting=True
                )
            else:
                # 从输入参数中提取关键词
                keywords = []
                for key, value in input_args_dict.items():
                    if isinstance(value, str) and len(value) > 3:
                        words = value.split()
                        keywords.extend([word for word in words if len(word) > 3])
                keywords = list(set(keywords))[:10]
                
                if keywords:
                    weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                        " ".join(keywords),
                        context=" ".join(keywords),
                        apply_weighting=True
                    )
                else:
                    weighted_memories = []
            
            enhanced_args = input_args_dict.copy()
            enhanced_args['_weighted_context'] = {
                'memories': weighted_memories[:5],
                'context': context,
                'tool_name': tool_name
            }
            
            result = {
                'success': True,
                'enhanced_args': enhanced_args,
                'memory_count': len(weighted_memories)
            }
            
        elif action == 'validate_parameters':
            # 验证工具参数
            validation_result = {
                'valid': True,
                'warnings': [],
                'suggestions': [],
                'confidence_score': 1.0,
                'DEBUG_MARKER': 'validate_parameters_executed'
            }
            
            # 工具名称长度验证和安全生成（预防性防御）
            # 简单长度检查调试
            validation_result['debug_tool_name_length'] = len(tool_name)
            if len(tool_name) > 64:
                validation_result['valid'] = False
                validation_result['warnings'].append(f"工具名称长度 {len(tool_name)} 超过64字符限制")
                validation_result['confidence_score'] = 0.0
                validation_result['truncated_name'] = tool_name[:64]
                validation_result['safe_tool_name'] = tool_name[:64]
            else:
                validation_result['safe_tool_name'] = tool_name
                if len(tool_name) > 30:
                    validation_result['warnings'].append(f"工具名称长度 {len(tool_name)} 超过30字符最佳实践")
            
            # 检查必需参数
            required_params = _get_required_parameters(tool_name)
            missing_params = []
            
            for param in required_params:
                if param not in input_args_dict or not input_args_dict[param]:
                    missing_params.append(param)
            
            if missing_params:
                validation_result['valid'] = False
                validation_result['warnings'].append(f"缺少必需参数: {', '.join(missing_params)}")
                validation_result['confidence_score'] = 0.0
            
            # 使用记忆权重提供智能建议
            if input_args_dict:
                context_str = " ".join(str(v) for v in input_args_dict.values() if isinstance(v, str))
                if context_str:
                    weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                        context_str[:100],
                        context=context_str[:100],
                        apply_weighting=True
                    )
                    
                    high_weight_memories = [m for m in weighted_memories if m.get('weight', 0) > 0.3]
                    if high_weight_memories:
                        suggestions = _extract_suggestions_from_memories(high_weight_memories, tool_name)
                        validation_result['suggestions'].extend(suggestions)
            
            result = validation_result
            
        elif action == 'enhance_tool_call':
            # 完整的工具调用增强流程
            # 先验证参数
            validation_result = {
                'valid': True,
                'warnings': [],
                'suggestions': [],
                'confidence_score': 1.0
            }
            
            # 工具名称长度验证和安全生成（预防性防御）
            safe_name_result = _generate_safe_tool_name(tool_name, max_length=64, best_practice_length=30)
            if not safe_name_result['valid']:
                validation_result['valid'] = False
                validation_result['warnings'].append(safe_name_result['recommendation'])
                validation_result['confidence_score'] = 0.0
                validation_result['truncated_name'] = safe_name_result['truncated_name']
                validation_result['safe_tool_name'] = safe_name_result['truncated_name']
            else:
                validation_result['safe_tool_name'] = safe_name_result['safe_name']
                if safe_name_result['recommendation']:
                    validation_result['warnings'].append(safe_name_result['recommendation'])
            
            required_params = _get_required_parameters(tool_name)
            missing_params = []
            
            for param in required_params:
                if param not in input_args_dict or not input_args_dict[param]:
                    missing_params.append(param)
            
            if missing_params:
                validation_result['valid'] = False
                validation_result['warnings'].append(f"缺少必需参数: {', '.join(missing_params)}")
                validation_result['confidence_score'] = 0.0
            
            # 应用加权上下文
            if context:
                weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                    context, 
                    context=context,
                    apply_weighting=True
                )
            else:
                keywords = []
                for key, value in input_args_dict.items():
                    if isinstance(value, str) and len(value) > 3:
                        words = value.split()
                        keywords.extend([word for word in words if len(word) > 3])
                keywords = list(set(keywords))[:10]
                
                if keywords:
                    weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                        " ".join(keywords),
                        context=" ".join(keywords),
                        apply_weighting=True
                    )
                else:
                    weighted_memories = []
            
            enhanced_args = input_args_dict.copy()
            enhanced_args['_weighted_context'] = {
                'memories': weighted_memories[:5],
                'context': context,
                'tool_name': tool_name
            }
            
            result = {
                'success': True,
                'validation': validation_result,
                'enhanced_args': enhanced_args,
                'memory_count': len(weighted_memories)
            }
            
        else:
            return {
                'result': {'error': f'不支持的动作: {action}'},
                'insights': ['支持的动作: apply_context, validate_parameters, enhance_tool_call'],
                'facts': [],
                'memories': []
            }
        
        return {
            'result': result,
            'insights': [f'成功执行认知权重框架操作: {action}'],
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
        error_str = f'认知权重框架执行失败: {str(e)}'
        traceback_str = traceback.format_exc()
        return {
            'result': {'error': error_str},
            'insights': [f'认知权重框架异常: {str(e)}', f'Traceback: {traceback_str}'],
            'facts': [],
            'memories': []
        }

def _get_required_parameters(tool_name: str) -> list:
    """获取工具的必需参数列表"""
    tool_param_map = {
        'weighted_recall_my_memories': ['keyword'],
        'run_skill': ['skill_name'],
        'read_workspace_file': ['filename'],
        'write_workspace_file': ['filename', 'content'],
        'forge_new_skill': ['description'],
        'cognitive_weighting_framework': ['action', 'tool_name']
    }
    return tool_param_map.get(tool_name, [])

def _extract_suggestions_from_memories(memories: list, tool_name: str) -> list:
    """从高权重记忆中提取建议"""
    suggestions = []
    for memory in memories[:3]:
        content = str(memory.get('Target', '') or memory.get('content', ''))
        if 'error' in content.lower() or 'missing' in content.lower():
            suggestions.append(f"注意: 相关记忆中提到可能的问题: {content[:100]}...")
    return suggestions

def _generate_safe_tool_name(base_name: str, max_length: int = 64, best_practice_length: int = 30) -> dict:
    """
    生成安全的工具名称，确保符合长度限制
    
    Args:
        base_name: 基础工具名称
        max_length: 最大允许长度（硬性限制，默认64）
        best_practice_length: 最佳实践长度（建议限制，默认30）
    
    Returns:
        dict: 包含原始名称、安全名称、是否截断、建议等信息
    """
    import re
    
    # 确保只包含合法字符
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
    
    result = {
        'original_name': base_name,
        'safe_name': safe_name,
        'needs_truncation': False,
        'truncated_name': safe_name,
        'recommendation': '',
        'valid': True
    }
    
    if len(safe_name) > max_length:
        result['needs_truncation'] = True
        result['truncated_name'] = safe_name[:max_length]
        result['valid'] = False
        result['recommendation'] = f"工具名称超过{max_length}字符限制，使用截断版本: '{safe_name[:max_length]}'"
    elif len(safe_name) > best_practice_length:
        result['recommendation'] = f"工具名称较长 ({len(safe_name)} 字符)，建议保持在{best_practice_length}字符以内"
    else:
        result['recommendation'] = f"工具名称 '{safe_name}' 符合所有要求"
    
    return result