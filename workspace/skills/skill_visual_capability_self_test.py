"""
自动生成的技能模块
需求: 视觉能力自检技能：生成两张不同的测试图像，然后比较它们的相似度，验证整个视觉处理链是否工作。
生成时间: 2026-03-21 11:55:20
"""

# skill_name: visual_capability_self_test
import os
import tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import hashlib
from datetime import datetime

def main(args=None):
    """
    视觉能力自检技能：生成两张不同的测试图像，然后比较它们的相似度，验证整个视觉处理链是否工作
    """
    if args is None:
        args = {}
    
    # 创建临时目录用于存储测试图像
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 生成第一张测试图像
        image1_path = os.path.join(temp_dir, "test_image_1.png")
        generate_test_image_1(image1_path)
        
        # 生成第二张测试图像
        image2_path = os.path.join(temp_dir, "test_image_2.png")
        generate_test_image_2(image2_path)
        
        # 计算图像相似度
        similarity_result = calculate_image_similarity(image1_path, image2_path)
        
        # 验证视觉处理链是否正常工作
        is_working = similarity_result['similarity_score'] >= 0 and similarity_result['similarity_score'] <= 1
        
        # 清理临时文件
        os.remove(image1_path)
        os.remove(image2_path)
        
        result = {
            'status': 'success',
            'image1_path': image1_path,
            'image2_path': image2_path,
            'similarity_result': similarity_result,
            'is_vision_chain_working': is_working,
            'temp_dir': temp_dir
        }
        
        insights = [
            f"视觉处理链自检完成，相似度分数: {similarity_result['similarity_score']:.4f}",
            f"视觉处理链工作状态: {'正常' if is_working else '异常'}"
        ]
        
        return {
            'result': result,
            'insights': insights,
            'capabilities': ['image_generation', 'image_comparison', 'visual_processing_chain'] if is_working else []
        }
    
    except Exception as e:
        # 清理临时文件
        try:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        except:
            pass
        
        result = {
            'status': 'error',
            'error': str(e),
            'temp_dir': temp_dir
        }
        
        return {
            'result': result,
            'insights': [f"视觉能力自检失败: {str(e)}"]
        }

def generate_test_image_1(image_path):
    """生成第一张测试图像 - 包含红色矩形和蓝色圆形"""
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制红色矩形
    draw.rectangle([50, 50, 150, 100], fill='red', outline='black')
    
    # 绘制蓝色圆形
    draw.ellipse([75, 120, 125, 170], fill='blue', outline='black')
    
    img.save(image_path)

def generate_test_image_2(image_path):
    """生成第二张测试图像 - 包含绿色三角形和黄色星形"""
    img = Image.new('RGB', (200, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # 绘制绿色三角形
    draw.polygon([100, 50, 50, 150, 150, 150], fill='green', outline='black')
    
    # 绘制黄色星形
    draw.polygon([100, 100, 110, 130, 140, 130, 115, 150, 125, 180, 100, 160, 75, 180, 85, 150, 60, 130, 90, 130], 
                 fill='yellow', outline='black')
    
    img.save(image_path)

def calculate_image_similarity(image1_path, image2_path):
    """计算两张图像的相似度"""
    # 读取图像
    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')
    
    # 调整图像大小以确保一致
    img1 = img1.resize((200, 200))
    img2 = img2.resize((200, 200))
    
    # 转换为numpy数组
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    # 计算像素级别的差异
    diff = np.sum(np.square(arr1 - arr2))
    max_diff = 200 * 200 * 3 * (255 ** 2)  # 最大可能的差异值
    
    # 计算相似度分数 (0-1之间，1为完全相同)
    similarity_score = 1 - (diff / max_diff)
    
    # 计算哈希值用于快速比较
    hash1 = hashlib.md5(arr1.tobytes()).hexdigest()
    hash2 = hashlib.md5(arr2.tobytes()).hexdigest()
    
    return {
        'similarity_score': float(similarity_score),
        'hash1': hash1,
        'hash2': hash2,
        'hash_match': hash1 == hash2,
        'pixel_diff': int(diff)
    }