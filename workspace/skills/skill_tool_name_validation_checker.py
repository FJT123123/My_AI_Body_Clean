"""
自动生成的技能模块
需求: 测试工具名称长度验证功能，使用 _validate_and_truncate_tool_name 函数验证给定的工具名称是否符合API约束。
生成时间: 2026-03-21 18:18:07
"""

# skill_name: tool_name_validation_checker

def main(args=None):
    """
    验证工具名称是否符合API约束的验证器
    使用 _validate_and_truncate_tool_name 函数验证给定的工具名称是否符合API约束
    """
    if args is None:
        args = {}
    
    # 获取要验证的工具名称
    tool_name = args.get('tool_name', '')
    
    # 获取上下文信息
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 验证函数定义
    def _validate_and_truncate_tool_name(name, max_length=64):
        """
        验证并截断工具名称以符合API约束
        """
        if not isinstance(name, str):
            return {'valid': False, 'error': '工具名称必须是字符串类型'}
        
        if len(name) == 0:
            return {'valid': False, 'error': '工具名称不能为空'}
        
        # 检查字符限制
        if len(name) > max_length:
            return {
                'valid': False, 
                'error': f'工具名称长度超过最大限制 {max_length} 个字符',
                'truncated_name': name[:max_length]
            }
        
        # 检查字符类型（只允许字母、数字、下划线和连字符）
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return {
                'valid': False, 
                'error': '工具名称只能包含字母、数字、下划线和连字符'
            }
        
        # 检查是否以字母开头
        if not name[0].isalpha():
            return {
                'valid': False,
                'error': '工具名称必须以字母开头'
            }
        
        # 验证通过
        return {
            'valid': True,
            'name': name,
            'length': len(name),
            'max_length': max_length
        }
    
    # 执行验证
    validation_result = _validate_and_truncate_tool_name(tool_name)
    
    # 准备返回结果
    result = {
        'tool_name': tool_name,
        'validation_result': validation_result,
        'is_valid': validation_result.get('valid', False)
    }
    
    # 生成洞察
    insights = []
    if validation_result.get('valid'):
        insights.append(f"工具名称 '{tool_name}' 符合API约束")
    else:
        error_msg = validation_result.get('error', '未知错误')
        insights.append(f"工具名称 '{tool_name}' 验证失败: {error_msg}")
    
    # 如果有截断建议，添加到洞察中
    if 'truncated_name' in validation_result:
        truncated = validation_result['truncated_name']
        insights.append(f"建议截断为: {truncated}")
    
    return {
        'result': result,
        'insights': insights,
        'facts': [
            ['tool_name', 'validation_status', 'valid' if validation_result.get('valid') else 'invalid'],
            ['tool_name', 'length', str(len(tool_name) if tool_name else 0)],
            ['tool_name', 'max_length_constraint', '64']
        ]
    }