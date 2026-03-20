"""
自动生成的技能模块
需求: 视频任务依赖检查技能，检查ffmpeg、ffprobe、opencv-python等视频处理必需的依赖是否可用
生成时间: 2026-03-13 19:13:44
"""

# skill_name: video_task_dependency_checker

def main(args=None):
    """
    检查视频处理任务所需的依赖是否已安装并可用
    包括 ffmpeg、ffprobe、opencv-python 等视频处理必需的依赖
    """
    import subprocess
    import sys
    import importlib
    
    result = {
        'ffmpeg': {'available': False, 'version': None},
        'ffprobe': {'available': False, 'version': None},
        'opencv_python': {'available': False, 'version': None}
    }
    
    insights = []
    facts = []
    
    # 检查 ffmpeg
    try:
        ffmpeg_result = subprocess.run(['ffmpeg', '-version'], 
                                     capture_output=True, text=True, timeout=10)
        if ffmpeg_result.returncode == 0:
            result['ffmpeg']['available'] = True
            # 提取版本信息
            version_line = ffmpeg_result.stdout.split('\n')[0]
            result['ffmpeg']['version'] = version_line.split()[2] if len(version_line.split()) >= 3 else 'unknown'
            insights.append(f"FFmpeg 已安装，版本: {result['ffmpeg']['version']}")
            facts.append(('ffmpeg', 'version', result['ffmpeg']['version']))
        else:
            insights.append("FFmpeg 未安装或不可用")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        insights.append("FFmpeg 未安装或不在系统 PATH 中")
    
    # 检查 ffprobe
    try:
        ffprobe_result = subprocess.run(['ffprobe', '-version'], 
                                      capture_output=True, text=True, timeout=10)
        if ffprobe_result.returncode == 0:
            result['ffprobe']['available'] = True
            # 提取版本信息
            version_line = ffprobe_result.stdout.split('\n')[0]
            result['ffprobe']['version'] = version_line.split()[2] if len(version_line.split()) >= 3 else 'unknown'
            insights.append(f"FFprobe 已安装，版本: {result['ffprobe']['version']}")
            facts.append(('ffprobe', 'version', result['ffprobe']['version']))
        else:
            insights.append("FFprobe 未安装或不可用")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        insights.append("FFprobe 未安装或不在系统 PATH 中")
    
    # 检查 opencv-python
    try:
        import cv2
        result['opencv_python']['available'] = True
        result['opencv_python']['version'] = cv2.__version__
        insights.append(f"OpenCV-Python 已安装，版本: {result['opencv_python']['version']}")
        facts.append(('opencv_python', 'version', result['opencv_python']['version']))
    except ImportError:
        insights.append("OpenCV-Python 未安装")
    
    # 检查总体可用性
    all_available = all(item['available'] for item in result.values())
    
    if all_available:
        insights.append("所有视频处理依赖均已安装并可用")
        facts.append(('video_processing_dependencies', 'status', 'all_available'))
    else:
        missing_deps = [key for key, value in result.items() if not value['available']]
        insights.append(f"缺少以下依赖: {', '.join(missing_deps)}")
        facts.append(('video_processing_dependencies', 'status', 'missing_some'))
    
    return {
        'result': result,
        'insights': insights,
        'facts': facts,
        'capabilities': ['video_processing'] if all_available else []
    }