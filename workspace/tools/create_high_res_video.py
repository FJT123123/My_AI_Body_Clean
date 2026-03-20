import subprocess
import os

def create_4k_video(output_path, duration=10):
    """创建4K分辨率视频用于压力测试"""
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'testsrc=size=3840x2160:rate=60',
        '-t', str(duration), '-c:v', 'libx264', '-preset', 'ultrafast', output_path
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=120)
    return result.returncode == 0

if __name__ == "__main__":
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/4k_test.mp4"
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    success = create_4k_video(output_path, duration)
    print(f"4K video creation {'successful' if success else 'failed'}: {output_path}")