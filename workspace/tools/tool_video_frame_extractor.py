# tool_name: video_frame_extractor
from langchain.tools import tool
import os
import subprocess
from pathlib import Path

@tool
def video_frame_extractor(video_path: str, output_dir: str, frame_rate: float = 1.0, max_frames: int = 100):
    """
    从视频中抽取帧并保存为图像文件
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录路径
        frame_rate: 抽帧频率（每秒帧数），默认1.0
        max_frames: 最大抽取帧数，默认100
        
    Returns:
        dict: 包含抽取结果的信息
            - success: 是否成功
            - frames_extracted: 实际抽取的帧数
            - output_files: 输出文件列表
            - error: 错误信息（如果有）
    """
    # 验证输入参数
    if not os.path.exists(video_path):
        return {
            "success": False,
            "frames_extracted": 0,
            "output_files": [],
            "error": f"视频文件不存在: {video_path}"
        }
    
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 构建ffmpeg命令
    output_pattern = os.path.join(output_dir, "frame_%06d.jpg")
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={frame_rate}",
        "-vframes", str(max_frames),
        "-q:v", "2",
        output_pattern,
        "-y"
    ]
    
    try:
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            return {
                "success": False,
                "frames_extracted": 0,
                "output_files": [],
                "error": f"FFmpeg执行失败: {result.stderr}"
            }
        
        # 获取输出文件列表
        output_files = []
        for i in range(1, max_frames + 1):
            frame_file = os.path.join(output_dir, f"frame_{i:06d}.jpg")
            if os.path.exists(frame_file):
                output_files.append(frame_file)
            else:
                break
        
        return {
            "success": True,
            "frames_extracted": len(output_files),
            "output_files": output_files,
            "error": ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "frames_extracted": 0,
            "output_files": [],
            "error": "FFmpeg执行超时"
        }
    except Exception as e:
        return {
            "success": False,
            "frames_extracted": 0,
            "output_files": [],
            "error": f"异常: {str(e)}"
        }