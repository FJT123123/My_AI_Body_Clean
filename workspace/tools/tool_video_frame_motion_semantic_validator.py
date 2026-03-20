# tool_name: video_frame_motion_semantic_validator
from typing import Dict, Any, Optional
from langchain.tools import tool
import os

@tool
def video_frame_motion_semantic_validator(
    video_path: str,
    output_dir: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    视频帧间运动语义验证工具
    
    使用motion_semantic_validation_capability能力模块验证视频帧间运动的语义合理性，
    分析视频中帧与帧之间的运动是否符合物理规律和语义连贯性。
    
    Args:
        video_path (str): 输入视频文件路径
        output_dir (str, optional): 输出分析结果的目录
        config (dict, optional): 验证配置参数
    
    Returns:
        dict: 包含运动语义验证结果的字典，包含运动一致性分析、
              帧间变化合理性判断等信息
    """
    # === 参数契约验证 ===
    if not video_path:
        return {
            'result': {'error': '缺少 video_path 参数'},
            'insights': ['参数校验失败：必须提供 video_path'],
            'facts': [],
            'memories': []
        }
    elif not isinstance(video_path, str):
        return {
            'result': {'error': 'video_path 参数类型错误，应为字符串'},
            'insights': ['参数校验失败：video_path 必须是字符串类型'],
            'facts': [],
            'memories': []
        }
    elif video_path.strip() == "":
        return {
            'result': {'error': 'video_path 参数不能为空字符串'},
            'insights': ['参数校验失败：video_path 不能为空'],
            'facts': [],
            'memories': []
        }
    
    # 检查文件是否存在
    if not os.path.exists(video_path):
        return {
            'result': {'error': f'视频文件不存在: {video_path}'},
            'insights': [f'参数校验失败：视频文件 {video_path} 不存在'],
            'facts': [],
            'memories': []
        }
    
    try:
        import sys
        import importlib.util
        
        # 运行时注入 capability
        spec = importlib.util.find_spec("motion_semantic_validation_capability")
        if spec is None:
            raise ImportError("motion_semantic_validation_capability not found")
        
        motion_semantic_module = importlib.util.module_from_spec(spec)
        sys.modules["motion_semantic_validation_capability"] = motion_semantic_module
        spec.loader.exec_module(motion_semantic_module)
        
        # 调用 capability 的验证功能
        if config is not None:
            result = motion_semantic_module.check_video_motion_semantics(
                video_path=video_path,
                config=config
            )
        else:
            result = motion_semantic_module.check_video_motion_semantics(video_path=video_path)
        
        # 确保所有数值类型都可以JSON序列化
        def ensure_json_serializable(obj):
            import numpy as np
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, dict):
                return {key: ensure_json_serializable(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [ensure_json_serializable(item) for item in obj]
            else:
                return obj
        
        # 标准化返回格式以符合双向数据流协议
        serialized_result = ensure_json_serializable(result)
        return {
            'result': serialized_result,
            'insights': [f'成功执行视频帧间运动语义验证: {video_path}'],
            'facts': [f'video_frame_motion_semantic_validation_completed_for_{video_path}'],
            'memories': [f'validated_motion_semantics_for_{video_path}']
        }
        
    except ImportError as e:
        return {
            'result': {'error': f'Failed to import motion_semantic_validation_capability: {str(e)}'},
            'insights': ['能力模块导入失败'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        return {
            'result': {'error': f'Video motion semantic validation failed: {str(e)}'},
            'insights': [f'视频运动语义验证失败: {str(e)}'],
            'facts': [],
            'memories': []
        }