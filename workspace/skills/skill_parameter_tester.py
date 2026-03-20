"""
自动生成的技能模块
需求: 创建一个简单的参数测试技能，打印接收到的参数
生成时间: 2026-03-12 16:29:14
"""

# skill_name: parameter_tester
def main(args=None):
    """
    参数测试技能：接收并打印传入的参数，用于验证参数传递功能
    """
    if args is None:
        args = {}
    
    # 提取参数信息
    received_args = args.copy()
    
    # 从上下文获取数据库路径和记忆数据
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 生成参数信息
    param_info = {
        'received_args_count': len(received_args),
        'args_keys': list(received_args.keys()),
        'has_context': '__context__' in received_args,
        'context_keys': list(context.keys()) if context else [],
        'db_path_available': bool(db_path)
    }
    
    # 返回结果
    result = {
        'received_args': received_args,
        'param_info': param_info,
        'status': '参数接收完成'
    }
    
    # 生成洞察信息
    insights = [f"接收到 {len(received_args)} 个参数", f"上下文包含 {len(context)} 个键"]
    
    return {
        'result': result,
        'insights': insights,
        'memories': [{
            'event_type': 'skill_insight',
            'content': f"参数测试完成，接收到参数信息: {param_info}",
            'importance': 0.5
        }]
    }