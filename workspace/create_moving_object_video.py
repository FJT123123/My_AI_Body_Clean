import cv2
import numpy as np
import os

# 创建测试视频目录
os.makedirs("./test_videos", exist_ok=True)

# 创建一个包含明显运动的测试视频
video_path = "./test_videos/moving_object_sample.mp4"
frame_width, frame_height = 640, 480
fps = 10  # 降低FPS以便更容易观察运动
duration = 3  # 3秒

# 创建视频写入器
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

# 生成带有圆形物体移动的帧
total_frames = fps * duration
for i in range(total_frames):
    # 创建黑色背景
    frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    
    # 计算圆形位置（从左到右移动）
    x_pos = int((i / (total_frames - 1)) * (frame_width - 60)) + 30
    y_pos = frame_height // 2
    
    # 绘制白色圆形
    cv2.circle(frame, (x_pos, y_pos), 30, (255, 255, 255), -1)
    
    # 写入帧
    out.write(frame)

# 释放资源
out.release()
print(f"移动物体测试视频已生成: {video_path}")