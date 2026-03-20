"""
自动生成的技能模块
需求: 探测ffmpeg和tesseract的完整功能矩阵，包括所有可用的编解码器、格式、滤镜以及OCR语言包。该技能将生成详细的兼容性报告，覆盖H.264、HEVC、VP9等主流编解码器组合，以及tesseract支持的所有语言环境。
生成时间: 2026-03-20 11:06:55
"""

# skill_name: system_ffmpeg_tesseract_capability_detection

import subprocess
import sys
import os
import json
from typing import Dict, List, Any

def main(args=None):
    """
    探测ffmpeg和tesseract的完整功能矩阵，包括所有可用的编解码器、格式、滤镜以及OCR语言包。
    生成详细的兼容性报告，覆盖H.264、HEVC、VP9等主流编解码器组合，以及tesseract支持的所有语言环境。
    """
    if args is None:
        args = {}
    
    result = {}
    capabilities = []
    
    # 检查ffmpeg
    ffmpeg_info = check_ffmpeg()
    if ffmpeg_info['available']:
        result['ffmpeg'] = ffmpeg_info
        capabilities.append("ffmpeg_system_tool")
    else:
        result['ffmpeg'] = {"available": False, "error": "ffmpeg not found"}
    
    # 检查tesseract
    tesseract_info = check_tesseract()
    if tesseract_info['available']:
        result['tesseract'] = tesseract_info
        capabilities.append("tesseract_ocr_tool")
    else:
        result['tesseract'] = {"available": False, "error": "tesseract not found"}
    
    # 生成兼容性报告
    compatibility_report = generate_compatibility_report(ffmpeg_info, tesseract_info)
    
    return {
        "result": result,
        "insights": [
            f"FFmpeg available: {ffmpeg_info['available']}",
            f"Tesseract available: {tesseract_info['available']}",
            f"Supported codecs: {len(ffmpeg_info.get('codecs', []))} codecs detected",
            f"Supported formats: {len(ffmpeg_info.get('formats', []))} formats detected",
            f"Supported filters: {len(ffmpeg_info.get('filters', []))} filters detected",
            f"OCR languages: {len(tesseract_info.get('languages', []))} languages available"
        ],
        "capabilities": capabilities,
        "compatibility_report": compatibility_report
    }

def run_command(cmd: List[str]) -> str:
    """执行系统命令并返回输出"""
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout + e.stderr
    except FileNotFoundError:
        return ""

def check_ffmpeg() -> Dict[str, Any]:
    """检查ffmpeg的可用性和功能"""
    info = {"available": False}
    
    # 检查ffmpeg是否可用
    version_output = run_command(["ffmpeg", "-version"])
    if "ffmpeg version" in version_output:
        info["available"] = True
        info["version"] = version_output.split("\n")[0]
        
        # 获取支持的编解码器
        codecs_output = run_command(["ffmpeg", "-encoders"])
        codecs_output += run_command(["ffmpeg", "-decoders"])
        info["codecs"] = parse_codecs(codecs_output)
        
        # 获取支持的格式
        formats_output = run_command(["ffmpeg", "-formats"])
        info["formats"] = parse_formats(formats_output)
        
        # 获取支持的滤镜
        filters_output = run_command(["ffmpeg", "-filters"])
        info["filters"] = parse_filters(filters_output)
        
        # 检查特定编解码器支持
        info["h264_support"] = any("h264" in codec["name"] for codec in info["codecs"])
        info["hevc_support"] = any("hevc" in codec["name"] for codec in info["codecs"])
        info["vp9_support"] = any("vp9" in codec["name"] for codec in info["codecs"])
    else:
        info["error"] = "ffmpeg not found or not in PATH"
    
    return info

def check_tesseract() -> Dict[str, Any]:
    """检查tesseract的可用性和功能"""
    info = {"available": False}
    
    # 检查tesseract是否可用
    version_output = run_command(["tesseract", "--version"])
    if "tesseract" in version_output:
        info["available"] = True
        info["version"] = version_output.split("\n")[0]
        
        # 获取支持的语言
        langs_output = run_command(["tesseract", "--list-langs"])
        if langs_output:
            lines = langs_output.split("\n")
            # 跳过标题行
            langs = [line.strip() for line in lines if line.strip() and not line.startswith("List of available languages")]
            info["languages"] = langs
        else:
            info["languages"] = []
    else:
        info["error"] = "tesseract not found or not in PATH"
    
    return info

def parse_codecs(output: str) -> List[Dict[str, str]]:
    """解析ffmpeg编解码器输出"""
    codecs = []
    lines = output.split("\n")
    for line in lines:
        if line.strip() and not line.startswith("ffmpeg version") and not line.startswith(" ") and not line.startswith("Encoders:") and not line.startswith("Decoders:"):
            # 格式: DE V..... h264                 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10
            parts = line.split(maxsplit=2)
            if len(parts) >= 2:
                codec_info = {
                    "flags": parts[0].strip(),
                    "type": parts[1].strip() if len(parts) > 1 else "",
                    "name": parts[2].split()[0].strip() if len(parts) > 2 else ""
                }
                if codec_info["name"] and codec_info["name"] != "=":
                    codecs.append(codec_info)
    return codecs

def parse_formats(output: str) -> List[Dict[str, str]]:
    """解析ffmpeg格式输出"""
    formats = []
    lines = output.split("\n")
    for line in lines:
        if line.strip() and " --" not in line:
            # 格式: D. 3g2             3GP2 (3GPP2 file format)
            parts = line.split()
            if len(parts) >= 2:
                format_info = {
                    "flags": parts[0].strip(),
                    "name": parts[1].strip(),
                    "description": " ".join(parts[2:]) if len(parts) > 2 else ""
                }
                if format_info["name"]:
                    formats.append(format_info)
    return formats

def parse_filters(output: str) -> List[Dict[str, str]]:
    """解析ffmpeg滤镜输出"""
    filters = []
    lines = output.split("\n")
    for line in lines[2:]:  # 跳过标题行
        if line.strip() and not line.startswith(" "):
            # 格式: T... scale            V->V       Set the video scale dimensions.
            parts = line.split(maxsplit=2)
            if len(parts) >= 2:
                filter_info = {
                    "flags": parts[0].strip(),
                    "name": parts[1].strip(),
                    "description": parts[2].strip() if len(parts) > 2 else ""
                }
                if filter_info["name"]:
                    filters.append(filter_info)
    return filters

def generate_compatibility_report(ffmpeg_info: Dict, tesseract_info: Dict) -> Dict[str, Any]:
    """生成兼容性报告"""
    report = {
        "system_tools": {
            "ffmpeg": ffmpeg_info["available"],
            "tesseract": tesseract_info["available"]
        },
        "video_processing": {
            "h264_support": ffmpeg_info.get("h264_support", False),
            "hevc_support": ffmpeg_info.get("hevc_support", False),
            "vp9_support": ffmpeg_info.get("vp9_support", False),
            "total_codecs": len(ffmpeg_info.get("codecs", [])),
            "total_formats": len(ffmpeg_info.get("formats", [])),
            "total_filters": len(ffmpeg_info.get("filters", []))
        },
        "ocr_support": {
            "total_languages": len(tesseract_info.get("languages", [])),
            "supported_languages": tesseract_info.get("languages", [])
        }
    }
    
    # 设备兼容性评估
    if ffmpeg_info["available"] and tesseract_info["available"]:
        report["overall_compatibility"] = "High"
        report["compatibility_notes"] = "Both tools are available, full multimedia processing and OCR capabilities"
    elif ffmpeg_info["available"]:
        report["overall_compatibility"] = "Medium"
        report["compatibility_notes"] = "Video/Audio processing available, OCR unavailable"
    elif tesseract_info["available"]:
        report["overall_compatibility"] = "Medium"
        report["compatibility_notes"] = "OCR available, video/audio processing unavailable"
    else:
        report["overall_compatibility"] = "Low"
        report["compatibility_notes"] = "Neither tool is available"
    
    return report