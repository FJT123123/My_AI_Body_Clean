"""
自动生成的技能模块
需求: 创建一个统一的API参数验证层，集成工具名称长度验证、参数契约验证、自动修复机制和详细的错误诊断。这个技能应该能够处理工具名称超过64字符的情况，自动截断并提供安全名称，同时验证参数契约并提供自动修复功能。
生成时间: 2026-03-21 19:01:07
"""

# skill_name: unified_api_parameter_validation_layer

import re
import json
from typing import Dict, Any, Optional, List, Tuple

def validate_tool_name_length(tool_name: str) -> Tuple[bool, str, str]:
    """
    验证工具名称长度，超过64字符则自动截断并生成安全名称
    """
    if len(tool_name) <= 64:
        return True, tool_name, "名称长度符合要求"
    
    # 截断到64字符
    truncated_name = tool_name[:64]
    
    # 生成安全名称（移除非字母数字下划线字符）
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', truncated_name).strip('_')
    
    # 确保长度不超过64
    if len(safe_name) > 64:
        safe_name = safe_name[:64]
    
    return False, safe_name, f"原名称长度为{len(tool_name)}，已截断为安全名称: {safe_name}"

def validate_parameter_contract(params: Dict[str, Any], contract: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    验证参数契约，检查必需参数、类型、格式等
    """
    errors = []
    repaired_params = params.copy()
    
    # 检查必需参数
    required = contract.get('required', [])
    for req_param in required:
        if req_param not in params:
            errors.append(f"缺少必需参数: {req_param}")
    
    # 检查参数类型和格式
    properties = contract.get('properties', {})
    for param_name, param_spec in properties.items():
        if param_name in params:
            param_value = params[param_name]
            param_type = param_spec.get('type')
            
            # 类型检查
            if param_type == 'string' and not isinstance(param_value, str):
                errors.append(f"参数 {param_name} 预期为字符串类型，实际为 {type(param_value).__name__}")
            elif param_type == 'integer' and not isinstance(param_value, int):
                errors.append(f"参数 {param_name} 预期为整数类型，实际为 {type(param_value).__name__}")
            elif param_type == 'number' and not isinstance(param_value, (int, float)):
                errors.append(f"参数 {param_name} 预期为数字类型，实际为 {type(param_value).__name__}")
            elif param_type == 'boolean' and not isinstance(param_value, bool):
                errors.append(f"参数 {param_name} 预期为布尔类型，实际为 {type(param_value).__name__}")
            elif param_type == 'array' and not isinstance(param_value, list):
                errors.append(f"参数 {param_name} 预期为数组类型，实际为 {type(param_value).__name__}")
            elif param_type == 'object' and not isinstance(param_value, dict):
                errors.append(f"参数 {param_name} 预期为对象类型，实际为 {type(param_value).__name__}")
            
            # 格式检查
            param_format = param_spec.get('format')
            if param_format == 'email' and isinstance(param_value, str):
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', param_value):
                    errors.append(f"参数 {param_name} 格式应为邮箱")
            
            # 长度检查
            if 'minLength' in param_spec and isinstance(param_value, str):
                if len(param_value) < param_spec['minLength']:
                    errors.append(f"参数 {param_name} 长度小于最小要求 {param_spec['minLength']}")
            
            if 'maxLength' in param_spec and isinstance(param_value, str):
                if len(param_value) > param_spec['maxLength']:
                    errors.append(f"参数 {param_name} 长度超过最大限制 {param_spec['maxLength']}")
            
            # 数值范围检查
            if 'minimum' in param_spec and isinstance(param_value, (int, float)):
                if param_value < param_spec['minimum']:
                    errors.append(f"参数 {param_name} 小于最小值 {param_spec['minimum']}")
            
            if 'maximum' in param_spec and isinstance(param_value, (int, float)):
                if param_value > param_spec['maximum']:
                    errors.append(f"参数 {param_name} 超过最大值 {param_spec['maximum']}")
        
        elif param_name in contract.get('required', []):
            # 如果是必需参数但不存在
            errors.append(f"缺少必需参数: {param_name}")
    
    # 自动修复可能的错误
    for param_name, param_spec in properties.items():
        if param_name in params:
            param_value = params[param_name]
            param_type = param_spec.get('type')
            
            # 尝试类型转换
            if param_type == 'integer' and not isinstance(param_value, int):
                try:
                    repaired_params[param_name] = int(param_value)
                except (ValueError, TypeError):
                    pass  # 如果转换失败，保持原值
            elif param_type == 'number' and not isinstance(param_value, (int, float)):
                try:
                    repaired_params[param_name] = float(param_value)
                except (ValueError, TypeError):
                    pass  # 如果转换失败，保持原值
            elif param_type == 'boolean' and not isinstance(param_value, bool):
                if isinstance(param_value, str):
                    if param_value.lower() in ['true', '1', 'yes', 'on']:
                        repaired_params[param_name] = True
                    elif param_value.lower() in ['false', '0', 'no', 'off']:
                        repaired_params[param_name] = False
    
    is_valid = len(errors) == 0
    return is_valid, errors, repaired_params

def main(args=None):
    """
    创建统一的API参数验证层，集成工具名称长度验证、参数契约验证、自动修复机制和详细的错误诊断。
    验证工具名称是否超过64字符，自动截断并提供安全名称，同时验证参数契约并提供自动修复功能。
    """
    if args is None:
        args = {}
    
    # 获取输入参数
    tool_name = args.get('tool_name', '')
    params = args.get('params', {})
    contract = args.get('contract', {})
    
    # 验证工具名称长度
    name_valid, safe_name, name_message = validate_tool_name_length(tool_name)
    
    # 验证参数契约
    contract_valid, validation_errors, repaired_params = validate_parameter_contract(params, contract)
    
    # 综合结果
    overall_valid = name_valid and contract_valid
    result = {
        'is_valid': overall_valid,
        'tool_name': {
            'original': tool_name,
            'is_valid': name_valid,
            'safe_name': safe_name,
            'message': name_message
        },
        'parameter_validation': {
            'is_valid': contract_valid,
            'errors': validation_errors,
            'repaired_params': repaired_params
        }
    }
    
    # 生成诊断信息
    insights = []
    if not name_valid:
        insights.append(f"工具名称超出长度限制，已自动修复为安全名称: {safe_name}")
    if not contract_valid:
        insights.append(f"参数验证失败，共发现 {len(validation_errors)} 个错误")
        if repaired_params != params:
            insights.append("参数已自动修复，修复后的参数可用于后续处理")
    else:
        insights.append("参数验证通过，符合契约要求")
    
    return {
        'result': result,
        'insights': insights,
        'memories': [
            {
                'event_type': 'skill_executed',
                'content': f"API参数验证完成，工具名称: {tool_name}, 有效: {name_valid}, 参数验证: {contract_valid}",
                'importance': 0.7
            }
        ],
        'facts': [
            ['tool_name', 'has_safe_name', safe_name],
            ['parameter_validation', 'has_repaired_params', str(repaired_params != params)]
        ]
    }