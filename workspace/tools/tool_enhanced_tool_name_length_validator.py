# tool_name: enhanced_tool_name_length_validator
from typing import Dict, Any
import json
from langchain.tools import tool

def validate_tool_name_length(tool_name: str, max_length: int = 64) -> dict:
    """
    验证工具名称长度是否符合API约束
    
    Args:
        tool_name: 工具名称
        max_length: 最大允许长度，默认64字符
        
    Returns:
        dict: 包含验证结果的字典
    """
    if not isinstance(tool_name, str):
        return {
            'valid': False,
            'error': '工具名称必须是字符串类型',
            'original_name': tool_name,
            'safe_name': None
        }
    
    if len(tool_name) <= max_length:
        return {
            'valid': True,
            'original_name': tool_name,
            'safe_name': tool_name,
            'message': f'工具名称 "{tool_name}" 符合长度要求（≤{max_length}字符）'
        }
    
    # 自动截断生成安全名称
    safe_name = tool_name[:max_length]
    # 确保不以数字或下划线结尾（如果原名称有意义的话）
    while safe_name and (safe_name[-1].isdigit() or safe_name[-1] == '_'):
        safe_name = safe_name[:-1]
        if len(safe_name) <= max_length - 5:  # 保留一些空间
            break
    
    if not safe_name:
        safe_name = f"tool_{hash(tool_name) % 10000}"
    
    return {
        'valid': False,
        'original_name': tool_name,
        'safe_name': safe_name,
        'message': f'工具名称 "{tool_name}" 超过{max_length}字符限制，建议使用 "{safe_name}"'
    }

@tool
def enhanced_tool_name_length_validator(input_args: str = "") -> Dict[str, Any]:
    """
    增强型工具名称长度验证器 - 防止API 400错误的可靠验证工具
    
    Args:
        input_args: JSON字符串，包含tool_name和max_length参数
        
    Returns:
        dict: 包含验证结果、洞察、事实和记忆的完整结构化数据
    """
    try:
        # 参数验证
        if not input_args:
            return {
                'result': {'error': '缺少 input_args 参数'},
                'insights': ['参数校验失败：必须提供input_args'],
                'facts': [],
                'memories': []
            }
        
        try:
            params = json.loads(input_args) if isinstance(input_args, str) else input_args
        except json.JSONDecodeError:
            return {
                'result': {'error': 'input_args 必须是有效的JSON字符串'},
                'insights': ['参数解析失败：input_args格式错误'],
                'facts': [],
                'memories': []
            }
        
        tool_name = params.get('tool_name')
        max_length = params.get('max_length', 64)
        
        if not tool_name:
            return {
                'result': {'error': '缺少 tool_name 参数'},
                'insights': ['参数校验失败：必须提供tool_name'],
                'facts': [],
                'memories': []
            }
        
        result = validate_tool_name_length(tool_name, max_length)
        return {
            'result': result,
            'insights': [result.get('message', '工具名称验证完成')],
            'facts': [f"工具名称长度验证结果: {result['valid']}"],
            'memories': [f"验证了工具名称 '{tool_name}' 的长度合规性"]
        }
    except Exception as e:
        return {
            'result': {'error': f'验证过程中发生异常: {str(e)}'},
            'insights': ['验证过程异常终止'],
            'facts': [f"验证异常: {str(e)}"],
            'memories': [f"工具名称验证失败: {str(e)}"]
        }