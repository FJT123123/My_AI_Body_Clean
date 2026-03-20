# tool_name: video_processing_error_mapper
from langchain.tools import tool
import json
import sys
import os

@tool
def video_processing_error_mapper(input_args: str) -> dict:
    """
    视频处理错误智能映射工具
    
    用途: 接收视频处理过程中的原始错误信息，调用semantic_error_mapping_capability进行智能错误分类，
          返回标准化的错误类型、根本原因分析和修复建议
    参数: input_args - JSON字符串，包含error_info（必需）、context（可选）、video_path（可选）
    返回值: 包含错误类型、分类结果、修复建议等信息的字典
    """
    try:
        # Parse input parameters
        params = json.loads(input_args)
        error_info = params.get('error_info', '')
        
        if not error_info:
            return {
                "status": "error",
                "message": "缺少 error_info 参数",
                "operation": "video_processing_error_mapper",
                "result": "error"
            }
        
        context = params.get('context', {})
        video_path = params.get('video_path', '')
        
        # Build context data
        if not context:
            context = {
                'system_info': {
                    'os': os.name,
                    'python_version': sys.version
                },
                'parameters': {'video_path': video_path} if video_path else {},
                'dependencies': {}
            }
        
        # Import capability module
        from capabilities.semantic_error_mapping_capability import run_error_mapping_cycle
        
        # Create exception object
        class VideoProcessingError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)
        
        error_obj = VideoProcessingError(error_info)
        
        # Execute error mapping
        result = run_error_mapping_cycle(error_obj, context)
        
        # Format return result
        if result.get('status') == 'success':
            return {
                "status": "success",
                "message": "错误映射成功完成",
                "operation": "video_processing_error_mapper",
                "result": {
                    'error_type': result.get('standardized_error_id', 'UnknownError'),
                    'classification': result.get('classification', {}),
                    'suggestions': result.get('suggestions', []),
                    'confidence_score': result.get('confidence_score', 0.0),
                    'matched_patterns': result.get('matched_patterns', [])
                }
            }
        else:
            return {
                "status": "error",
                "message": f"错误映射失败: {result.get('error_message', 'Unknown error')}",
                "operation": "video_processing_error_mapper",
                "result": "error"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"参数解析或执行错误: {str(e)}",
            "operation": "video_processing_error_mapper",
            "result": "error"
        }