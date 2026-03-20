"""
测试文件验证功能
"""
import json
from pathlib import Path

def validate_file_output(target_dir, expected_count, file_pattern="*"):
    """验证指定目录下是否存在符合预期数量和命名模式的文件"""
    try:
        target_path = Path(target_dir)
        if not target_path.exists() or not target_path.is_dir():
            return {
                'success': False,
                'target_dir': str(target_path),
                'expected_count': expected_count,
                'actual_count': 0,
                'error': '目标目录不存在或不是目录'
            }
        
        # 获取匹配的文件列表
        files = list(target_path.glob(file_pattern))
        actual_count = len(files)
        
        success = (actual_count == expected_count)
        
        return {
            'success': success,
            'target_dir': str(target_path),
            'expected_count': expected_count,
            'actual_count': actual_count,
            'file_pattern': file_pattern,
            'matched_files': [str(f) for f in files],
            'validation_result': '文件产出验证成功' if success else f'期望 {expected_count} 个文件，实际找到 {actual_count} 个'
        }
    except Exception as e:
        return {
            'success': False,
            'target_dir': target_dir,
            'expected_count': expected_count,
            'actual_count': 0,
            'error': str(e)
        }

def main(args=None):
    print(f"DEBUG: main args = {args}, type = {type(args)}")
    if args is None:
        args = {}
    elif isinstance(args, str):
        args = json.loads(args)
        print(f"DEBUG: parsed args = {args}")
    # 如果已经是字典，直接使用
    
    print(f"DEBUG: full args keys = {list(args.keys()) if isinstance(args, dict) else 'not dict'}")
    if isinstance(args, dict) and 'input' in args:
        print(f"DEBUG: input content = {args['input']}")
        # 尝试解析 input
        try:
            import json
            input_data = json.loads(args['input'])
            print(f"DEBUG: parsed input_data = {input_data}")
            target_dir = input_data.get('target_dir', './test_frames')
            expected_count = input_data.get('expected_count', 5)
            file_pattern = input_data.get('file_pattern', '*_*.jpg')
        except:
            print("DEBUG: failed to parse input")
            target_dir = args.get('target_dir', './test_frames')
            expected_count = args.get('expected_count', 5)
            file_pattern = args.get('file_pattern', '*_*.jpg')
    else:
        target_dir = args.get('target_dir', './test_frames')
        expected_count = args.get('expected_count', 5)
        file_pattern = args.get('file_pattern', '*_*.jpg')
    
    print(f"DEBUG: target_dir={target_dir}, expected_count={expected_count}, file_pattern={file_pattern}")
    
    result = validate_file_output(target_dir, expected_count, file_pattern)
    
    return {
        'result': result,
        'insights': [f"测试验证结果: {result.get('validation_result', '未知')}"],
        'facts': []
    }