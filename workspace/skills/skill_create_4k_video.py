import subprocess
import os
import tempfile
import json

def main(input_args=""):
    """创建4K测试视频技能"""
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
    
    duration = params.get('duration', 5)
    output_path = params.get('output_path', os.path.join(tempfile.gettempdir(), "4k_stress_test.mp4"))
    
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', f'testsrc=size=3840x2160:rate=60',
        '-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast', output_path
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    
    if result.returncode == 0 and os.path.exists(output_path):
        return {
            'result': {'video_path': output_path, 'success': True},
            'insights': [f'成功创建4K压力测试视频: {output_path}'],
            'facts': [['stress_test_video', 'has_resolution', '3840x2160']],
            'memories': [f'4K压力测试视频创建成功: {output_path}']
        }
    else:
        return {
            'result': {'error': 'Failed to create 4K test video', 'success': False},
            'insights': ['无法创建4K测试视频'],
            'facts': [],
            'memories': []
        }