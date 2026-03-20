# tool_name: smart_video_repair_tool
import json
import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any, List
from langchain.tools import tool


def analyze_video_issues(video_path: str) -> Dict[str, Any]:
    """分析视频问题"""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_format', '-show_streams', video_path
        ], capture_output=True, text=True, check=True)
        
        metadata = json.loads(result.stdout)
        
        # 提取视频和音频流
        video_stream = None
        audio_stream = None
        for stream in metadata.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
            elif stream.get('codec_type') == 'audio':
                audio_stream = stream
        
        issues = {
            'has_video': video_stream is not None,
            'has_audio': audio_stream is not None,
            'video_codec': video_stream.get('codec_name', '') if video_stream else '',
            'audio_codec': audio_stream.get('codec_name', '') if audio_stream else '',
            'width': int(video_stream.get('width', 0)) if video_stream else 0,
            'height': int(video_stream.get('height', 0)) if video_stream else 0,
            'duration': float(metadata['format'].get('duration', 0)),
            'format_name': metadata['format'].get('format_name', ''),
            'issues': []
        }
        
        # 检测常见问题
        if not issues['has_video']:
            issues['issues'].append('no_video_stream')
        if not issues['has_audio']:
            issues['issues'].append('no_audio_stream')
            
        # 检查不支持的编解码器
        supported_video_codecs = ['h264', 'hevc', 'vp8', 'vp9', 'av1', 'mpeg4']
        if issues['video_codec'] and issues['video_codec'].lower() not in supported_video_codecs:
            issues['issues'].append(f'unsupported_video_codec_{issues["video_codec"]}')
            
        supported_audio_codecs = ['aac', 'mp3', 'opus', 'vorbis', 'pcm_s16le']
        if issues['audio_codec'] and issues['audio_codec'].lower() not in supported_audio_codecs:
            issues['issues'].append(f'unsupported_audio_codec_{issues["audio_codec"]}')
            
        return issues
    except Exception as e:
        return {'error': str(e), 'issues': ['analysis_failed']}


def add_silent_audio(input_path: str, output_path: str) -> bool:
    """为无声视频添加静音音频轨道"""
    try:
        cmd = [
            'ffmpeg', '-y', '-v', 'quiet',
            '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
            '-i', input_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def convert_codec(input_path: str, output_path: str, target_codec: str = 'h264') -> bool:
    """转换视频编解码器"""
    try:
        # 确定编码器参数
        encoder_map = {
            'h264': 'libx264',
            'hevc': 'libx265',
            'vp8': 'libvpx',
            'vp9': 'libvpx-vp9',
            'av1': 'libaom-av1'
        }
        
        encoder = encoder_map.get(target_codec.lower(), 'libx264')
        
        cmd = [
            'ffmpeg', '-y', '-v', 'quiet',
            '-i', input_path,
            '-c:v', encoder,
            '-c:a', 'aac',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def repair_video(input_path: str, output_path: str, fixes: List[str]) -> bool:
    """应用修复措施"""
    temp_path = input_path
    temp_files = []
    
    try:
        # 应用修复
        for fix in fixes:
            if fix == 'no_audio_stream':
                # 添加静音音频
                temp_output = tempfile.mktemp(suffix='.mp4')
                temp_files.append(temp_output)
                if not add_silent_audio(temp_path, temp_output):
                    return False
                temp_path = temp_output
            elif fix.startswith('unsupported_video_codec_'):
                # 转换视频编解码器
                temp_output = tempfile.mktemp(suffix='.mp4')
                temp_files.append(temp_output)
                if not convert_codec(temp_path, temp_output, 'h264'):
                    return False
                temp_path = temp_output
            elif fix.startswith('unsupported_audio_codec_'):
                # 转换音频编解码器
                temp_output = tempfile.mktemp(suffix='.mp4')
                temp_files.append(temp_output)
                # 使用默认的aac编码
                cmd = [
                    'ffmpeg', '-y', '-v', 'quiet',
                    '-i', temp_path,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    temp_output
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    return False
                temp_path = temp_output
        
        # 复制最终结果到输出路径
        shutil.copy2(temp_path, output_path)
        return True
    finally:
        # 清理临时文件
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


@tool
def smart_video_repair_tool(input_args: str = "") -> Dict[str, Any]:
    """
    智能视频修复工具
    能够根据视频验证结果自动选择并应用适当的修复策略
    
    参数:
    - input_video_path (str, required): 输入视频文件路径
    - output_video_path (str, optional): 输出视频文件路径，如果不提供则自动生成
    - target_codec (str, optional): 目标视频编解码器 (如 'h264', 'hevc')
    - add_silent_audio (bool, optional): 是否为无声视频添加静音音频轨道
    - target_resolution (str, optional): 目标分辨率 (如 '1920x1080')
    - target_framerate (float, optional): 目标帧率
    - force_repair (bool, optional): 是否强制修复即使没有检测到问题
    
    返回值:
    - repaired_video_path: 修复后的视频路径
    - applied_fixes: 应用的修复列表
    - original_metadata: 原始视频元数据
    - new_metadata: 修复后视频元数据
    - success: 是否成功修复
    """
    # 解析输入参数
    if isinstance(input_args, str):
        try:
            params = json.loads(input_args) if input_args else {}
        except json.JSONDecodeError:
            params = {}
    else:
        params = input_args if isinstance(input_args, dict) else {}
    
    # 验证必需参数
    input_video_path = params.get('input_video_path')
    if not input_video_path:
        return {
            'result': {'error': '缺少 input_video_path 参数'},
            'insights': ['参数校验失败：必须提供input_video_path'],
            'facts': [],
            'memories': []
        }
    
    if not os.path.exists(input_video_path):
        return {
            'result': {'error': f'输入视频文件不存在: {input_video_path}'},
            'insights': ['指定的视频文件路径不存在'],
            'facts': [],
            'memories': []
        }
    
    # 设置输出路径
    output_video_path = params.get('output_video_path')
    if not output_video_path:
        base_name = os.path.splitext(input_video_path)[0]
        output_video_path = f"{base_name}_repaired.mp4"
    
    # 获取其他参数
    target_codec = params.get('target_codec', 'h264')
    add_silent_audio_param = params.get('add_silent_audio', False)
    force_repair = params.get('force_repair', False)
    
    # 分析视频问题
    analysis = analyze_video_issues(input_video_path)
    if 'error' in analysis:
        return {
            'result': {'error': f'视频分析失败: {analysis["error"]}'},
            'insights': ['无法分析视频文件'],
            'facts': [],
            'memories': []
        }
    
    # 确定需要应用的修复
    fixes_to_apply = []
    
    # 检查是否需要添加静音音频
    if add_silent_audio_param or (analysis['issues'] and 'no_audio_stream' in analysis['issues']):
        fixes_to_apply.append('no_audio_stream')
    
    # 检查是否需要转换编解码器
    for issue in analysis['issues']:
        if issue.startswith('unsupported_'):
            fixes_to_apply.append(issue)
    
    # 如果没有问题且不强制修复，则直接复制文件
    if not fixes_to_apply and not force_repair:
        try:
            shutil.copy2(input_video_path, output_video_path)
            return {
                'result': {
                    'repaired_video_path': output_video_path,
                    'applied_fixes': [],
                    'original_metadata': analysis,
                    'new_metadata': analysis,
                    'success': True
                },
                'insights': ['视频无需修复，已直接复制'],
                'facts': [['video_repair', 'status', 'no_repair_needed']],
                'memories': [f'视频修复: {input_video_path} -> {output_video_path} (无需修复)']
            }
        except Exception as e:
            return {
                'result': {'error': f'复制文件失败: {str(e)}'},
                'insights': ['无法复制视频文件'],
                'facts': [],
                'memories': []
            }
    
    # 执行修复
    success = repair_video(input_video_path, output_video_path, fixes_to_apply)
    
    if not success:
        return {
            'result': {'error': '视频修复失败'},
            'insights': ['无法应用修复措施'],
            'facts': [],
            'memories': []
        }
    
    # 获取修复后的元数据
    new_analysis = analyze_video_issues(output_video_path)
    
    return {
        'result': {
            'repaired_video_path': output_video_path,
            'applied_fixes': fixes_to_apply,
            'original_metadata': analysis,
            'new_metadata': new_analysis,
            'success': True
        },
        'insights': [
            f'成功修复视频: {input_video_path} -> {output_video_path}',
            f'应用的修复: {", ".join(fixes_to_apply) if fixes_to_apply else "无"}'
        ],
        'facts': [
            ['video_repair', 'input_path', input_video_path],
            ['video_repair', 'output_path', output_video_path],
            ['video_repair', 'applied_fixes', str(fixes_to_apply)],
            ['video_repair', 'success', 'true']
        ],
        'memories': [
            f'视频修复完成: {input_video_path} -> {output_video_path}, 修复: {fixes_to_apply}'
        ]
    }