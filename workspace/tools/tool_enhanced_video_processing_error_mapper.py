# tool_name: enhanced_video_processing_error_mapper
from langchain.tools import tool
import json

@tool
def enhanced_video_processing_error_mapper(input_args: str) -> dict:
    """
    增强版视频处理错误智能映射工具
    
    用途: 接收视频处理过程中的原始错误信息，使用enhanced_video_error_classification_capability进行精细化错误分类，
          返回标准化的错误类型、根本原因分析和针对性修复建议
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
                "operation": "enhanced_video_processing_error_mapper",
                "result": "error"
            }
        
        context = params.get('context', {})
        video_path = params.get('video_path', '')
        
        # Import enhanced capability module
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from capabilities.enhanced_video_error_classification_capability import run_enhanced_error_mapping_cycle
        
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
        
        # Create exception object
        class VideoProcessingError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)
        
        error_obj = VideoProcessingError(error_info)
        
        # Execute enhanced error mapping
        result = run_enhanced_error_mapping_cycle(error_obj, context)
        
        # Format return result
        if result.get('status') == 'success':
            return {
                "status": "success",
                "message": "增强版错误映射成功完成",
                "operation": "enhanced_video_processing_error_mapper",
                "result": {
                    'error_type': result.get('standardized_error_id', 'UnknownError'),
                    'classification': result.get('classification', {}),
                    'suggestions': result.get('suggestions', []),
                    'confidence_score': result.get('confidence_score', 0.0),
                    'enhanced_mapping': True
                }
            }
        else:
            return {
                "status": "error",
                "message": f"增强版错误映射失败: {result.get('error_message', 'Unknown error')}",
                "operation": "enhanced_video_processing_error_mapper",
                "result": "error"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"参数解析或执行错误: {str(e)}",
            "operation": "enhanced_video_processing_error_mapper",
            "result": "error"
        }