"""
自动生成的技能模块
需求: 测试参数传递的技能，打印接收到的参数
生成时间: 2026-03-21 13:30:28
"""

# skill_name: test_parameter_receiver
def main(args=None):
    """
    测试参数传递的技能，打印接收到的参数
    用于验证参数传递机制和调试参数内容
    """
    import json
    import os
    
    if args is None:
        args = {}
    
    # 获取上下文信息
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 记录接收到的参数
    received_args = {
        'original_args': args,
        'context_available': bool(context),
        'db_path_exists': bool(db_path and os.path.exists(db_path)),
        'context_keys': list(context.keys()) if context else []
    }
    
    # 打印接收到的参数内容
    print("接收到的参数详情:")
    print(f"- args: {args}")
    print(f"- context: {context}")
    print(f"- db_path: {db_path}")
    print(f"- 参数总数: {len(args) if args else 0}")
    
    # 检查是否包含隐藏的上下文参数
    has_context = '__context__' in args
    has_db_path = bool(db_path)
    
    insights = []
    if has_context:
        insights.append("参数中包含上下文信息")
    if has_db_path:
        insights.append("数据库路径已提供")
    
    # 返回结构化结果
    result = {
        'received_args': received_args,
        'param_count': len(args) if args else 0,
        'has_context': has_context,
        'has_db_path': has_db_path,
        'context_keys': list(context.keys()) if context else []
    }
    
    return {
        'result': result,
        'insights': insights,
        'memories': [
            f"参数接收测试完成，接收到{len(args) if args else 0}个参数",
            f"上下文信息: {bool(context)}",
            f"数据库路径: {bool(db_path)}"
        ]
    }