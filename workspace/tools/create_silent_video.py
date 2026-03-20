#!/usr/bin/env python3
import subprocess
import os

def create_silent_video():
    """创建无声视频"""
    input_video = "/Users/zhufeng/My_AI_Body_副本/test_video.mp4"
    output_video = "/Users/zhufeng/My_AI_Body_副本/silent_test_video.mp4"
    
    if not os.path.exists(input_video):
        print(f"输入视频不存在: {input_video}")
        return False
    
    cmd = ["ffmpeg", "-y", "-i", input_video, "-c", "copy", "-an", output_video]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"无声视频已创建: {output_video}")
        return True
    else:
        print(f"创建无声视频失败: {result.stderr}")
        return False

if __name__ == "__main__":
    create_silent_video()