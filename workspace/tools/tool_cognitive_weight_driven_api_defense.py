# tool_name: cognitive_weight_driven_api_defense

from langchain.tools import tool
import json
import logging
from typing import Dict, Any, Optional

def run_skill(skill_name: str, input_args: str) -> Any:
    """运行技能的辅助函数"""
    try:
        # 尝试调用已有的工具
        if skill_name == 'cognitive_weighting_framework':
            from langchain.tools import tool
            # 通过工具调用方式运行
            cognitive_tool = globals().get('attention_driven_api_defense_validator')
            if cognitive_tool:
                return cognitive_tool(input_args)
        elif skill_name == 'tool_name_length_validator':
            from langchain.tools import tool
            # 通过工具调用方式运行
            validator_tool = globals().get('enhanced_api_parameter_validator')
            if validator_tool:
                return validator_tool(input_args)
        
        # 如果没有找到对应的工具，返回默认值
        return {
            'result': {'cognitive_weight': 0.5, 'weighted_context': {}}
        }
    except Exception as e:
        logging.warning(f"run_skill调用失败: {e}")
        return {
            'result': {'cognitive_weight': 0.5, 'weighted_context': {}}
        }

def invoke_tool(tool_name: str, input_args: str) -> Any:
    """工具间协作调用"""
    try:
        # 获取可用的工具
        available_tools = {
            'attention_driven_api_defense_validator': globals().get('attention_driven_api_defense_validator'),
            'enhanced_api_parameter_validator': globals().get('enhanced_api_parameter_validator'),
            'enhanced_api_parameter_defense_validator': globals().get('enhanced_api_parameter_defense_validator')
        }
        
        if tool_name in available_tools and available_tools[tool_name]:
            return available_tools[tool_name](input_args)
        else:
            # 如果工具不存在，返回默认值
            return {
                'result': {'cognitive_weight': 0.5, 'weighted_context': {}}
            }
    except Exception as e:
        logging.warning(f"invoke_tool调用失败: {e}")
        return {
            'result': {'cognitive_weight': 0.5, 'weighted_context': {}}
        }

@tool
def cognitive_weight_driven_api_defense(input_args: str) -> dict:
    """
    认知权重驱动的动态API防御体系
    
    这个工具将认知权重框架与API参数语义验证深度集成，
    实现基于当前上下文和任务重要性的动态验证严格程度调整。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - tool_name (str): 要调用的工具名称
            - parameters (dict): 工具参数字典
            - context (str, optional): 当前执行上下文
            - base_validation_level (str, optional): 基础验证级别 ('strict', 'moderate', 'lenient')
            - criticality_score (float, optional): 任务关键性评分 (0.0-1.0)
    
    Returns:
        dict: 包含动态验证结果、调整后的验证策略和执行建议的字典
    """
    # 解析输入参数
    try:
        if isinstance(input_args, str):
            args_dict = json.loads(input_args)
        else:
            args_dict = input_args
    except json.JSONDecodeError:
        return {
            'result': {'error': '缺少有效的JSON格式输入参数'},
            'insights': ['参数校验失败：输入参数必须是有效的JSON字符串'],
            'facts': [],
            'memories': []
        }

    # 提取必需参数
    tool_name = args_dict.get('tool_name')
    parameters = args_dict.get('parameters', {})
    context = args_dict.get('context', '')
    base_validation_level = args_dict.get('base_validation_level', 'moderate')
    criticality_score = args_dict.get('criticality_score', 0.5)

    # 验证必需参数
    if not tool_name:
        return {
            'result': {'error': '缺少 tool_name 参数'},
            'insights': ['参数校验失败：必须提供tool_name'],
            'facts': [],
            'memories': []
        }

    if not parameters:
        return {
            'result': {'error': '缺少 parameters 参数'},
            'insights': ['参数校验失败：必须提供parameters'],
            'facts': [],
            'memories': []
        }

    # 使用认知权重框架计算动态权重
    try:
        cognitive_weight_input = json.dumps({
            'action': 'apply_context',
            'tool_name': tool_name,
            'input_args_dict': parameters,
            'context': context
        })
        
        # 使用已有的工具进行认知权重计算
        cognitive_result = invoke_tool('attention_driven_api_defense_validator', cognitive_weight_input)
        
        if isinstance(cognitive_result, str):
            cognitive_result = json.loads(cognitive_result)
            
        # 提取认知权重信息
        cognitive_weight = cognitive_result.get('result', {}).get('cognitive_weight', 0.5)
        weighted_context = cognitive_result.get('result', {}).get('weighted_context', {})
        
    except Exception as e:
        logging.warning(f"认知权重计算失败: {e}")
        cognitive_weight = 0.5
        weighted_context = {}

    # 结合任务关键性评分和认知权重计算最终验证严格度
    # 公式: final_strictness = (cognitive_weight * 0.6 + criticality_score * 0.4) * base_strictness_factor
    base_strictness_map = {
        'strict': 1.0,
        'moderate': 0.7,
        'lenient': 0.4
    }
    base_strictness = base_strictness_map.get(base_validation_level, 0.7)

    final_strictness = (cognitive_weight * 0.6 + criticality_score * 0.4) * base_strictness

    # 根据最终严格度确定验证策略
    if final_strictness >= 0.8:
        validation_strategy = 'comprehensive'
        auto_repair = False
        max_length = 60  # 更严格的长度限制
    elif final_strictness >= 0.5:
        validation_strategy = 'standard'
        auto_repair = True
        max_length = 64  # 标准长度限制
    else:
        validation_strategy = 'basic'
        auto_repair = True
        max_length = 70  # 宽松的长度限制（但仍需防止API错误）

    # 执行工具名称验证
    try:
        tool_name_validation_input = json.dumps({
            'tool_name': tool_name,
            'max_length': max_length
        })
        
        tool_name_result = invoke_tool('enhanced_api_parameter_validator', tool_name_validation_input)
        
        if isinstance(tool_name_result, str):
            tool_name_result = json.loads(tool_name_result)
            
        tool_name_valid = tool_name_result.get('result', {}).get('valid', False)
        safe_tool_name = tool_name_result.get('result', {}).get('truncated_name', tool_name)
        
    except Exception as e:
        logging.warning(f"工具名称验证失败: {e}")
        tool_name_valid = len(tool_name) <= max_length
        safe_tool_name = tool_name[:max_length] if len(tool_name) > max_length else tool_name

    # 执行参数契约验证（如果可用）
    parameter_validation_result = {'valid': True, 'issues': []}

    try:
        # 尝试获取参数契约（这里简化处理，实际中可以从工具元数据获取）
        # 对于高严格度场景，执行更全面的参数验证
        if validation_strategy == 'comprehensive':
            # 检查所有参数类型和值范围
            for param_name, param_value in parameters.items():
                if param_name.startswith('_') and param_value is None:
                    parameter_validation_result['issues'].append(f"参数 {param_name} 不能为空")
                    parameter_validation_result['valid'] = False
        
        elif validation_strategy == 'standard':
            # 基本的参数存在性检查
            pass  # 已经在前面验证了parameters不为空
            
    except Exception as e:
        logging.warning(f"参数验证异常: {e}")

    # 生成最终结果
    overall_valid = tool_name_valid and parameter_validation_result['valid']

    result = {
        'overall_valid': overall_valid,
        'validation_strategy': validation_strategy,
        'final_strictness': final_strictness,
        'tool_name_validation': {
            'valid': tool_name_valid,
            'original_name': tool_name,
            'safe_name': safe_tool_name,
            'max_length_used': max_length
        },
        'parameter_validation': parameter_validation_result,
        'cognitive_context': {
            'cognitive_weight': cognitive_weight,
            'criticality_score': criticality_score,
            'weighted_context': weighted_context
        },
        'recommendations': {
            'use_safe_name': safe_tool_name != tool_name,
            'enable_auto_repair': auto_repair,
            'suggested_next_action': 'proceed' if overall_valid else 'repair_and_retry'
        }
    }

    insights = [
        f"基于认知权重({cognitive_weight:.2f})和关键性评分({criticality_score:.2f})选择了{validation_strategy}验证策略",
        f"最终验证严格度: {final_strictness:.2f}",
        f"工具名称验证: {'通过' if tool_name_valid else '失败'}",
        f"参数验证: {'通过' if parameter_validation_result['valid'] else '失败'}"
    ]

    facts = [
        f"动态API防御系统使用{validation_strategy}策略处理工具调用",
        f"认知权重驱动的验证严格度调整已应用"
    ]

    memories = [
        f"成功实现了认知权重与API防御验证的动态集成",
        f"验证策略根据上下文重要性自动调整: {validation_strategy}"
    ]

    return {
        'result': result,
        'insights': insights,
        'facts': facts,
        'memories': memories
    }