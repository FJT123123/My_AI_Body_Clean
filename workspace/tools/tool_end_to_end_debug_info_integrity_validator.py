# tool_name: end_to_end_debug_info_integrity_validator
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from langchain.tools import tool

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

def load_capability_module(capability_name: str):
    """运行时能力模块加载接口"""
    import importlib
    try:
        capability_module = importlib.import_module(f"capability.{capability_name}")
        return capability_module
    except Exception as e:
        raise e

@tool
def end_to_end_debug_info_integrity_validator(input_args: str) -> Dict[str, Any]:
    """
    端到端调试信息流完整性验证工具
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - test_scenarios: 要测试的场景列表，如['output_redirection', 'cross_tool_boundary', 'weight_propagation']
            - tools_to_validate: 要验证的工具列表
            - context: 当前执行上下文
            - validation_criteria: 验证标准
            
    Returns:
        dict: 包含验证结果的字典，包括成功状态、详细结果、见解、事实和记忆
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
            
        test_scenarios = params.get('test_scenarios', ['output_redirection'])
        tools_to_validate = params.get('tools_to_validate', [])
        context = params.get('context', 'debug_info_integrity_validation')
        validation_criteria = params.get('validation_criteria', {'completeness': 0.95, 'consistency': 0.9})
        
        results = {
            'success': True,
            'detailed_results': {},
            'insights': [],
            'facts': [],
            'memories': []
        }
        
        # 执行输出重定向场景测试
        if 'output_redirection' in test_scenarios:
            # 使用tool_output_stream_diagnostic捕获流
            capture_params = {
                'action': 'capture_stream',
                'tool_name': tools_to_validate[0] if tools_to_validate else 'context_aware_debug_info_weighting_framework',
                'context': context
            }
            
            # 使用invoke_tool调用现有工具
            capture_result = invoke_tool('tool_output_stream_diagnostic', json.dumps(capture_params))
            results['detailed_results']['output_redirection'] = capture_result
            
            capture_status = capture_result.get('result', {}).get('status', '')
            if capture_status == 'success':
                results['insights'].append("成功捕获工具输出流，未检测到信息逃逸")
            else:
                results['success'] = False
                results['insights'].append("检测到输出重定向可能导致信息逃逸")
        
        # 执行跨工具边界测试
        if 'cross_tool_boundary' in test_scenarios and len(tools_to_validate) >= 2:
            # 使用context_aware_debug_info_weighting_framework验证跨工具调试信息
            weight_params = {
                'action': 'validate_context_awareness',
                'debug_info': {'tools': tools_to_validate},
                'context': context,
                'tool_name': 'cross_tool_validator'
            }
            
            # 使用invoke_tool调用现有工具
            weight_result = invoke_tool('context_aware_debug_info_weighting_framework', json.dumps(weight_params))
            results['detailed_results']['cross_tool_boundary'] = weight_result
            
            if weight_result.get('result', {}).get('validation_passed', False):
                results['insights'].append("跨工具边界调试信息完整性验证通过")
            else:
                results['success'] = False
                results['insights'].append("跨工具边界存在调试信息完整性问题")
        
        # 执行权重传播测试
        if 'weight_propagation' in test_scenarios:
            # 使用context_aware_debug_info_weighting_framework分析权重传播
            analyze_params = {
                'action': 'analyze_weight_propagation',
                'debug_info': {'tools': tools_to_validate},
                'context': context,
                'execution_path': tools_to_validate
            }
            
            # 使用invoke_tool调用现有工具
            analyze_result = invoke_tool('context_aware_debug_info_weighting_framework', json.dumps(analyze_params))
            results['detailed_results']['weight_propagation'] = analyze_result
            
            if analyze_result.get('result', {}).get('propagation_consistent', True):
                results['insights'].append("调试信息权重在工具间传播一致")
            else:
                results['success'] = False
                results['insights'].append("调试信息权重传播不一致")
        
        # 生成最终验证报告
        results['facts'].append(f"端到端调试信息流完整性验证完成，测试场景: {', '.join(test_scenarios)}")
        results['memories'].append({
            'content': f"调试信息流完整性验证结果: {'通过' if results['success'] else '失败'}",
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
        return results
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'insights': [f"端到端调试信息流完整性验证失败: {str(e)}"],
            'facts': [],
            'memories': []
        }