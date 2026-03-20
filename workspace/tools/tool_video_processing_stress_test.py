# tool_name: video_processing_stress_test
import os
import json
import psutil
import time
import subprocess
import tempfile
from typing import Dict, Any
from langchain.tools import tool

@tool
def video_processing_stress_test(input_args: str = "") -> Dict[str, Any]:
    """
    视频处理真实世界压力测试工具
    
    Args:
        input_args (str): JSON字符串，包含以下可选参数:
            - test_high_resolution: 是否测试高分辨率视频 (bool)
            - test_unsupported_codec: 是否测试不支持的编解码器 (bool)
    
    Returns:
        Dict[str, Any]: 压力测试结果字典
    """
    def create_test_video(output_path: str, resolution: str = "1920x1080", duration: int = 10):
        """创建用于测试的视频文件"""
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i', f'testsrc=size={resolution}:rate=30',
            '-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast', output_path
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        return result.returncode == 0

    def get_system_load():
        """获取当前系统负载"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'available_memory_mb': psutil.virtual_memory().available // (1024 * 1024)
        }

    def run_video_validation(video_path: str):
        """运行视频验证"""
        # 使用现有的视频分析工具
        from langchain.tools import Tool
        from workspace.skills.skill_video_physics_validation_workflow import main as validation_main
        return validation_main({"video_path": video_path})

    def test_codec_support(codec_name: str):
        """测试特定编解码器是否受支持"""
        try:
            result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, timeout=10)
            return codec_name in result.stdout
        except:
            return False

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
    
    test_high_resolution = params.get('test_high_resolution', False)
    test_unsupported_codec = params.get('test_unsupported_codec', False)
    
    results = {
        'baseline_system_load': get_system_load(),
        'tests_run': [],
        'overall_success': True,
        'errors': []
    }
    
    # 创建测试视频
    test_video = os.path.join(tempfile.gettempdir(), 'stress_test_video.mp4')
    resolution = "3840x2160" if test_high_resolution else "1920x1080"
    
    video_created = create_test_video(test_video, resolution, 10)
    if not video_created:
        return {
            'result': {'error': 'Failed to create test video'},
            'insights': ['无法创建测试视频'],
            'facts': [],
            'memories': []
        }
    
    try:
        # 测试正常条件下的视频验证
        normal_result = run_video_validation(test_video)
        results['tests_run'].append({
            'test_name': 'normal_validation',
            'system_load_before': get_system_load(),
            'result': normal_result,
            'system_load_after': get_system_load()
        })
        
        # 测试高分辨率视频（如果请求）
        if test_high_resolution:
            high_res_result = run_video_validation(test_video)
            results['tests_run'].append({
                'test_name': 'high_resolution_validation',
                'system_load_before': get_system_load(),
                'result': high_res_result,
                'system_load_after': get_system_load()
            })
        
        # 测试不支持的编解码器处理
        if test_unsupported_codec:
            # 创建一个使用不太常见的编解码器的视频
            uncommon_video = os.path.join(tempfile.gettempdir(), 'uncommon_codec_test.avi')
            cmd = [
                'ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=640x480:rate=30',
                '-t', '5', '-c:v', 'ffv1', uncommon_video
            ]
            uncommon_created = subprocess.run(cmd, capture_output=True, timeout=30).returncode == 0
            
            if uncommon_created:
                try:
                    uncommon_result = run_video_validation(uncommon_video)
                    results['tests_run'].append({
                        'test_name': 'uncommon_codec_validation',
                        'system_load_before': get_system_load(),
                        'result': uncommon_result,
                        'system_load_after': get_system_load()
                    })
                except Exception as e:
                    results['tests_run'].append({
                        'test_name': 'uncommon_codec_validation',
                        'system_load_before': get_system_load(),
                        'error': str(e),
                        'system_load_after': get_system_load()
                    })
                finally:
                    if os.path.exists(uncommon_video):
                        os.unlink(uncommon_video)
        
        # 检查所有测试是否成功
        for test in results['tests_run']:
            if 'error' in test or (isinstance(test['result'], dict) and 
                                  test['result'].get('result', {}).get('error')):
                results['overall_success'] = False
                error_msg = test.get('error', test['result'].get('result', {}).get('error', 'Unknown error'))
                results['errors'].append(f"{test['test_name']}: {error_msg}")
    
    finally:
        # 清理测试视频
        if os.path.exists(test_video):
            os.unlink(test_video)
    
    return {
        'result': results,
        'insights': [
            f"Baseline CPU load: {results['baseline_system_load']['cpu_percent']}%",
            f"Baseline memory usage: {results['baseline_system_load']['memory_percent']}%",
            f"High resolution test: {test_high_resolution}",
            f"Uncommon codec test: {test_unsupported_codec}",
            f"Overall success: {results['overall_success']}"
        ],
        'facts': [
            'Video processing real-world stress test completed',
            f"Tests run: {len(results['tests_run'])}",
            f"Errors encountered: {len(results['errors'])}"
        ],
        'memories': [
            f"Real-world stress test results: {results['overall_success']}, errors: {len(results['errors'])}"
        ]
    }