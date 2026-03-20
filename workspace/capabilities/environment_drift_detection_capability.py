# Environment Drift Detection and Adaptive Calibration Capability

import json
import os
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib

class EnvironmentDriftDetector:
    """环境漂移检测器，用于监控视频处理参数的变化和漂移"""
    
    def __init__(self, baseline_data_path: str = "./environment_baseline.json"):
        self.baseline_data_path = baseline_data_path
        self.baseline_data = self._load_baseline_data()
        self.drift_thresholds = {
            'codec_performance': 0.15,  # 15% 性能变化视为漂移
            'memory_usage': 0.20,      # 20% 内存使用变化视为漂移
            'processing_time': 0.25,   # 25% 处理时间变化视为漂移
            'quality_metrics': 0.10,   # 10% 质量指标变化视为漂移
            'hardware_acceleration': 0.30  # 30% 硬件加速效率变化视为漂移
        }
    
    def _load_baseline_data(self) -> Dict[str, Any]:
        """加载基线环境数据"""
        if os.path.exists(self.baseline_data_path):
            with open(self.baseline_data_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_baseline_data(self, data: Dict[str, Any]):
        """保存基线环境数据"""
        with open(self.baseline_data_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def establish_baseline(self, environment_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """建立环境基线"""
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'metrics': environment_metrics,
            'system_info': {
                'os': os.name,
                'python_version': os.sys.version if hasattr(os, 'sys') else 'unknown',
                'hardware_info': self._get_hardware_info()
            }
        }
        self.baseline_data = baseline
        self._save_baseline_data(baseline)
        return baseline
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            import psutil
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:\\').total
            }
        except ImportError:
            return {'error': 'psutil not available'}
    
    def detect_drift(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """检测环境漂移"""
        if not self.baseline_data:
            return {
                'drift_detected': False,
                'message': 'No baseline established',
                'recommendations': ['Establish baseline first']
            }
        
        baseline_metrics = self.baseline_data['metrics']
        drift_results = {}
        significant_drift = False
        
        for metric_key, current_value in current_metrics.items():
            if metric_key in baseline_metrics:
                baseline_value = baseline_metrics[metric_key]
                threshold = self.drift_thresholds.get(metric_key, 0.15)
                
                if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                    if baseline_value != 0:
                        relative_change = abs(current_value - baseline_value) / abs(baseline_value)
                        drift_detected = relative_change > threshold
                        if drift_detected:
                            significant_drift = True
                        drift_results[metric_key] = {
                            'baseline_value': baseline_value,
                            'current_value': current_value,
                            'relative_change': relative_change,
                            'threshold': threshold,
                            'drift_detected': drift_detected
                        }
                    else:
                        # 基线值为0的情况，使用绝对变化
                        absolute_change = abs(current_value)
                        drift_detected = absolute_change > threshold
                        if drift_detected:
                            significant_drift = True
                        drift_results[metric_key] = {
                            'baseline_value': baseline_value,
                            'current_value': current_value,
                            'absolute_change': absolute_change,
                            'threshold': threshold,
                            'drift_detected': drift_detected
                        }
                elif isinstance(current_value, dict) and isinstance(baseline_value, dict):
                    # 递归处理嵌套字典
                    nested_drift = self._detect_nested_drift(baseline_value, current_value, threshold)
                    if nested_drift.get('drift_detected', False):
                        significant_drift = True
                    drift_results[metric_key] = nested_drift
        
        return {
            'drift_detected': significant_drift,
            'drift_details': drift_results,
            'timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(drift_results) if significant_drift else []
        }
    
    def _detect_nested_drift(self, baseline_dict: Dict, current_dict: Dict, default_threshold: float) -> Dict[str, Any]:
        """检测嵌套字典中的漂移"""
        nested_drift = {}
        significant_drift = False
        
        all_keys = set(baseline_dict.keys()) | set(current_dict.keys())
        for key in all_keys:
            if key in baseline_dict and key in current_dict:
                baseline_val = baseline_dict[key]
                current_val = current_dict[key]
                
                if isinstance(current_val, (int, float)) and isinstance(baseline_val, (int, float)):
                    if baseline_val != 0:
                        relative_change = abs(current_val - baseline_val) / abs(baseline_val)
                        threshold = self.drift_thresholds.get(key, default_threshold)
                        drift_detected = relative_change > threshold
                        if drift_detected:
                            significant_drift = True
                        nested_drift[key] = {
                            'baseline_value': baseline_val,
                            'current_value': current_val,
                            'relative_change': relative_change,
                            'threshold': threshold,
                            'drift_detected': drift_detected
                        }
            elif key in baseline_dict:
                nested_drift[key] = {
                    'baseline_value': baseline_dict[key],
                    'current_value': None,
                    'drift_detected': True,
                    'message': 'Key missing in current metrics'
                }
                significant_drift = True
            elif key in current_dict:
                nested_drift[key] = {
                    'baseline_value': None,
                    'current_value': current_dict[key],
                    'drift_detected': True,
                    'message': 'New key in current metrics'
                }
                significant_drift = True
        
        return {
            'drift_detected': significant_drift,
            'nested_drift': nested_drift
        }
    
    def _generate_recommendations(self, drift_results: Dict[str, Any]) -> List[str]:
        """基于漂移结果生成建议"""
        recommendations = []
        
        for metric_key, drift_info in drift_results.items():
            if drift_info.get('drift_detected', False):
                if metric_key == 'codec_performance':
                    recommendations.append('Consider switching to alternative codec or adjusting quality parameters')
                elif metric_key == 'memory_usage':
                    recommendations.append('Reduce batch size or optimize memory allocation')
                elif metric_key == 'processing_time':
                    recommendations.append('Adjust processing parameters or enable hardware acceleration')
                elif metric_key == 'quality_metrics':
                    recommendations.append('Recalibrate quality parameters based on current environment')
                elif metric_key == 'hardware_acceleration':
                    recommendations.append('Verify hardware acceleration settings or fallback to software processing')
                else:
                    recommendations.append(f'Recalibrate {metric_key} parameters for current environment')
        
        return recommendations


class AdaptiveParameterCalibrator:
    """自适应参数校准器，基于环境漂移检测结果调整视频处理参数"""
    
    def __init__(self, drift_detector: EnvironmentDriftDetector):
        self.drift_detector = drift_detector
        self.parameter_mapping = {
            'codec_performance': ['target_codec', 'quality_factor', 'bitrate'],
            'memory_usage': ['batch_size', 'buffer_size', 'frame_cache_size'],
            'processing_time': ['target_framerate', 'resolution_scale', 'processing_threads'],
            'quality_metrics': ['quality_factor', 'sharpness', 'denoise_level'],
            'hardware_acceleration': ['use_hardware_acceleration', 'gpu_memory_limit']
        }
    
    def calibrate_parameters(self, original_params: Dict[str, Any], drift_report: Dict[str, Any]) -> Dict[str, Any]:
        """根据漂移报告校准参数"""
        calibrated_params = original_params.copy()
        
        if not drift_report.get('drift_detected', False):
            return calibrated_params
        
        drift_details = drift_report.get('drift_details', {})
        
        for metric_key, drift_info in drift_details.items():
            if drift_info.get('drift_detected', False):
                affected_params = self.parameter_mapping.get(metric_key, [])
                for param_name in affected_params:
                    if param_name in calibrated_params:
                        calibrated_params[param_name] = self._adjust_parameter(
                            param_name, 
                            calibrated_params[param_name], 
                            drift_info
                        )
        
        return calibrated_params
    
    def _adjust_parameter(self, param_name: str, current_value: Any, drift_info: Dict[str, Any]) -> Any:
        """调整单个参数值"""
        if isinstance(current_value, (int, float)):
            relative_change = drift_info.get('relative_change', 0)
            if relative_change > 0:
                # 性能下降，需要降低要求
                adjustment_factor = 1.0 - min(relative_change, 0.5)  # 最多降低50%
            else:
                # 性能提升，可以提高要求
                adjustment_factor = 1.0 + min(abs(relative_change), 0.3)  # 最多提高30%
            
            if isinstance(current_value, int):
                return int(current_value * adjustment_factor)
            else:
                return current_value * adjustment_factor
        
        # 对于布尔值或字符串，保持原样
        return current_value


def run_environment_drift_detection_cycle(environment_metrics: Dict[str, Any], 
                                        establish_baseline: bool = False) -> Dict[str, Any]:
    """
    执行环境漂移检测周期
    
    Args:
        environment_metrics: 当前环境指标
        establish_baseline: 是否建立新的基线
        
    Returns:
        漂移检测结果
    """
    detector = EnvironmentDriftDetector()
    
    if establish_baseline:
        baseline = detector.establish_baseline(environment_metrics)
        return {
            'status': 'success',
            'message': 'Baseline established successfully',
            'baseline': baseline
        }
    
    drift_report = detector.detect_drift(environment_metrics)
    return {
        'status': 'success',
        'message': 'Drift detection completed',
        'drift_report': drift_report
    }


def run_adaptive_calibration_cycle(original_params: Dict[str, Any], 
                                 environment_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行自适应校准周期
    
    Args:
        original_params: 原始参数
        environment_metrics: 当前环境指标
        
    Returns:
        校准后的参数和相关信息
    """
    detector = EnvironmentDriftDetector()
    calibrator = AdaptiveParameterCalibrator(detector)
    
    # 先检测漂移
    drift_report = detector.detect_drift(environment_metrics)
    
    # 如果没有漂移，返回原始参数
    if not drift_report.get('drift_detected', False):
        return {
            'status': 'success',
            'message': 'No drift detected, using original parameters',
            'calibrated_params': original_params,
            'drift_report': drift_report
        }
    
    # 执行校准
    calibrated_params = calibrator.calibrate_parameters(original_params, drift_report)
    
    return {
        'status': 'success',
        'message': 'Parameters calibrated based on environment drift',
        'original_params': original_params,
        'calibrated_params': calibrated_params,
        'drift_report': drift_report
    }


# 视频处理特定的环境指标收集函数
def collect_video_processing_environment_metrics(video_path: str, 
                                               test_duration: int = 5) -> Dict[str, Any]:
    """
    收集视频处理环境指标
    
    Args:
        video_path: 测试视频路径
        test_duration: 测试持续时间（秒）
        
    Returns:
        环境指标字典
    """
    import subprocess
    import time
    import cv2
    
    metrics = {}
    
    try:
        # 获取视频基本信息
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            metrics.update({
                'video_info': {
                    'fps': fps,
                    'frame_count': frame_count,
                    'width': width,
                    'height': height,
                    'duration': duration
                }
            })
        
        # 测试编解码器性能
        start_time = time.time()
        start_memory = get_current_memory_usage()
        
        # 使用ffmpeg进行简短的转码测试
        output_path = video_path.replace('.mp4', '_test_output.mp4')
        cmd = [
            'ffmpeg', '-y', '-i', video_path, 
            '-t', str(min(test_duration, duration if duration > 0 else test_duration)),
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            output_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=test_duration + 10)
            processing_time = time.time() - start_time
            end_memory = get_current_memory_usage()
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                os.remove(output_path)
                
                metrics.update({
                    'codec_performance': {
                        'processing_time': processing_time,
                        'memory_usage_delta': end_memory - start_memory,
                        'output_file_size': file_size,
                        'throughput_fps': min(test_duration, duration) * fps / processing_time if processing_time > 0 else 0
                    }
                })
            else:
                metrics['codec_performance_error'] = result.stderr
                
        except subprocess.TimeoutExpired:
            metrics['codec_performance_error'] = 'Timeout during codec performance test'
            if os.path.exists(output_path):
                os.remove(output_path)
        
        # 检测硬件加速支持
        hardware_accel_info = detect_hardware_acceleration_support()
        metrics['hardware_acceleration'] = hardware_accel_info
        
    except Exception as e:
        metrics['collection_error'] = str(e)
    
    return metrics


def get_current_memory_usage() -> float:
    """获取当前内存使用量（MB）"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


def detect_hardware_acceleration_support() -> Dict[str, Any]:
    """检测硬件加速支持"""
    hardware_info = {
        'cuda_available': False,
        'opencl_available': False,
        'vaapi_available': False,
        'qsv_available': False
    }
    
    try:
        # 检测CUDA
        import subprocess
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        hardware_info['cuda_available'] = result.returncode == 0
    except:
        pass
    
    try:
        # 检测VA-API (Linux)
        result = subprocess.run(['vainfo'], capture_output=True, text=True)
        hardware_info['vaapi_available'] = result.returncode == 0
    except:
        pass
    
    try:
        # 检测Intel QSV
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'], capture_output=True, text=True)
        if 'h264_qsv' in result.stdout or 'hevc_qsv' in result.stdout:
            hardware_info['qsv_available'] = True
    except:
        pass
    
    return hardware_info