# capability_name: metal_video_codec_support_capability

def detect_metal_video_codec_support():
    """
    专门用于探测Apple Silicon GPU的Metal编解码器支持情况的能力模块
    
    Returns:
        dict: 包含Metal编解码器支持详情的字典
    """
    import subprocess
    import platform
    import os
    import tempfile
    
    # 检查是否为Apple Silicon平台
    if not (platform.system() == "Darwin" and platform.machine() == "arm64"):
        return {
            "is_apple_silicon": False,
            "metal_codecs": [],
            "hardware_acceleration_details": {},
            "error": "Not running on Apple Silicon"
        }
    
    result = {
        "is_apple_silicon": True,
        "metal_codecs": [],
        "hardware_acceleration_details": {}
    }
    
    try:
        # 检查ffmpeg是否可用
        try:
            ffmpeg_version_cmd = ["ffmpeg", "-version"]
            subprocess.run(ffmpeg_version_cmd, capture_output=True, text=True, timeout=10)
        except FileNotFoundError:
            result["error"] = "ffmpeg not found"
            return result
        except subprocess.TimeoutExpired:
            result["error"] = "ffmpeg command timed out"
            return result
        
        # 获取所有编码器列表
        encoders_cmd = ["ffmpeg", "-hide_banner", "-encoders"]
        encoders_result = subprocess.run(encoders_cmd, capture_output=True, text=True, timeout=30)
        
        # 获取所有解码器列表
        decoders_cmd = ["ffmpeg", "-hide_banner", "-decoders"]
        decoders_result = subprocess.run(decoders_cmd, capture_output=True, text=True, timeout=30)
        
        # 解析编码器和解码器列表
        encoders = []
        decoders = []
        
        if encoders_result.returncode == 0:
            lines = encoders_result.stdout.split('\n')
            in_encoders_section = False
            for line in lines:
                if line.strip().startswith('------'):
                    in_encoders_section = True
                    continue
                if in_encoders_section and line.strip() and not line.startswith(' '):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        codec_name = parts[1]
                        # 检查是否为硬件加速编解码器
                        if any(hw_prefix in codec_name for hw_prefix in ['videotoolbox', 'vt', 'h264_vt', 'hevc_vt']):
                            encoders.append(codec_name)
        
        if decoders_result.returncode == 0:
            lines = decoders_result.stdout.split('\n')
            in_decoders_section = False
            for line in lines:
                if line.strip().startswith('------'):
                    in_decoders_section = True
                    continue
                if in_decoders_section and line.strip() and not line.startswith(' '):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        codec_name = parts[1]
                        # 检查是否为硬件加速编解码器
                        if any(hw_prefix in codec_name for hw_prefix in ['videotoolbox', 'vt', 'h264_vt', 'hevc_vt']):
                            decoders.append(codec_name)
        
        # 获取详细的硬件加速能力信息
        hwaccels_cmd = ["ffmpeg", "-hide_banner", "-hwaccels"]
        hwaccels_result = subprocess.run(hwaccels_cmd, capture_output=True, text=True, timeout=30)
        
        hwaccels = []
        if hwaccels_result.returncode == 0:
            lines = hwaccels_result.stdout.split('\n')
            in_hwaccels_section = False
            for line in lines:
                if line.strip().startswith('Hardware acceleration methods:'):
                    in_hwaccels_section = True
                    continue
                if in_hwaccels_section and line.strip():
                    hwaccel = line.strip()
                    if hwaccel and not hwaccel.startswith('Hardware acceleration methods:'):
                        hwaccels.append(hwaccel)
        
        # 测试具体的Metal编解码器支持
        metal_codecs = []
        hardware_details = {}
        
        # 常见的Apple Silicon Metal编解码器
        test_codecs = [
            "h264_videotoolbox", "hevc_videotoolbox", 
            "h264_vt", "hevc_vt",
            "prores_videotoolbox", "vp9_videotoolbox"
        ]
        
        for codec in test_codecs:
            # 测试编码器支持
            try:
                encode_test_cmd = ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "testsrc=duration=1:size=1920x1080:rate=30", 
                                 "-c:v", codec, "-f", "null", "-"]
                encode_result = subprocess.run(encode_test_cmd, capture_output=True, text=True, timeout=15)
                can_encode = encode_result.returncode == 0
                
                # 测试解码器支持 - 创建临时文件进行解码测试
                can_decode = False
                temp_filename = None
                try:
                    # 创建临时文件
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                        temp_filename = temp_file.name
                    
                    # 先用软件编码创建测试文件
                    create_cmd = ["ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "testsrc=duration=1:size=1920x1080:rate=30", 
                                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-y", temp_filename]
                    create_result = subprocess.run(create_cmd, capture_output=True, text=True, timeout=15)
                    
                    if create_result.returncode == 0:
                        # 用硬件解码器测试
                        decode_codec_name = codec.replace('_videotoolbox', '').replace('_vt', '')
                        decode_cmd = ["ffmpeg", "-hide_banner", "-hwaccel", "videotoolbox", 
                                    "-c:v", decode_codec_name, 
                                    "-i", temp_filename, "-f", "null", "-"]
                        decode_result = subprocess.run(decode_cmd, capture_output=True, text=True, timeout=15)
                        can_decode = decode_result.returncode == 0
                except Exception:
                    # 如果解码测试失败，继续尝试
                    pass
                finally:
                    # 清理临时文件
                    if temp_filename and os.path.exists(temp_filename):
                        os.unlink(temp_filename)
                
                if can_encode or can_decode:
                    metal_codecs.append(codec)
                    hardware_details[codec] = {
                        "can_encode": can_encode,
                        "can_decode": can_decode,
                        "status": "supported"
                    }
                else:
                    hardware_details[codec] = {
                        "can_encode": can_encode,
                        "can_decode": can_decode,
                        "status": "not_supported"
                    }
                    
            except subprocess.TimeoutExpired:
                hardware_details[codec] = {
                    "can_encode": False,
                    "can_decode": False,
                    "status": "error",
                    "error": "Command timeout"
                }
            except Exception as e:
                hardware_details[codec] = {
                    "can_encode": False,
                    "can_decode": False,
                    "status": "error",
                    "error": str(e)
                }
        
        result["metal_codecs"] = metal_codecs
        result["hardware_acceleration_details"] = hardware_details
        result["available_hwaccels"] = hwaccels
        result["detected_encoders"] = encoders
        result["detected_decoders"] = decoders
        
    except subprocess.TimeoutExpired:
        result["error"] = "Command timeout during detection"
    except Exception as e:
        result["error"] = f"Error detecting Metal codec support: {str(e)}"
    
    return result