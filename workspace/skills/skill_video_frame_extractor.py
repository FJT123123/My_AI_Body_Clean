"""
自动生成的技能模块
需求: 从视频文件中按指定时间间隔、帧率或特定时间点精确抽取帧序列，并为每帧附加精确时间戳。支持批量处理、自定义输出格式和元数据保存。该技能专注于高效、精确的帧抽取，不包含错误修复功能。
生成时间: 2026-03-13 19:23:35
"""

# skill_name: video_frame_extractor

def main(args=None):
    """
    从视频文件中按指定时间间隔、帧率或特定时间点精确抽取帧序列，并为每帧附加精确时间戳。
    支持批量处理、自定义输出格式和元数据保存。该技能专注于高效、精确的帧抽取。
    
    参数:
    - video_path: 输入视频文件路径
    - output_dir: 输出目录路径
    - interval: 抽取时间间隔（秒），默认为1
    - specific_times: 特定时间点列表（秒），如 [10, 20, 30]
    - fps: 目标帧率，按此帧率抽取
    - format: 输出格式（jpg, png等）
    """
    import os
    import subprocess
    import json
    import time
    from datetime import datetime
    
    import json
    
    # 调试：打印接收到的args
    print(f"DEBUG: Received args: {args}")
    print(f"DEBUG: Type of args: {type(args)}")
    
    # 解析实际参数
    actual_args = {}
    if isinstance(args, dict) and 'input' in args:
        try:
            # input 是 JSON 字符串
            actual_args = json.loads(args['input'])
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，使用空字典
            actual_args = {}
    elif isinstance(args, str):
        try:
            actual_args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            actual_args = {}
    elif isinstance(args, dict):
        actual_args = args
    else:
        actual_args = {}
    
    # 获取参数
    video_path = actual_args.get('video_path')
    output_dir = actual_args.get('output_dir', './extracted_frames')
    interval = actual_args.get('interval', 1)
    specific_times = actual_args.get('specific_times', [])
    fps = actual_args.get('fps', None)
    format = actual_args.get('format', 'jpg')
    
    if not video_path:
        return {
            'result': {'error': f'缺少 video_path 参数, args={args}, type={type(args)}'},
            'insights': ['参数校验失败：必须提供视频文件路径'],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'视频文件路径无效：{video_path}'],
            'facts': [],
            'memories': []
        }
    
    # 检查ffmpeg是否安装
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return {
            'result': {'error': 'ffmpeg未安装或不可用'},
            'insights': ['ffmpeg未安装，需要先安装ffmpeg'],
            'facts': [],
            'memories': []
        }
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取视频信息
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', video_path
        ], capture_output=True, text=True)
        
        video_info = json.loads(result.stdout)
        video_stream = next((stream for stream in video_info['streams'] if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            return {
                'result': {'error': '视频文件中未找到视频流'},
                'insights': ['输入文件可能不是视频文件或损坏'],
                'facts': [],
                'memories': []
            }
        
        duration = float(video_info['format'].get('duration', 0))
        fps_info = eval(video_stream.get('avg_frame_rate', '0/0'))
        
    except Exception as e:
        return {
            'result': {'error': f'读取视频信息失败: {str(e)}'},
            'insights': ['读取视频元数据时出错'],
            'facts': [],
            'memories': []
        }
    
    # 构建ffmpeg命令
    extracted_frames = []
    metadata = []
    
    try:
        if specific_times:
            # 按特定时间点抽取
            for i, time_point in enumerate(specific_times):
                output_path = os.path.join(output_dir, f'frame_{i:04d}_{time_point}s.{format}')
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-ss', str(time_point),
                    '-vframes', '1',
                    '-y',  # 覆盖已存在的文件
                    output_path
                ]
                
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists(output_path):
                    frame_info = {
                        'frame_index': i,
                        'time_point': time_point,
                        'output_path': output_path,
                        'timestamp': datetime.fromtimestamp(time.time()).isoformat()
                    }
                    extracted_frames.append(output_path)
                    metadata.append(frame_info)
        elif fps:
            # 按目标帧率抽取
            output_pattern = os.path.join(output_dir, f'frame_%04d.{format}')
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'fps={fps}',
                '-y',
                output_pattern
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 获取生成的帧文件
            for file in sorted(os.listdir(output_dir)):
                if file.endswith(f'.{format}'):
                    frame_path = os.path.join(output_dir, file)
                    extracted_frames.append(frame_path)
            
            # 计算时间戳
            if duration > 0:
                total_frames = len(extracted_frames)
                interval = duration / total_frames if total_frames > 0 else 0
                
                for i, frame_path in enumerate(extracted_frames):
                    time_point = i * interval
                    frame_info = {
                        'frame_index': i,
                        'time_point': time_point,
                        'output_path': frame_path,
                        'timestamp': datetime.fromtimestamp(time.time()).isoformat()
                    }
                    metadata.append(frame_info)
        else:
            # 按时间间隔抽取
            output_pattern = os.path.join(output_dir, f'frame_%04d.{format}')
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'thumbnail,scale=640:360',
                '-r', f'1/{interval}',
                '-y',
                output_pattern
            ]
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 另一种抽取方式 - 更精确控制
            frame_count = 0
            current_time = 0
            while current_time <= duration:
                output_path = os.path.join(output_dir, f'frame_{frame_count:04d}_{current_time:.2f}s.{format}')
                
                cmd = [
                    'ffmpeg', '-i', video_path,
                    '-ss', str(current_time),
                    '-vframes', '1',
                    '-y',
                    output_path
                ]
                
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                if os.path.exists(output_path):
                    frame_info = {
                        'frame_index': frame_count,
                        'time_point': current_time,
                        'output_path': output_path,
                        'timestamp': datetime.fromtimestamp(time.time()).isoformat()
                    }
                    extracted_frames.append(output_path)
                    metadata.append(frame_info)
                    frame_count += 1
                
                current_time += interval
    
    except Exception as e:
        return {
            'result': {'error': f'帧抽取失败: {str(e)}'},
            'insights': [f'帧抽取过程中出错：{str(e)}'],
            'facts': [],
            'memories': []
        }
    
    # 保存元数据
    metadata_path = os.path.join(output_dir, 'frame_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            'video_source': video_path,
            'extract_method': 'interval' if not specific_times and not fps else ('specific_times' if specific_times else 'fps'),
            'total_frames': len(extracted_frames),
            'extracted_frames': metadata
        }, f, ensure_ascii=False, indent=2)
    
    # 返回结果
    result_data = {
        'total_extracted': len(extracted_frames),
        'extracted_frames': extracted_frames,
        'metadata_path': metadata_path,
        'video_duration': duration,
        'output_dir': output_dir
    }
    
    insights = [
        f'成功从视频中抽取了 {len(extracted_frames)} 帧',
        f'输出目录：{output_dir}',
        f'视频时长：{duration:.2f} 秒'
    ]
    
    return {
        'result': result_data,
        'insights': insights,
        'facts': [
            ['视频', '包含', f'{len(extracted_frames)} 帧图像'],
            ['抽取任务', '状态', '完成'],
            [video_path, '处理结果', '成功']
        ],
        'memories': [
            f'视频帧抽取任务完成，源视频：{video_path}，输出帧数：{len(extracted_frames)}'
        ]
    }