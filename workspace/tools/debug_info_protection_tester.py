def main(input_args=None):
    """
    调试信息权重保护测试工具
    测试增强版调试信息权重保护机制是否有效
    """
    import json
    
    # 解析输入参数
    if input_args:
        try:
            params = json.loads(input_args)
        except (json.JSONDecodeError, TypeError):
            params = {}
    else:
        params = {}
    
    # 获取测试数据
    test_debug_info = params.get('debug_info', {'content': 'test content', '_weight': 0.05})
    minimum_threshold = params.get('minimum_threshold', 0.8)
    
    # 应用保护机制
    try:
        from enhanced_debug_info_weight_protection import apply_debug_info_weight_protection
        protected_debug_info = apply_debug_info_weight_protection(
            test_debug_info, 
            context="protection_test",
            tool_name="debug_info_protection_tester",
            minimum_weight_threshold=minimum_threshold
        )
        
        original_weight = test_debug_info.get('_weight', 1.0) if isinstance(test_debug_info, dict) else 1.0
        protected_weight = protected_debug_info.get('_weight', 1.0)
        
        result = {
            'success': True,
            'original_debug_info': test_debug_info,
            'protected_debug_info': protected_debug_info,
            'original_weight': original_weight,
            'protected_weight': protected_weight,
            'weight_increased': protected_weight > original_weight,
            'meets_threshold': protected_weight >= minimum_threshold,
            'protection_applied': protected_debug_info.get('_weight_protected', False)
        }
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e),
            'original_debug_info': test_debug_info
        }
    
    return {
        'result': result,
        'insights': [
            f"调试信息权重保护测试完成: {'成功' if result['success'] else '失败'}",
            f"原始权重: {result.get('original_weight', 'N/A')}, 保护后权重: {result.get('protected_weight', 'N/A')}",
            f"是否满足阈值要求: {result.get('meets_threshold', 'N/A')}"
        ],
        'facts': [
            f"调试信息权重保护机制测试结果: {result}"
        ],
        'memories': []
    }