import cv2
import numpy as np
import os

# 创建测试视频目录
os.makedirs("./test_videos", exist_ok=True)

# 创建一个简单的测试视频，包含有意义的运动
video_path = "./test_videos/repair_validation_sample.mp4"
frame_width, frame_height = 640, 480
fps = 30
duration = 5  # 5秒

# 创建视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

# 生成带有圆形物体移动的帧
for i in range(fps * duration):
    # 创建黑色背景
    frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    
    # 计算圆形位置（从左到右移动）
    x_pos = int((i / (fps * duration)) * frame_width)
    y_pos = frame_height // 2
    
    # 绘制白色圆形
    cv2.circle(frame, (x_pos, y_pos), 30, (255, 255, 255), -1)
    
    # 写入帧
    out.write(frame)

# 释放资源
out.release()
print(f"测试视频已生成: {video_path}")