import os

frame_paths = [
    "../extracted_test_frames/frame_0000_0.00s.jpg",
    "../extracted_test_frames/frame_0001_0.50s.jpg",
    "../extracted_test_frames/frame_0002_1.00s.jpg"
]

for path in frame_paths:
    print(f"{path}: {os.path.exists(path)}")