"""
测试 enhanced_classify_error_with_semantics 函数的可用性和功能
"""

def main(args=None):
    """
    测试 enhanced_classify_error_with_semantics 函数
    """
    import json
    
    # 测试用例
    test_cases = [
        "No module named 'requests'",
        "缺少必需参数 'input_file'",
        "文件不存在: /tmp/nonexistent.txt",
        "This is a completely unknown error message"
    ]
    
    results = []
    
    # 检查函数是否在全局命名空间中
    if 'enhanced_classify_error_with_semantics' in globals():
        function_available = True
        classify_func = globals()['enhanced_classify_error_with_semantics']
    else:
        # 尝试从 builtins 导入
        import builtins
        if hasattr(builtins, 'enhanced_classify_error_with_semantics'):
            function_available = True
            classify_func = builtins.enhanced_classify_error_with_semantics
        else:
            function_available = False
            classify_func = None
    
    if not function_available:
        return {
            'result': {'error': 'enhanced_classify_error_with_semantics function not available in global namespace'},
            'insights': ['函数未在全局命名空间中找到'],
            'facts': []
        }
    
    for test_case in test_cases:
        try:
            result = classify_func(test_case)
            results.append({
                'input': test_case,
                'classified_type': result,
                'success': True
            })
        except Exception as e:
            results.append({
                'input': test_case,
                'error': str(e),
                'success': False
            })
    
    return {
        'result': {
            'function_available': function_available,
            'test_results': results
        },
        'insights': [f"测试了 {len(test_cases)} 个错误消息，函数可用性: {function_available}"],
        'facts': []
    }