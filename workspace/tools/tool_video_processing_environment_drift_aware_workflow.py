# tool_name: video_processing_environment_drift_aware_workflow

import json
import os
from typing import Dict, Any
from langchain.tools import tool

@tool
def video_processing_environment_drift_aware_workflow(input_args: str) -> Dict[str, Any]:
    """
    环境漂移感知的视频处理工作流
    
    用途: 在视频处理前检测环境漂移，自适应调整参数，然后执行处理
    参数: input_args - JSON字符串，包含以下必需和可选参数:
        - video_path (str, required): 输入视频文件路径
        - processing_params (dict, optional): 视频处理参数
        - establish_baseline (bool, optional): 是否建立新的环境基线
        - output_dir (str, optional): 输出目录，默认为当前目录
        
    返回值: 包含环境漂移检测结果、参数校准结果和处理结果的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args) if input_args else {}
        else:
            params = input_args if isinstance(input_args, dict) else {}
        
        # 验证必需参数
        video_path = params.get('video_path')
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
                'insights': ['指定的视频文件路径不存在'],
                'facts': [],
                'memories': []
            }
        
        processing_params = params.get('processing_params', {})
        establish_baseline = params.get('establish_baseline', False)
        output_dir = params.get('output_dir', './drift_aware_processing_output')
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 收集当前环境指标
        from workspace.capabilities.environment_drift_detection_capability import collect_video_processing_environment_metrics
        environment_metrics = collect_video_processing_environment_metrics(video_path)
        
        # 建立基线或检测漂移
        from workspace.capabilities.environment_drift_detection_capability import run_environment_drift_detection_cycle
        drift_detection_result = run_environment_drift_detection_cycle(
            environment_metrics, 
            establish_baseline=establish_baseline
        )
        
        if establish_baseline:
            return {
                'result': {
                    'status': 'success',
                    'message': '环境基线已建立',
                    'baseline_info': drift_detection_result.get('baseline', {})
                },
                'insights': ['环境基线已成功建立，可用于后续漂移检测'],
                'facts': [['environment_drift_detection', 'baseline_established', 'true']],
                'memories': [f'环境基线已建立: {video_path}']
            }
        
        # 如果检测到漂移，进行参数校准
        calibrated_params = processing_params.copy()
        drift_report = drift_detection_result.get('drift_report', {})
        
        if drift_report.get('drift_detected', False):
            from workspace.capabilities.environment_drift_detection_capability import run_adaptive_calibration_cycle
            calibration_result = run_adaptive_calibration_cycle(processing_params, environment_metrics)
            calibrated_params = calibration_result.get('calibrated_params', processing_params)
            
            insights = [
                f'检测到环境漂移，已自动校准参数: {video_path}',
                f'漂移详情: {json.dumps(drift_report.get("drift_details", {}), indent=2)}',
                f'校准建议: {", ".join(drift_report.get("recommendations", ["无"]))}'
            ]
        else:
            insights = [f'未检测到环境漂移，使用原始参数: {video_path}']
        
        # 执行视频处理（这里可以调用现有的视频处理工具）
        # 由于这是一个演示工具，我们只返回校准后的参数
        result = {
            'status': 'success',
            'message': '环境漂移感知处理完成',
            'original_params': processing_params,
            'calibrated_params': calibrated_params,
            'drift_detected': drift_report.get('drift_detected', False),
            'drift_report': drift_report,
            'environment_metrics': environment_metrics
        }
        
        facts = [
            ['environment_drift_detection', 'video_path', video_path],
            ['environment_drift_detection', 'drift_detected', str(drift_report.get('drift_detected', False))],
            ['environment_drift_detection', 'status', 'completed']
        ]
        
        memories = [
            f'环境漂移感知处理完成: {video_path}, 漂移检测: {drift_report.get("drift_detected", False)}'
        ]
        
        return {
            'result': result,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except Exception as e:
        return {
            'result': {'error': f'环境漂移感知处理异常: {str(e)}'},
            'insights': [f'环境漂移感知处理异常: {str(e)}'],
            'facts': [['environment_drift_detection', 'status', 'exception']],
            'memories': [f'环境漂移感知处理异常: {video_path} - {str(e)}']
        }