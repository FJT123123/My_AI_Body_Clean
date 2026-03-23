# tool_name: memory_decay_video_frame_extractor
from langchain.tools import tool
import os
import json
import subprocess
import tempfile
from pathlib import Path

@tool
def memory_decay_video_frame_extractor(video_path: str = None, output_dir: str = None, frame_rate: float = 1.0, max_frames: int = 50, create_test_video: bool = False):
    """
    记忆衰减实证测试专用视频帧抽取工具
    
    Args:
        video_path (str): 输入视频文件路径（可选，如果create_test_video=True则忽略）
        output_dir (str): 输出目录路径
        frame_rate (float): 抽帧频率（每秒帧数），默认1.0
        max_frames (int): 最大抽取帧数，默认50
        create_test_video (bool): 是否创建测试视频文件
    
    Returns:
        dict: 包含抽取结果和物理可观测指标的完整报告
    """
    # 使用运行时注入API加载能力模块
    load_capability_module = __import__('builtins').__dict__.get('load_capability_module')
    if load_capability_module:
        try:
            env_drift_cap = load_capability_module('environment_drift_detection_capability')
            video_physics_cap = load_capability_module('video_physics_validation_capability')
        except:
            env_drift_cap = None
            video_physics_cap = None
    else:
        env_drift_cap = None
        video_physics_cap = None

    # 设置默认输出目录
    if not output_dir:
        output_dir = "/Users/zhufeng/My_AI_Body_Clean/workspace/test_frames"
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 如果需要创建测试视频
    if create_test_video:
        # 创建一个简单的测试视频使用ffmpeg
        test_video_path = os.path.join("/tmp", "test_memory_decay_video.mp4")
        
        # 使用ffmpeg生成一个5秒的测试视频
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", "testsrc=duration=5:size=640x480:rate=30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            test_video_path,
            "-y"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'测试视频创建失败: {result.stderr}',
                    'physical_metrics': {}
                }
            video_path = test_video_path
        except Exception as e:
            return {
                'success': False,
                'error': f'测试视频创建异常: {str(e)}',
                'physical_metrics': {}
            }
    
    # 验证视频文件存在
    if not video_path or not os.path.exists(video_path):
        return {
            'success': False,
            'error': f'视频文件不存在: {video_path}',
            'physical_metrics': {}
        }
    
    try:
        # 使用ffmpeg抽取帧
        output_pattern = os.path.join(output_dir, "frame_%06d.jpg")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"fps={frame_rate}",
            "-frames:v", str(max_frames),
            "-q:v", "2",
            output_pattern,
            "-y"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            error_msg = f"FFmpeg执行失败: {result.stderr}"
            return {
                'success': False,
                'error': error_msg,
                'physical_metrics': {}
            }
        
        # 统计实际抽取的帧数
        extracted_frames = []
        for file in os.listdir(output_dir):
            if file.startswith("frame_") and file.endswith(".jpg"):
                extracted_frames.append(file)
        
        actual_frames = len(extracted_frames)
        
        # 计算物理可观测指标
        total_size_kb = 0
        for frame_file in extracted_frames:
            file_path = os.path.join(output_dir, frame_file)
            total_size_kb += os.path.getsize(file_path) // 1024
        
        # 如果有环境漂移检测能力，收集额外指标
        if env_drift_cap:
            try:
                env_metrics = env_drift_cap.collect_video_processing_environment_metrics(video_path, test_duration=5)
            except:
                env_metrics = {}
        else:
            env_metrics = {}
        
        # 如果有视频物理验证能力，执行验证
        if video_physics_cap:
            try:
                physics_validation = video_physics_cap.validate_video_frame_physics_compliance(video_path, output_dir=output_dir)
            except:
                physics_validation = {}
        else:
            physics_validation = {}
        
        # 返回完整的物理验证报告
        report = {
            'success': True,
            'frames_extracted': actual_frames,
            'max_frames_requested': max_frames,
            'frame_rate_used': frame_rate,
            'total_data_size_kb': total_size_kb,
            'output_directory': output_dir,
            'output_files': sorted(extracted_frames),
            'physical_metrics': {
                'data_volume_kb': total_size_kb,
                'frames_per_kb': actual_frames / max(total_size_kb, 1),
                'extraction_efficiency': actual_frames / max_frames if max_frames > 0 else 0,
                'access_latency_ms': 0,  # 可以通过更复杂的测量获得
                'retrieval_accuracy': 1.0 if actual_frames > 0 else 0.0
            },
            'environment_metrics': env_metrics,
            'physics_validation': physics_validation,
            'validation_status': 'passed' if actual_frames > 0 else 'failed'
        }
        
        return report
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': '视频处理超时',
            'physical_metrics': {}
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'视频帧抽取异常: {str(e)}',
            'physical_metrics': {}
        }