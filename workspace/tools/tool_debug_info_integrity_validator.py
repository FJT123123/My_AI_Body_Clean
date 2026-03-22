# tool_name: debug_info_integrity_validator

from typing import Dict, Any, List, Optional, Union
from langchain.tools import tool
import json
import os
import sys
import traceback
import hashlib
from datetime import datetime
from collections import defaultdict

def invoke_tool(tool_name: str, input_args: str) -> Dict[str, Any]:
    """运行时工具调用接口"""
    import importlib
    import sys
    import os
    
    # 确保 workspace 目录在 Python 路径中
    current_dir = os.path.dirname(__file__)
    workspace_dir = os.path.join(current_dir, '..')
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)
    
    try:
        # 尝试从 tools 目录导入
        tool_module = importlib.import_module(f"tools.tool_{tool_name}")
        tool_func = getattr(tool_module, tool_name)
        return tool_func(input_args)
    except Exception as e:
        # 如果失败，尝试直接导入（兼容旧格式）
        try:
            tool_module = importlib.import_module(f"tool_{tool_name}")
            tool_func = getattr(tool_module, tool_name)
            return tool_func(input_args)
        except Exception as e2:
            return {"error": f"Primary import error: {str(e)}, Fallback import error: {str(e2)}", "success": False}

@tool
def debug_info_integrity_validator(input_args: str) -> Dict[str, Any]:
    """
    通用调试信息完整性保证验证器 - UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE
    
    这个工具提供深度的端到端完整性保护机制，确保调试信息在跨工具边界和高速上下文切换中的认知权重稳定性。
    它不仅防止信息逃逸，还确保调试信息的认知权重在传递过程中保持稳定和可预测。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - test_scenarios: 要测试的场景列表，如['output_redirection', 'cross_tool_boundary', 'weight_propagation']
            - tools_to_validate: 要验证的工具列表
            - context: 当前执行上下文
            - validation_criteria: 验证标准
            - enable_cognitive_weight_stability: 是否启用认知权重稳定性保证（默认True）
            - minimum_weight_threshold: 最小权重阈值（默认0.98）
            
    Returns:
        dict: 包含验证结果的字典，包括成功状态、详细结果、见解、事实和记忆
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
            
        test_scenarios = params.get('test_scenarios', ['output_redirection', 'cross_tool_boundary', 'weight_propagation'])
        tools_to_validate = params.get('tools_to_validate', [])
        context = params.get('context', 'universal_debug_info_integrity_validation')
        validation_criteria_param = params.get('validation_criteria', ['structure_preservation', 'weight_stability', 'semantic_consistency'])
        # 如果是列表，转换为默认字典格式
        if isinstance(validation_criteria_param, list):
            validation_criteria = {'completeness': 0.99, 'consistency': 0.98, 'weight_stability': 0.98}
            # 根据提供的标准调整阈值
            if 'structure_preservation' in validation_criteria_param:
                validation_criteria['completeness'] = 0.99
            if 'semantic_consistency' in validation_criteria_param:
                validation_criteria['consistency'] = 0.98
            if 'weight_stability' in validation_criteria_param:
                validation_criteria['weight_stability'] = 0.98
        else:
            validation_criteria = validation_criteria_param
        enable_cognitive_weight_stability = params.get('enable_cognitive_weight_stability', True)
        minimum_weight_threshold = params.get('minimum_weight_threshold', 0.98)
        
        results = {
            'success': True,
            'detailed_results': {},
            'insights': [],
            'facts': [],
            'memories': []
        }
        
        # UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 强制启用认知权重稳定性
        if enable_cognitive_weight_stability:
            results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 已启用认知权重稳定性保证机制")
        
        # 执行输出重定向场景测试 - 增强版
        if 'output_redirection' in test_scenarios:
            # 使用增强的输出重定向防护机制
            prevention_params = {
                'debug_info': {'tools': tools_to_validate, 'context': context},
                'context': context,
                'tool_name': tools_to_validate[0] if tools_to_validate else 'universal_validator',
                'minimum_weight_threshold': minimum_weight_threshold,
                'force_preserve_keys': ['error', 'status', 'success', 'cognitive_weight', 'debug_metadata']
            }
            
            # 使用invoke_tool调用输出重定向防护工具
            prevention_result = invoke_tool('output_redirection_debug_info_escape_prevention', json.dumps(prevention_params))
            results['detailed_results']['output_redirection'] = prevention_result
            
            if prevention_result.get('result', {}).get('success', False):
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 成功应用输出重定向防护，防止信息逃逸")
            else:
                results['success'] = False
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 输出重定向防护失败，存在信息逃逸风险")
        
        # 执行跨工具边界测试 - 增强版
        if 'cross_tool_boundary' in test_scenarios and len(tools_to_validate) >= 2:
            # 使用上下文感知调试信息权重框架进行深度验证
            weight_params = {
                'action': 'validate_context_awareness',
                'debug_info': {'tools': tools_to_validate, 'execution_path': tools_to_validate},
                'context': context,
                'tool_name': 'universal_cross_tool_validator'
            }
            
            # 使用invoke_tool调用现有工具
            weight_result = invoke_tool('context_aware_debug_info_weighting_framework', json.dumps(weight_params))
            results['detailed_results']['cross_tool_boundary'] = weight_result
            
            # UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 强制最小相关性为0.98
            if weight_result.get('result', {}).get('validation_passed', False):
                final_weight = weight_result.get('result', {}).get('weighted_result', {}).get('weight_calculation', {}).get('final_weight', 0.0)
                if final_weight >= minimum_weight_threshold:
                    results['insights'].append(f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 跨工具边界调试信息完整性验证通过，权重: {final_weight:.3f} >= {minimum_weight_threshold}")
                else:
                    results['success'] = False
                    results['insights'].append(f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 跨工具边界权重低于阈值 {final_weight:.3f} < {minimum_weight_threshold}")
            else:
                results['success'] = False
                results['insights'].append("UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 跨工具边界存在调试信息完整性问题")
        
        # 执行权重传播测试 - 增强版
        if 'weight_propagation' in test_scenarios:
            # 使用上下文感知调试信息权重框架分析权重传播
            analyze_params = {
                'action': 'analyze_weight_propagation',
                'debug_info': {'tools': tools_to_validate},
                'context': context,
                'execution_path': tools_to_validate
            }
            
            # 使用invoke_tool调用现有工具
            analyze_result = invoke_tool('context_aware_debug_info_weighting_framework', json.dumps(analyze_params))
            results['detailed_results']['weight_propagation'] = analyze_result
            
            # UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 验证权重传播稳定性
            metrics = analyze_result.get('result', {}).get('metrics', {})
            final_weight = metrics.get('final_weight', 0.0)
            initial_weight = metrics.get('initial_weight', 1.0)
            weight_stability_ratio = final_weight / initial_weight if initial_weight > 0 else 0.0
            
            if weight_stability_ratio >= validation_criteria.get('weight_stability', 0.98):
                results['insights'].append(f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 调试信息权重传播稳定，稳定性比率: {weight_stability_ratio:.3f}")
            else:
                results['success'] = False
                results['insights'].append(f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 调试信息权重传播不稳定，稳定性比率: {weight_stability_ratio:.3f} < {validation_criteria.get('weight_stability', 0.98)}")
        
        # 生成最终验证报告
        results['facts'].append(f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 端到端调试信息流完整性验证完成，测试场景: {', '.join(test_scenarios)}")
        results['memories'].append({
            'content': f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 调试信息流完整性验证结果: {'通过' if results['success'] else '失败'}",
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'guarantee_level': 'universal',
            'minimum_weight_threshold': minimum_weight_threshold
        })
        
        return results
        
    except Exception as e:
        error_str = f"UNIVERSAL DEBUG INFO INTEGRITY GUARANTEE: 端到端调试信息流完整性验证失败: {str(e)}"
        return {
            'success': False,
            'error': error_str,
            'insights': [error_str],
            'facts': [],
            'memories': []
        }