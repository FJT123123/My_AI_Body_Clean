def main(input_args):
    """
    测试OpenCV图像处理能力 - 修正版本
    """
    import json
    
    # 处理实际的参数结构
    actual_input = input_args
    if isinstance(input_args, dict) and 'input' in input_args:
        # 从包装结构中提取实际输入
        try:
            actual_input = json.loads(input_args['input'])
        except:
            actual_input = input_args['input'] if isinstance(input_args['input'], dict) else {}
    
    image_path = None
    if isinstance(actual_input, dict):
        image_path = actual_input.get("image_path")
    
    if not image_path:
        return {
            'result': {'error': '缺少 image_path 参数', 'debug_input': str(input_args)[:200]},
            'insights': ['参数校验失败：必须提供image_path'],
            'facts': [],
            'memories': []
        }
    
    try:
        import cv2
        import os
        
        if not os.path.exists(image_path):
            return {
                'result': {'error': f'图像文件 {image_path} 不存在'},
                'insights': [f'无法找到测试图像文件: {image_path}'],
                'facts': [],
                'memories': []
            }
        
        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            return {
                'result': {'error': f'无法读取图像文件 {image_path}'},
                'insights': [f'OpenCV无法解析图像文件: {image_path}'],
                'facts': [],
                'memories': []
            }
        
        height, width = img.shape[:2]
        
        return {
            'result': {
                'success': True,
                'image_path': image_path,
                'dimensions': f'{width}x{height}',
                'message': f'成功读取并处理图像: {image_path}'
            },
            'insights': [f'OpenCV成功读取图像: {image_path} ({width}x{height})'],
            'facts': [f'图像 {image_path} 尺寸为 {width}x{height}'],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': str(e), 'message': '图像处理失败'},
            'insights': [f'图像处理过程中发生错误: {str(e)}'],
            'facts': [],
            'memories': []
        }