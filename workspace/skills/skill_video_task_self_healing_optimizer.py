"""
自动生成的技能模块
需求: 视频任务自我修复优化技能，包含依赖检查、视频文件验证、错误检测和自动修复功能，专门针对视频时序分析任务的常见问题提供解决方案
生成时间: 2026-03-13 19:15:27
"""

# skill_name: video_task_self_healing_optimizer

import os
import subprocess
import json
import cv2
import numpy as np
from pathlib import Path
import hashlib
import time
from typing import Dict, List, Tuple, Optional


def main(args=None):
    """
    视频任务自我修复优化技能
    检查视频处理依赖、验证视频文件完整性、检测常见错误并提供自动修复功能
    针对视频时序分析任务的常见问题提供解决方案
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 获取视频路径
    video_path = args.get('video_path', '')
    if not video_path or not os.path.exists(video_path):
        return {
            'result': {'error': 'video_path 参数缺失或文件不存在'},
            'insights': ['video_path 是必需参数'],
            'capabilities': ['视频文件验证', '依赖检查', '错误检测'],
            'next_skills': ['skill_video_task_dependency_checker', 'skill_self_healing_task_execution']
        }
    
    # 检查依赖
    dependencies = check_video_dependencies()
    
    # 验证视频文件
    video_info = validate_video_file(video_path)
    
    # 检测错误
    errors = detect_video_errors(video_path, video_info)
    
    # 自动修复
    repairs = auto_repair_video_issues(video_path, errors)
    
    # 优化建议
    optimizations = suggest_video_optimizations(video_path, video_info)
    
    return {
        'result': {
            'dependencies': dependencies,
            'video_info': video_info,
            'errors_detected': errors,
            'repairs_performed': repairs,
            'optimization_suggestions': optimizations
        },
        'insights': [
            f"视频文件验证结果: {video_info['status']}",
            f"检测到 {len(errors)} 个错误",
            f"完成 {len(repairs)} 项修复"
        ],
        'facts': [
            ['video_file', 'has_path', video_path],
            ['video_file', 'has_duration', str(video_info.get('duration', 'unknown'))],
            ['video_file', 'has_resolution', f"{video_info.get('width', 0)}x{video_info.get('height', 0)}"]
        ],
        'memories': [
            f"视频任务自我修复检查完成 - 路径: {video_path}",
            f"依赖检查结果: {dependencies['status']}",
            f"视频验证结果: {video_info['status']}"
        ],
        'capabilities': ['视频依赖检查', '视频文件验证', '错误检测与修复', '性能优化建议'],
        'next_skills': ['skill_video_frame_analyzer', 'skill_video_metadata_extractor'] if errors else []
    }


def check_video_dependencies() -> Dict:
    """检查视频处理所需依赖"""
    dependencies = {
        'ffmpeg': False,
        'opencv': False,
        'ffprobe': False,
        'python_packages': {
            'cv2': False,
            'numpy': False
        }
    }
    
    # 检查系统命令
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        dependencies['ffmpeg'] = result.returncode == 0
    except FileNotFoundError:
        dependencies['ffmpeg'] = False
    
    try:
        result = subprocess.run(['ffprobe', '-version'], capture_output=True, text=True)
        dependencies['ffprobe'] = result.returncode == 0
    except FileNotFoundError:
        dependencies['ffprobe'] = False
    
    # 检查Python包
    try:
        import cv2
        dependencies['python_packages']['cv2'] = True
    except ImportError:
        dependencies['python_packages']['cv2'] = False
    
    try:
        import numpy
        dependencies['python_packages']['numpy'] = True
    except ImportError:
        dependencies['python_packages']['numpy'] = False
    
    status = all([
        dependencies['ffmpeg'],
        dependencies['ffprobe'],
        dependencies['python_packages']['cv2'],
        dependencies['python_packages']['numpy']
    ])
    
    return {
        'status': status,
        'details': dependencies
    }


def validate_video_file(video_path: str) -> Dict:
    """验证视频文件的完整性"""
    try:
        # 使用OpenCV验证
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {
                'status': 'invalid',
                'error': '无法打开视频文件',
                'format': 'unknown',
                'duration': 0,
                'width': 0,
                'height': 0,
                'fps': 0,
                'frame_count': 0
            }
        
        # 获取视频信息
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if fps > 0:
            duration = frame_count / fps
        else:
            duration = 0
        
        # 尝试读取几帧确认文件可读
        frame_read_success = True
        for i in range(min(5, frame_count)):
            ret, frame = cap.read()
            if not ret:
                frame_read_success = False
                break
        
        cap.release()
        
        if not frame_read_success:
            return {
                'status': 'corrupted',
                'error': '视频文件损坏，无法读取帧',
                'format': 'unknown',
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'frame_count': frame_count
            }
        
        # 使用ffprobe获取更详细的格式信息
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', video_path],
                capture_output=True,
                text=True
            )
            format_info = json.loads(result.stdout)
            file_format = format_info.get('format', {}).get('format_name', 'unknown')
        except:
            file_format = 'unknown'
        
        return {
            'status': 'valid',
            'error': None,
            'format': file_format,
            'duration': duration,
            'width': width,
            'height': height,
            'fps': fps,
            'frame_count': frame_count
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'format': 'unknown',
            'duration': 0,
            'width': 0,
            'height': 0,
            'fps': 0,
            'frame_count': 0
        }


def detect_video_errors(video_path: str, video_info: Dict) -> List[Dict]:
    """检测视频文件的常见错误"""
    errors = []
    
    # 检查文件大小
    try:
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            errors.append({
                'type': 'empty_file',
                'description': '视频文件为空',
                'severity': 'critical'
            })
    except:
        errors.append({
            'type': 'file_access_error',
            'description': '无法访问视频文件',
            'severity': 'critical'
        })
    
    # 检查视频信息
    if video_info['status'] == 'invalid':
        errors.append({
            'type': 'invalid_format',
            'description': video_info['error'],
            'severity': 'critical'
        })
    elif video_info['status'] == 'corrupted':
        errors.append({
            'type': 'corrupted_file',
            'description': video_info['error'],
            'severity': 'high'
        })
    else:
        # 检查视频参数合理性
        if video_info['width'] <= 0 or video_info['height'] <= 0:
            errors.append({
                'type': 'invalid_resolution',
                'description': '视频分辨率无效',
                'severity': 'high'
            })
        
        if video_info['fps'] <= 0:
            errors.append({
                'type': 'invalid_fps',
                'description': '视频帧率无效',
                'severity': 'medium'
            })
        
        if video_info['duration'] <= 0:
            errors.append({
                'type': 'invalid_duration',
                'description': '视频时长无效',
                'severity': 'medium'
            })
        
        if video_info['frame_count'] == 0:
            errors.append({
                'type': 'invalid_frame_count',
                'description': '视频帧数为0',
                'severity': 'high'
            })
    
    # 检查视频文件是否被锁定
    try:
        with open(video_path, 'r+b') as f:
            pass
    except PermissionError:
        errors.append({
            'type': 'file_locked',
            'description': '视频文件被其他程序占用',
            'severity': 'medium'
        })
    
    return errors


def auto_repair_video_issues(video_path: str, errors: List[Dict]) -> List[Dict]:
    """自动修复视频文件的常见问题"""
    repairs = []
    
    # 标记是否需要重建视频文件
    needs_rebuild = False
    
    for error in errors:
        if error['type'] == 'corrupted_file':
            # 尝试修复损坏的视频文件
            repair_result = attempt_video_repair(video_path)
            if repair_result['success']:
                repairs.append({
                    'type': 'file_repair',
                    'description': '尝试修复损坏的视频文件',
                    'result': repair_result['message']
                })
                needs_rebuild = True
        
        elif error['type'] == 'invalid_resolution':
            # 如果分辨率无效，尝试重新编码
            repair_result = reencode_video(video_path)
            if repair_result['success']:
                repairs.append({
                    'type': 'reencode',
                    'description': '重新编码视频以修复分辨率',
                    'result': repair_result['message']
                })
        
        elif error['type'] == 'invalid_fps':
            # 如果帧率无效，尝试设置合适的帧率
            repair_result = fix_video_fps(video_path)
            if repair_result['success']:
                repairs.append({
                    'type': 'fps_correction',
                    'description': '修正视频帧率',
                    'result': repair_result['message']
                })
    
    return repairs


def attempt_video_repair(video_path: str) -> Dict:
    """尝试修复损坏的视频文件"""
    try:
        # 创建临时修复后的文件路径
        path_obj = Path(video_path)
        temp_path = f"{path_obj.stem}_fixed{path_obj.suffix}"
        
        # 使用ffmpeg尝试修复视频
        result = subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y', temp_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 替换原文件
            backup_path = f"{video_path}.backup"
            os.rename(video_path, backup_path)
            os.rename(temp_path, video_path)
            
            return {
                'success': True,
                'message': '视频修复成功，原文件已备份'
            }
        else:
            return {
                'success': False,
                'message': f'修复失败: {result.stderr}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'修复异常: {str(e)}'
        }


def reencode_video(video_path: str) -> Dict:
    """重新编码视频文件"""
    try:
        path_obj = Path(video_path)
        temp_path = f"{path_obj.stem}_reencoded{path_obj.suffix}"
        
        # 使用ffmpeg重新编码
        result = subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-y', temp_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # 替换原文件
            backup_path = f"{video_path}.backup"
            os.rename(video_path, backup_path)
            os.rename(temp_path, video_path)
            
            return {
                'success': True,
                'message': '视频重新编码成功，原文件已备份'
            }
        else:
            return {
                'success': False,
                'message': f'重新编码失败: {result.stderr}'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'重新编码异常: {str(e)}'
        }


def fix_video_fps(video_path: str) -> Dict:
    """修正视频帧率"""
    try:
        # 获取当前视频信息
        cap = cv2.VideoCapture(video_path)
        current_fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        # 如果帧率异常，设置一个合理的默认值
        if current_fps <= 0 or current_fps > 120:
            path_obj = Path(video_path)
            temp_path = f"{path_obj.stem}_fixed_fps{path_obj.suffix}"
            
            # 使用ffmpeg设置合理的帧率
            result = subprocess.run([
                'ffmpeg',
                '-i', video_path,
                '-r', '30',  # 设置为30fps
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-y', temp_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                backup_path = f"{video_path}.backup"
                os.rename(video_path, backup_path)
                os.rename(temp_path, video_path)
                
                return {
                    'success': True,
                    'message': '视频帧率修正成功，设置为30fps'
                }
            else:
                return {
                    'success': False,
                    'message': f'帧率修正失败: {result.stderr}'
                }
        else:
            return {
                'success': True,
                'message': '帧率正常，无需修正'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'帧率修正异常: {str(e)}'
        }


def suggest_video_optimizations(video_path: str, video_info: Dict) -> List[Dict]:
    """提供视频优化建议"""
    suggestions = []
    
    # 建议合适的分辨率
    if video_info['width'] > 1920 or video_info['height'] > 1080:
        suggestions.append({
            'type': 'resolution_downscale',
            'description': '视频分辨率过高，建议降采样以提高处理效率',
            'recommended_value': '1920x1080',
            'impact': '性能提升'
        })
    
    # 建议合适的帧率
    if video_info['fps'] > 30:
        suggestions.append({
            'type': 'fps_downscale',
            'description': '视频帧率过高，建议降低以减少计算量',
            'recommended_value': '30fps',
            'impact': '性能提升'
        })
    
    # 建议合适的编码格式
    if video_info['format'] not in ['mp4', 'mov']:
        suggestions.append({
            'type': 'format_recommendation',
            'description': '建议转换为MP4格式以提高兼容性',
            'recommended_value': 'mp4',
            'impact': '兼容性提升'
        })
    
    # 文件大小优化建议
    try:
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        if file_size > 100:  # 超过100MB
            suggestions.append({
                'type': 'compression',
                'description': f'视频文件过大({file_size:.1f}MB)，建议压缩',
                'recommended_value': '使用H.264编码压缩',
                'impact': '存储空间节省'
            })
    except:
        pass
    
    # 内存使用优化建议
    suggestions.append({
        'type': 'processing_strategy',
        'description': '对大视频文件建议使用分段处理',
        'recommended_value': '按时间分段或按帧数分段',
        'impact': '内存使用优化'
    })
    
    return suggestions