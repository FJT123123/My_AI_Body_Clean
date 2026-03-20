# capability_name: video_error_context_analysis_capability

def analyze_video_processing_error_context(error_info: str, video_metadata: dict = None, processing_context: dict = None) -> dict:
    """
    分析视频处理错误的上下文，返回结构化的错误分类和修复建议
    
    Args:
        error_info: 原始错误信息字符串
        video_metadata: 视频元数据字典，包含 codec, resolution, duration, framerate 等
        processing_context: 处理上下文字典，包含操作类型、工具链、参数等
        
    Returns:
        dict: 包含错误类型、根本原因、修复建议、置信度的结构化结果
    """
    try:
        # 初始化参数
        error_info = error_info or ""
        video_metadata = video_metadata or {}
        processing_context = processing_context or {}
        
        # 提取错误特征
        error_features = _extract_error_features(error_info)
        
        # 分析视频元数据
        metadata_analysis = _analyze_video_metadata(video_metadata)
        
        # 分析处理上下文
        context_analysis = _analyze_processing_context(processing_context)
        
        # 综合分析错误类型
        error_classification = _classify_error(error_features, metadata_analysis, context_analysis)
        
        # 生成修复建议
        fix_suggestions = _generate_fix_suggestions(error_classification, video_metadata, processing_context)
        
        # 计算置信度
        confidence = _calculate_confidence(error_classification, error_features)
        
        result = {
            "error_type": error_classification.get("type", "unknown"),
            "error_category": error_classification.get("category", "unknown"),
            "error_description": error_classification.get("description", ""),
            "root_cause": error_classification.get("root_cause", "unknown"),
            "confidence": confidence,
            "metadata_analysis": metadata_analysis,
            "context_analysis": context_analysis,
            "fix_suggestions": fix_suggestions,
            "error_features": error_features,
            "success": True,
            "message": "Error analysis completed successfully"
        }
        
        return result
        
    except Exception as e:
        return {
            "error_type": "analysis_failure",
            "error_category": "unknown",
            "error_description": f"Failed to analyze error: {str(e)}",
            "root_cause": "analysis_error",
            "confidence": 0.0,
            "metadata_analysis": {},
            "context_analysis": {},
            "fix_suggestions": [],
            "error_features": {},
            "success": False,
            "message": str(e)
        }


def _extract_error_features(error_info: str) -> dict:
    """提取错误信息的关键特征"""
    error_lower = error_info.lower()
    
    # 常见错误模式识别
    features = {
        "error_codes": [],
        "keywords": [],
        "error_patterns": [],
        "severity": "unknown"
    }
    
    # 提取错误码
    import re
    error_code_pattern = r'(\b[0-9]{1,5}\b|error\s*[0-9]+|code\s*[0-9]+|errno\s*[0-9]+)'
    error_codes = re.findall(error_code_pattern, error_info, re.IGNORECASE)
    features["error_codes"] = [code.strip() for code in error_codes]
    
    # 常见错误关键词
    error_keywords = [
        "codec", "decode", "encode", "format", "unsupported", "corrupted",
        "memory", "allocation", "overflow", "timeout", "buffer", "overflow",
        "access", "permission", "file", "not found", "no space", "disk full",
        "overflow", "underflow", "sync", "desync", "timestamp", "frame",
        "resolution", "bitrate", "framerate", "seek", "input", "output"
    ]
    
    found_keywords = []
    for keyword in error_keywords:
        if keyword in error_lower:
            found_keywords.append(keyword)
    
    features["keywords"] = found_keywords
    
    # 常见错误模式
    severity_patterns = [
        ("critical", r"(fatal|critical|emergency|severe|unrecoverable)"),
        ("error", r"(error|failed|failure|cannot|unable)"),
        ("warning", r"(warning|warn|problem|issue|potential)"),
        ("info", r"(info|information|debug|notice|verbose)")
    ]
    
    for severity, pattern in severity_patterns:
        if re.search(pattern, error_info, re.IGNORECASE):
            features["severity"] = severity
            features["error_patterns"].append(severity)
            break
    
    return features


def _analyze_video_metadata(metadata: dict) -> dict:
    """分析视频元数据"""
    analysis = {
        "size_risk": "low",
        "codec_risk": "low",
        "resolution_risk": "low",
        "complexity_risk": "low",
        "metadata_available": bool(metadata)
    }
    
    if not metadata:
        return analysis
    
    # 检查文件大小
    file_size = metadata.get("size", 0)
    if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
        analysis["size_risk"] = "high"
    elif file_size > 500 * 1024 * 1024:  # 500MB
        analysis["size_risk"] = "medium"
    
    # 检查分辨率
    resolution = metadata.get("resolution", "")
    width = metadata.get("width", 0)
    height = metadata.get("height", 0)
    
    if width > 3840 or height > 2160:  # 4K+
        analysis["resolution_risk"] = "high"
    elif width > 1920 or height > 1080:  # 1080p
        analysis["resolution_risk"] = "medium"
    
    # 检查编解码器
    codec = metadata.get("codec", "").lower()
    complex_codecs = ["hevc", "h265", "vp9", "av1"]
    if codec in complex_codecs:
        analysis["codec_risk"] = "medium"
    
    # 检查复杂度 (码率、帧率、时长)
    bitrate = metadata.get("bitrate", 0)
    framerate = metadata.get("framerate", 0)
    duration = metadata.get("duration", 0)
    
    complexity_score = 0
    if bitrate > 20000000:  # 20Mbps
        complexity_score += 1
    if framerate > 60:
        complexity_score += 1
    if duration > 3600:  # 1小时
        complexity_score += 1
    
    if complexity_score >= 2:
        analysis["complexity_risk"] = "high"
    elif complexity_score >= 1:
        analysis["complexity_risk"] = "medium"
    
    return analysis


def _analyze_processing_context(context: dict) -> dict:
    """分析处理上下文"""
    analysis = {
        "operation_type": context.get("operation_type", "unknown"),
        "tool_chain": context.get("tool_chain", "unknown"),
        "parameters": context.get("parameters", {}),
        "resource_constraints": "none"
    }
    
    if not context:
        return analysis
    
    # 分析资源限制
    params = context.get("parameters", {})
    memory_limit = params.get("memory_limit", 0)
    threads = params.get("threads", 0)
    
    if memory_limit > 0 and memory_limit < 1024 * 1024 * 1024:  # 1GB
        analysis["resource_constraints"] = "memory_limited"
    elif threads > 0 and threads < 2:
        if analysis["resource_constraints"] == "none":
            analysis["resource_constraints"] = "cpu_limited"
    
    return analysis


def _classify_error(error_features: dict, metadata_analysis: dict, context_analysis: dict) -> dict:
    """基于特征和上下文分类错误"""
    error_type = "unknown"
    category = "unknown"
    description = "Unknown error"
    root_cause = "unknown"
    
    # 基于关键词分类
    keywords = error_features.get("keywords", [])
    
    # 编解码器相关错误
    if any(k in ["codec", "decode", "encode", "format", "unsupported"] for k in keywords):
        error_type = "codec_error"
        category = "codec_unsupported"
        description = "Video codec is not supported or format is incompatible"
        root_cause = "codec_unsupported"
    elif any(k in ["memory", "allocation", "overflow"] for k in keywords):
        error_type = "resource_error"
        category = "memory_insufficient"
        description = "Insufficient memory to process the video"
        root_cause = "memory_insufficient"
        if metadata_analysis.get("size_risk") == "high" or metadata_analysis.get("complexity_risk") == "high":
            root_cause = "memory_insufficient_large_file"
    elif any(k in ["file", "not found", "access", "permission"] for k in keywords):
        error_type = "file_error"
        category = "file_access"
        description = "File access error or file not found"
        root_cause = "file_access_error"
    elif any(k in ["corrupted", "corrupt", "damaged"] for k in keywords):
        error_type = "file_error"
        category = "file_corrupted"
        description = "Video file is corrupted or damaged"
        root_cause = "file_corrupted"
    elif any(k in ["timeout", "buffer", "overflow", "underflow", "sync", "desync"] for k in keywords):
        error_type = "processing_error"
        category = "stream_processing"
        description = "Error during video stream processing"
        root_cause = "stream_processing_error"
    elif any(k in ["resolution", "bitrate", "framerate"] for k in keywords):
        error_type = "parameter_error"
        category = "parameter_mismatch"
        description = "Video parameters do not match processing requirements"
        root_cause = "parameter_mismatch"
    else:
        # 根据上下文推断
        if context_analysis.get("resource_constraints") != "none":
            error_type = "resource_error"
            category = "resource_limitation"
            description = "Processing failed due to resource constraints"
            root_cause = "resource_limitation"
        elif metadata_analysis.get("size_risk") == "high":
            error_type = "resource_error"
            category = "large_file_processing"
            description = "Processing large file may require more resources"
            root_cause = "large_file_memory_issue"
        else:
            error_type = "unknown"
            category = "unclassified"
            description = "Unable to classify the error from available information"
            root_cause = "unclassified"
    
    return {
        "type": error_type,
        "category": category,
        "description": description,
        "root_cause": root_cause
    }


def _generate_fix_suggestions(error_classification: dict, video_metadata: dict, processing_context: dict) -> list:
    """生成修复建议"""
    suggestions = []
    
    root_cause = error_classification.get("root_cause", "")
    
    if root_cause == "codec_unsupported":
        suggestions.append("Try converting the video to a widely supported format like MP4 with H.264 codec")
        suggestions.append("Check if the video player/processing tool supports the current codec")
        if video_metadata.get("codec"):
            codec = video_metadata.get("codec")
            suggestions.append(f"The video uses {codec} codec which may not be supported by all tools")
    
    elif root_cause == "memory_insufficient":
        suggestions.append("Increase available memory or reduce processing parameters")
        suggestions.append("Process the video in smaller segments if possible")
        if processing_context.get("parameters", {}).get("threads", 0) > 1:
            suggestions.append("Reduce the number of processing threads to lower memory usage")
    
    elif root_cause == "memory_insufficient_large_file":
        suggestions.append("Reduce video resolution or bitrate before processing")
        suggestions.append("Use a more efficient codec for processing")
        suggestions.append("Process high-resolution video on a machine with more RAM")
    
    elif root_cause == "file_access_error":
        suggestions.append("Check file permissions and ensure the file is accessible")
        suggestions.append("Verify the file path is correct and the file exists")
        suggestions.append("Ensure no other process is using the file")
    
    elif root_cause == "file_corrupted":
        suggestions.append("Try to repair the video file using a repair tool")
        suggestions.append("Use a different copy of the video file if available")
        suggestions.append("Check if the file was properly downloaded/transferred")
    
    elif root_cause == "stream_processing_error":
        suggestions.append("Try processing with different buffer settings")
        suggestions.append("Adjust processing parameters to handle stream synchronization")
        suggestions.append("Check for timestamp or frame ordering issues")
    
    elif root_cause == "parameter_mismatch":
        suggestions.append("Adjust video parameters to match processing requirements")
        suggestions.append("Verify that resolution, bitrate, and framerate are within supported ranges")
        suggestions.append("Use default parameters or commonly supported settings")
    
    elif root_cause == "resource_limitation":
        suggestions.append("Increase resource limits or use a more powerful machine")
        suggestions.append("Optimize processing parameters for current resource constraints")
        suggestions.append("Consider processing during off-peak hours")
    
    elif root_cause == "large_file_memory_issue":
        suggestions.append("Split the video into smaller segments for processing")
        suggestions.append("Use a streaming processing approach instead of loading entire file")
        suggestions.append("Consider processing on a system with more memory")
    
    else:
        suggestions.append("Check the error details and consult the documentation for the video processing tool")
        suggestions.append("Verify input parameters and file format compatibility")
        suggestions.append("Consider updating the video processing software to the latest version")
    
    return suggestions


def _calculate_confidence(error_classification: dict, error_features: dict) -> float:
    """计算分析置信度"""
    base_confidence = 0.6  # 基础置信度
    
    # 如果有明确的错误关键词，增加置信度
    if error_features.get("keywords"):
        base_confidence += 0.2
    
    # 如果有具体的错误码，再增加置信度
    if error_features.get("error_codes"):
        base_confidence += 0.1
    
    # 根据分类的明确性调整
    if error_classification.get("root_cause") != "unclassified":
        base_confidence += 0.1
    
    # 确保置信度在合理范围内
    return min(1.0, max(0.0, base_confidence))