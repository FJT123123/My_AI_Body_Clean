import subprocess
import os
import tempfile
import json

def main(input_args=""):
    """创建使用不常见编解码器的测试视频技能"""
    # 解析输入参数
    if input_args:
        if isinstance(input_args, str):
            try:
                params = json.loads(input_args)
            except json.JSONDecodeError:
                params = {}
        else:
            params = input_args
    else:
        params = {}
    
    codec = params.get('codec', 'ffv1')
    duration = params.get('duration', 5)
    output_path = params.get('output_path', os.path.join(tempfile.gettempdir(), f"uncommon_{codec}_test.avi"))
    
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=640x480:rate=30',
        '-t', str(duration), '-c:v', codec, output_path
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    
    if result.returncode == 0 and os.path.exists(output_path):
        return {
            'result': {'video_path': output_path, 'codec': codec, 'success': True},
            'insights': [f'成功创建{codec}编解码器测试视频: {output_path}'],
            'facts': [['uncommon_codec_test_video', 'has_codec', codec]],
            'memories': [f'{codec}编解码器测试视频创建成功: {output_path}']
        }
    else:
        return {
            'result': {'error': f'Failed to create {codec} test video', 'codec': codec, 'success': False},
            'insights': [f'无法创建{codec}测试视频'],
            'facts': [],
            'memories': []
        }