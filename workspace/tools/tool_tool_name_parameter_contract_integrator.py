# tool_name: tool_name_parameter_contract_integrator
from langchain.tools import tool
import json
import re

def _validate_tool_name(tool_name, max_length=64):
    """验证工具名称是否符合API约束"""
    result = {
        'valid': True,
        'original_name': tool_name,
        'safe_tool_name': tool_name,
        'errors': [],
        'warnings': []
    }
    
    # 长度检查
    if len(tool_name) > max_length:
        result['valid'] = False
        result['errors'].append(f"工具名称长度 {len(tool_name)} 超过最大限制 {max_length}")
        # 截断并清理
        safe_name = tool_name[:max_length]
        safe_name = re.sub(r'[^a-zA-Z0-9_]+$', '', safe_name)
        if not safe_name:
            safe_name = "safe_tool"
        result['safe_tool_name'] = safe_name
    
    # 字符检查
    if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
        result['valid'] = False
        result['errors'].append("工具名称只能包含字母、数字和下划线")
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', tool_name)
        safe_name = re.sub(r'_+', '_', safe_name).strip('_')
        if not safe_name:
            safe_name = "safe_tool"
        if len(safe_name) > max_length:
            safe_name = safe_name[:max_length].rstrip('_')
            if not safe_name:
                safe_name = "safe_tool"
        result['safe_tool_name'] = safe_name
    
    # 最佳实践警告
    if len(tool_name) > 30:
        result['warnings'].append("工具名称超过30字符，建议缩短以留出扩展空间")
    
    return result

def _validate_parameters(parameters, contract):
    """验证参数是否符合契约"""
    result = {'valid': True, 'errors': [], 'missing_required': []}
    
    if not contract:
        return result
    
    for param_name, param_def in contract.items():
        required = param_def.get('required', False)
        param_type = param_def.get('type', 'any')
        
        if required and param_name not in parameters:
            result['valid'] = False
            result['missing_required'].append(param_name)
            result['errors'].append(f"缺少必需参数: {param_name}")
    
    return result

@tool
def tool_name_parameter_contract_integrator(input_args: str) -> dict:
    """
    工具名称与参数契约集成验证工具：将工具名称视为参数契约的延伸，提供统一的防御框架。
    
    Args:
        input_args (str): JSON字符串，包含:
            - action: "integrate_validation" (默认)
            - tool_name: 工具名称
            - parameters: 参数字典
            - parameter_contract: 参数契约
            - max_length: 最大长度限制 (默认64)
    
    Returns:
        dict: 包含整体验证结果、工具名称验证结果、参数验证结果等信息
    """
    try:
        args = json.loads(input_args) if isinstance(input_args, str) else input_args
    except Exception as e:
        return {"error": "无效的JSON输入", "valid": False, "exception": str(e)}
    
    action = args.get('action', 'integrate_validation')
    
    if action == 'integrate_validation':
        tool_name = args.get('tool_name', '')
        parameters = args.get('parameters', {})
        contract = args.get('parameter_contract', {})
        max_length = args.get('max_length', 64)
        
        # 验证工具名称
        name_result = _validate_tool_name(tool_name, max_length)
        
        # 验证参数
        param_result = _validate_parameters(parameters, contract)
        
        # 统一结果
        overall_valid = name_result['valid'] and param_result['valid']
        
        return {
            'overall_valid': overall_valid,
            'tool_name_validation': name_result,
            'parameter_validation': param_result,
            'suggested_tool_name': name_result['safe_tool_name'] if not name_result['valid'] else None,
            'missing_parameters': param_result['missing_required'] if not param_result['valid'] else None
        }
    
    return {"error": f"不支持的操作: {action}", "valid": False}