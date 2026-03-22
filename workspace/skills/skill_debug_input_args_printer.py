"""
自动生成的技能模块
需求: 调试技能，打印接收到的原始输入参数
生成时间: 2026-03-21 13:33:50
"""

# skill_name: debug_input_args_printer
def main(args=None):
    """
    调试技能：打印接收到的原始输入参数
    用于查看传入技能的完整参数结构，包括上下文信息
    """
    import json
    
    if args is None:
        args = {}
    
    # 打印原始输入参数
    result = {
        'received_args': args,
        'args_type': type(args).__name__,
        'args_keys': list(args.keys()) if isinstance(args, dict) else None
    }
    
    # 如果有上下文信息，也进行详细分析
    context = args.get('__context__', {})
    if context:
        result['context_info'] = {
            'has_context': True,
            'context_keys': list(context.keys()),
            'db_path': context.get('db_path', 'Not provided'),
            'has_db_path': bool(context.get('db_path', ''))
        }
    
    # 返回结构化结果
    return {
        'result': result,
        'insights': [
            f"接收到的参数类型为 {type(args).__name__}",
            f"参数包含 {len(args) if isinstance(args, dict) else 0} 个键值对",
            f"包含上下文信息: {bool(context)}"
        ],
        'facts': [
            ['debug_input_args_printer', 'received_args_type', type(args).__name__],
            ['debug_input_args_printer', 'has_context', str(bool(context))]
        ],
        'memories': [
            {
                'event_type': 'skill_debug',
                'content': f"调试信息: {json.dumps(result, ensure_ascii=False, default=str)[:500]}",
                'importance': 0.5,
                'tags': ['debug', 'input_args']
            }
        ]
    }