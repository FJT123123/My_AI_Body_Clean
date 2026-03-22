# tool_name: enhanced_tool_name_validator
from langchain.tools import tool
import json
import re

def _generate_safe_tool_name(base_name: str, max_length: int = 64) -> str:
    """
    生成符合API约束的安全工具名称
    
    Args:
        base_name: 基础名称
        max_length: 最大长度限制，默认64字符
        
    Returns:
        符合约束的安全工具名称
    """
    # 只保留字母、数字、下划线
    safe_name = re.sub(r'[^a-z0-9_]', '_', base_name.lower())
    
    # 移除连续的下划线
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # 移除开头和结尾的下划线
    safe_name = safe_name.strip('_')
    
    # 截断到最大长度
    if len(safe_name) > max_length:
        # 保留前58个字符 + "_trc" 后缀表示截断
        safe_name = safe_name[:58] + "_trc"
    
    # 确保不以数字开头
    if safe_name and safe_name[0].isdigit():
        safe_name = "tool_" + safe_name
    
    return safe_name

@tool
def enhanced_tool_name_validator(input_args: str) -> dict:
    """
    验证并生成安全的工具名称，同时处理字符集合规性和长度限制
    
    Args:
        input_args: JSON字符串，包含 'tool_name' 和可选的 'max_length'
        
    Returns:
        包含验证结果和安全名称的字典
    """
    try:
        params = json.loads(input_args) if isinstance(input_args, str) else input_args
        tool_name = params.get('tool_name', '')
        max_length = params.get('max_length', 64)
        
        if not tool_name:
            return {
                'result': {'error': '缺少 tool_name 参数'},
                'insights': ['参数校验失败：必须提供tool_name'],
                'facts': [],
                'memories': []
            }
            
        # 验证原始名称
        original_valid = True
        errors = []
        
        # 检查长度
        if len(tool_name) > max_length:
            original_valid = False
            errors.append(f"工具名称超过{max_length}字符限制")
            
        # 检查字符集
        if not re.match(r'^[a-z0-9_]+$', tool_name):
            original_valid = False
            errors.append("工具名称包含非法字符，只允许字母、数字、下划线")
            
        # 检查是否以数字开头
        if tool_name and tool_name[0].isdigit():
            original_valid = False
            errors.append("工具名称不能以数字开头")
        
        # 生成安全名称
        safe_name = _generate_safe_tool_name(tool_name, max_length)
        
        # 二次验证安全名称
        safe_name_valid = bool(re.match(r'^[a-z0-9_]+$', safe_name)) and len(safe_name) <= max_length
        
        return {
            'result': {
                'original_valid': original_valid,
                'original_name': tool_name,
                'safe_tool_name': safe_name,
                'safe_name_valid': safe_name_valid,
                'errors': errors,
                'length_check': len(tool_name) <= max_length,
                'charset_check': bool(re.match(r'^[a-z0-9_]+$', tool_name)),
                'start_char_check': not (tool_name and tool_name[0].isdigit())
            },
            'insights': [
                f'工具名称验证完成: 原始名称{"有效" if original_valid else "无效"}',
                f'安全工具名称: {safe_name}',
                f'原始长度: {len(tool_name)}, 安全长度: {len(safe_name)}',
                f'安全名称有效性: {"有效" if safe_name_valid else "无效"}'
            ],
            'facts': [
                f'tool_name_validation_result_{tool_name[:20]}'
            ],
            'memories': [
                '工具名称必须符合API约束：长度<=64，字符集[a-z0-9_]，不能以数字开头',
                f'安全工具名称生成规则已验证: {safe_name}'
            ]
        }
        
    except json.JSONDecodeError:
        return {
            'result': {'error': '输入参数JSON格式错误'},
            'insights': ['JSON解析失败'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'工具名称验证失败: {str(e)}'},
            'insights': ['工具名称验证异常'],
            'facts': [],
            'memories': []
        }