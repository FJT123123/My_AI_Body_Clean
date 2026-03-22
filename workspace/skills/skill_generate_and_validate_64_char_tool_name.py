"""
自动生成的技能模块
需求: 创建一个正好64字符长的工具名称并验证其有效性
生成时间: 2026-03-21 18:03:18
"""

# skill_name: generate_and_validate_64_char_tool_name
import re
import random
import string

def main(args=None):
    """
    生成一个恰好64个字符长的工具名称，并验证其有效性
    """
    if args is None:
        args = {}
    
    # 生成64字符长度的工具名称
    tool_name = generate_64_char_tool_name()
    
    # 验证工具名称的有效性
    is_valid, validation_errors = validate_tool_name(tool_name)
    
    result = {
        'tool_name': tool_name,
        'length': len(tool_name),
        'is_valid': is_valid,
        'validation_errors': validation_errors
    }
    
    insights = []
    if is_valid:
        insights.append(f"成功生成有效工具名称: {tool_name}")
        insights.append(f"工具名称长度为64字符: {len(tool_name)}")
    else:
        insights.append(f"生成的工具名称无效: {tool_name}")
        insights.extend([f"验证错误: {error}" for error in validation_errors])
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            ['tool_name', 'has_length', '64'],
            ['tool_name', 'validation_status', 'valid' if is_valid else 'invalid']
        ]
    }

def generate_64_char_tool_name():
    """生成一个恰好64个字符长的工具名称"""
    # 使用字母、数字和下划线生成名称
    chars = string.ascii_lowercase + string.digits + '_'
    
    # 确保开头是字母
    name = random.choice(string.ascii_lowercase)
    
    # 填充剩余63个字符
    for _ in range(63):
        name += random.choice(chars)
    
    return name

def validate_tool_name(tool_name):
    """验证工具名称的有效性"""
    errors = []
    
    # 检查长度是否为64
    if len(tool_name) != 64:
        errors.append(f"长度必须为64字符，当前为{len(tool_name)}字符")
    
    # 检查是否只包含字母、数字和下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', tool_name):
        errors.append("名称只能包含字母、数字和下划线")
    
    # 检查是否以字母开头
    if not re.match(r'^[a-zA-Z]', tool_name):
        errors.append("名称必须以字母开头")
    
    # 检查是否以字母或数字结尾
    if not re.match(r'.*[a-zA-Z0-9]$', tool_name):
        errors.append("名称必须以字母或数字结尾")
    
    return len(errors) == 0, errors