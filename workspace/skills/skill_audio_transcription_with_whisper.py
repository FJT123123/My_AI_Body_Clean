"""
自动生成的技能模块
需求: 音频转录技能：从音频文件中转录文本，支持多种音频格式（mp3, wav, m4a, flac, ogg, aac），使用whisper模型进行转录。输入参数包括audio_path（必需）、output_dir（可选，默认自动生成）、language（可选，默认'en'）和model_size（可选，默认'base'）。该技能应验证参数契约，检查文件存在性和格式，并返回转录结果、输出文件路径和处理状态。
生成时间: 2026-03-21 22:21:47
"""

# skill_name: audio_transcription_with_whisper

import os
import subprocess
import sys
from typing import Optional, Dict, Any
import json

def main(args=None):
    """
    音频转录技能：从音频文件中转录文本，支持多种音频格式（mp3, wav, m4a, flac, ogg, aac）
    使用whisper模型进行转录。输入参数包括audio_path（必需）、output_dir（可选，默认自动生成）、
    language（可选，默认'en'）和model_size（可选，默认'base'）
    """
    args = args or {}
    
    # 验证参数契约
    audio_path = args.get('audio_path')
    if not audio_path:
        return {
            'result': {'success': False, 'error': 'audio_path参数是必需的'},
            'insights': ['音频转录技能参数验证失败：缺少audio_path参数'],
            'next_skills': []
        }
    
    output_dir = args.get('output_dir', None)
    language = args.get('language', 'en')
    model_size = args.get('model_size', 'base')
    
    # 检查文件存在性
    if not os.path.exists(audio_path):
        return {
            'result': {'success': False, 'error': f'音频文件不存在: {audio_path}'},
            'insights': [f'音频转录技能参数验证失败：音频文件不存在 {audio_path}'],
            'next_skills': []
        }
    
    # 检查音频格式
    supported_formats = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
    file_ext = os.path.splitext(audio_path)[1].lower()
    if file_ext not in supported_formats:
        return {
            'result': {'success': False, 'error': f'不支持的音频格式: {file_ext}, 支持的格式: {supported_formats}'},
            'insights': [f'音频转录技能参数验证失败：不支持的音频格式 {file_ext}'],
            'next_skills': []
        }
    
    # 检查whisper是否已安装
    try:
        import whisper
    except ImportError:
        # 尝试安装whisper
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
            import whisper
        except Exception as e:
            return {
                'result': {'success': False, 'error': f'whisper模型安装失败: {str(e)}'},
                'insights': ['音频转录技能依赖安装失败：whisper库未安装'],
                'next_skills': []
            }
    
    # 检查模型是否可用
    available_models = whisper.available_models()
    if model_size not in available_models:
        return {
            'result': {'success': False, 'error': f'模型大小 {model_size} 不在可用模型中: {available_models}'},
            'insights': [f'音频转录技能参数验证失败：模型大小 {model_size} 不可用'],
            'next_skills': []
        }
    
    # 创建输出目录
    if output_dir is None:
        output_dir = os.path.dirname(audio_path)
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 加载模型
        model = whisper.load_model(model_size)
        
        # 转录音频
        result = model.transcribe(audio_path, language=language)
        
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_file = os.path.join(output_dir, f"{base_name}_transcription.txt")
        
        # 保存转录结果
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        # 生成SRT字幕文件
        srt_file = os.path.join(output_dir, f"{base_name}_transcription.srt")
        with open(srt_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(result['segments'], 1):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                f.write(f"{i}\n{start} --> {end}\n{segment['text']}\n\n")
        
        return {
            'result': {
                'success': True,
                'transcription': result['text'],
                'output_text_file': output_file,
                'output_srt_file': srt_file,
                'language': language,
                'model_size': model_size,
                'duration': result.get('duration', 0)
            },
            'insights': [f'音频转录完成，文件长度: {len(result["text"])} 字符'],
            'memories': [{'event_type': 'skill_executed', 'content': f'音频转录完成: {audio_path} -> {output_file}'}],
            'next_skills': []
        }
    
    except Exception as e:
        return {
            'result': {'success': False, 'error': f'音频转录失败: {str(e)}'},
            'insights': [f'音频转录技能执行失败：{str(e)}'],
            'next_skills': []
        }

def format_timestamp(seconds: float) -> str:
    """格式化时间戳为 SRT 格式"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"