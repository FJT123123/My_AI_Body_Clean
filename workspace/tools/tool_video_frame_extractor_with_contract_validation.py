# tool_name: video_frame_extractor_with_contract_validation

from langchain.tools import tool
import os
import json
import subprocess
from pathlib import Path

@tool
def video_frame_extractor_with_contract_validation(video_path: str, output_dir: str = None, frame_rate: int = 1, max_frames: int = None, format: str = 'jpg'):
    """
    从视频中抽取帧，并验证参数契约（正确参数顺序）
    
    Args:
        video_path (str): 输入视频文件路径（必需）
        output_dir (str, optional): 输出目录，默认为None（自动生成）
        frame_rate (int, optional): 抽取帧率（每秒帧数），默认为1
        max_frames (int, optional): 最大抽取帧数，默认为None（不限制）
        format (str, optional): 输出图像格式，支持'jpg'、'png'，默认为'jpg'
    
    Returns:
        dict: 包含抽取结果的字典
    """
    # 参数契约验证
    if not video_path:
        return {
            'result': {'error': '缺少 video_path 参数'},
            'insights': ['参数校验失败：必须提供video_path'],
            'facts': [],
            'memories': []
        }

    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'文件路径错误：{video_path} 不存在'],
            'facts': [],
            'memories': []
        }

    # 设置默认输出目录
    if output_dir is None:
        video_stem = Path(video_path).stem
        output_dir = f"./extracted_frames_{video_stem}"

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 构建ffmpeg命令 - 正确的参数顺序
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'fps={frame_rate}',
        '-q:v', '2' if format == 'jpg' else '0'
    ]
    
    if max_frames:
        cmd.extend(['-frames:v', str(max_frames)])
    
    cmd.append(f'{output_dir}/frame_%04d_%%.2fs.{format}')

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {
                'result': {'error': f'FFmpeg执行失败: {result.stderr}'},
                'insights': ['视频处理失败，请检查视频格式和参数'],
                'facts': [],
                'memories': []
            }

        # 获取抽取的帧列表
        extracted_frames = []
        for file in sorted(os.listdir(output_dir)):
            if file.endswith(f'.{format}'):
                extracted_frames.append(os.path.join(output_dir, file))

        return {
            'result': {
                'success': True,
                'total_extracted': len(extracted_frames),
                'extracted_frames': extracted_frames,
                'output_dir': output_dir,
                'frame_rate': frame_rate,
                'format': format
            },
            'insights': [
                f'成功从视频中抽取了 {len(extracted_frames)} 帧',
                f'输出目录：{output_dir}',
                f'帧率：{frame_rate} fps',
                f'格式：{format}'
            ],
            'facts': [
                ['视频', '包含', f'{len(extracted_frames)} 帧图像'],
                ['抽取任务', '状态', '完成'],
                [video_path, '处理结果', '成功']
            ],
            'memories': [
                f'视频帧抽取任务完成，源视频：{video_path}，输出帧数：{len(extracted_frames)}'
            ]
        }

    except subprocess.TimeoutExpired:
        return {
            'result': {'error': '视频处理超时'},
            'insights': ['视频处理时间过长，请尝试减少帧率或最大帧数'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'未知错误: {str(e)}'},
            'insights': ['视频帧抽取过程中发生异常'],
            'facts': [],
            'memories': []
        }