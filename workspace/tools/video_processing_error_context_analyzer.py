# tool_name: video_processing_error_context_analyzer

import json
import os
import subprocess
import sys

# Add the workspace directory to the path to import capabilities
workspace_dir = os.path.join(os.path.dirname(__file__), '..')
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from capabilities.video_error_context_analysis_capability import analyze_video_processing_error_context


def extract_video_metadata(video_path):
    """Extract video metadata using ffprobe"""
    if not video_path or not os.path.exists(video_path):
        return {}
    
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}
            
        data = json.loads(result.stdout)
        
        # Extract relevant metadata
        metadata = {
            "path": video_path,
            "size": int(data.get("format", {}).get("size", 0)),
            "duration": float(data.get("format", {}).get("duration", 0)),
            "format": data.get("format", {}).get("format_name", "")
        }
        
        # Find video stream
        video_stream = None
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                video_stream = stream
                break
                
        if video_stream:
            metadata.update({
                "codec": video_stream.get("codec_name", ""),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
                "framerate": eval(video_stream.get("r_frame_rate", "0/1")) if "/" in video_stream.get("r_frame_rate", "") else float(video_stream.get("r_frame_rate", 0)),
                "bitrate": int(video_stream.get("bit_rate", 0))
            })
            
        return metadata
        
    except Exception as e:
        return {}


def main(input_args):
    """
    Video processing error context analyzer tool
    
    Args:
        input_args (str): JSON string containing:
            - error_info (str, required): The raw error information
            - video_path (str, optional): Path to the video file
            - processing_context (dict, optional): Processing context information
            
    Returns:
        dict: Analysis results with error classification and repair suggestions
    """
    try:
        # Parse input arguments
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
            
        # Validate required parameters
        error_info = params.get("error_info")
        if not error_info:
            return {
                "result": {"error": "Missing error_info parameter"},
                "insights": ["Parameter validation failed: error_info is required"],
                "facts": [],
                "memories": []
            }
            
        video_path = params.get("video_path")
        processing_context = params.get("processing_context", {})
        
        # Extract video metadata if video_path is provided
        video_metadata = {}
        if video_path and os.path.exists(video_path):
            video_metadata = extract_video_metadata(video_path)
            
        # Analyze the error context
        analysis_result = analyze_video_processing_error_context(
            error_info=error_info,
            video_metadata=video_metadata,
            processing_context=processing_context
        )
        
        # Format the response
        response = {
            "result": analysis_result,
            "insights": [
                f"Error type classified as: {analysis_result.get('error_type', 'unknown')}",
                f"Root cause identified: {analysis_result.get('root_cause', 'unknown')}",
                f"Analysis confidence: {analysis_result.get('confidence', 0.0):.2f}"
            ],
            "facts": [
                f"Video processing error analysis completed with {len(analysis_result.get('fix_suggestions', []))} repair suggestions"
            ],
            "memories": [
                f"Analyzed video processing error: {error_info[:100]}..." if len(error_info) > 100 else error_info
            ]
        }
        
        return response
        
    except json.JSONDecodeError as e:
        return {
            "result": {"error": f"Invalid JSON input: {str(e)}"},
            "insights": ["Input parsing failed: invalid JSON format"],
            "facts": [],
            "memories": []
        }
    except Exception as e:
        return {
            "result": {"error": f"Error analysis failed: {str(e)}"},
            "insights": ["Unexpected error during error analysis"],
            "facts": [],
            "memories": []
        }