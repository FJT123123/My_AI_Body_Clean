"""
人脸检测技能模块
需求: 检测图像中的人脸：使用OpenCV的人脸检测器识别和定位图像中的人脸，并返回人脸位置、数量和置信度信息
"""

# skill_name: image_face_detector
import cv2
import numpy as np
import os
from PIL import Image

def main(args=None):
    """
    检测图像中的人脸：使用OpenCV的人脸检测器识别和定位图像中的人脸
    
    参数:
    - args: 包含图像路径的参数字典，格式为 {'image_path': 'path/to/image.jpg'}
    
    返回:
    - dict: 包含人脸检测结果的字典
    """
    if args is None:
        args = {}
    
    image_path = args.get('image_path', '')
    
    if not image_path or not os.path.exists(image_path):
        return {
            'result': {'error': '图像路径不存在'},
            'insights': ['人脸检测失败：指定路径不存在']
        }
    
    try:
        # 加载预训练的人脸检测器
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # 读取图像
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # 转换为列表以便JSON序列化
        faces_list = []
        for (x, y, w, h) in faces:
            faces_list.append({
                'x': int(x),
                'y': int(y),
                'width': int(w),
                'height': int(h),
                'center_x': int(x + w/2),
                'center_y': int(y + h/2)
            })
        
        result = {
            'image_path': image_path,
            'face_count': len(faces_list),
            'faces': faces_list,
            'detection_method': 'Haar Cascade'
        }
        
        insights = [
            f"检测到 {len(faces_list)} 张人脸",
            f"使用 Haar Cascade 分类器进行人脸检测"
        ]
        
        if len(faces_list) == 0:
            insights.append("图像中未检测到人脸")
        elif len(faces_list) == 1:
            insights.append("图像中检测到单张人脸")
        else:
            insights.append(f"图像中检测到多张人脸 ({len(faces_list)} 张)")
        
        return {
            'result': result,
            'insights': insights
        }
    
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'人脸检测失败：{str(e)}']
        }