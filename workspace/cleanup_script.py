import os
import shutil

# Clean up test files
test_files = [
    "test_validation_video.mp4",
    "test_video.mp4",
    "test_video_auto_repaired.mp4",
    "test_video_fixed.mp4",
    "test_video_for_frame_extraction.mp4",
    "test_video_for_validation.mp4",
    "test_video_repaired.mp4",
    "repaired_test_video.mp4"
]

for file in test_files:
    if os.path.exists(file):
        os.remove(file)
        print(f"Deleted {file}")

# Clean up test directories
test_dirs = ["test_frames"]

for dir_name in test_dirs:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)
        print(f"Deleted directory {dir_name}")