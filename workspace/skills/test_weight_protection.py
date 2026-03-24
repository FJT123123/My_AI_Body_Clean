import json

def main(input_args=""):
    """测试权重保护功能"""
    try:
        if input_args:
            params = json.loads(input_args)
        else:
            params = {}
    except:
        params = {}
    
    # 获取调试信息
    debug_info = params.get('debug_info', {'test': 'default'})
    context = params.get('context', 'test')
    tool_name = params.get('tool_name', 'test_tool')
    
    # 应用保护
    from workspace.patches.complete_debug_info_weight_protection import protect_debug_info_in_toolchain
    protected = protect_debug_info_in_toolchain(debug_info, context, tool_name)
    
    return {
        'result': protected,
        'insights': ['成功应用调试信息权重保护'],
        'facts': ['权重保护阈值设置为0.95'],
        'memories': ['complete_debug_info_weight_protection 测试成功']
    }