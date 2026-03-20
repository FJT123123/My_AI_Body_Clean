"""
自动生成的技能模块
需求: 创建视觉故障注入器。该技能应能对输入的图像或视频文件注入各种类型的故障，包括：1) 图像噪声（高斯噪声、椒盐噪声等）；2) 图像模糊；3) 压缩失真；4) 部分区域遮挡；5) 颜色失真；6) 对于视频，还包括帧丢失、时间戳错误等。该技能应接受源文件路径和故障类型参数，并输出注入故障后的文件。
生成时间: 2026-03-13 17:16:41
"""

# skill_name: visual_fault_injector

import os
import cv2
import numpy as np
from PIL import Image
import subprocess
import tempfile
import uuid
from typing import List, Dict, Any

def add_gaussian_noise(image: np.ndarray, mean: float = 0, std: float = 25) -> np.ndarray:
    """添加高斯噪声到图像"""
    noise = np.random.normal(mean, std, image.shape).astype(np.uint8)
    noisy_image = cv2.add(image, noise)
    return noisy_image

def add_salt_pepper_noise(image: np.ndarray, salt_prob: float = 0.01, pepper_prob: float = 0.01) -> np.ndarray:
    """添加椒盐噪声到图像"""
    noisy = image.copy()
    # 随机选择盐（白色）像素
    salt_coords = [np.random.randint(0, i - 1, int(salt_prob * image.size)) for i in image.shape]
    noisy[salt_coords[0], salt_coords[1], :] = 255

    # 随机选择椒（黑色）像素
    pepper_coords = [np.random.randint(0, i - 1, int(pepper_prob * image.size)) for i in image.shape]
    noisy[pepper_coords[0], pepper_coords[1], :] = 0
    return noisy

def blur_image(image: np.ndarray, blur_type: str = "gaussian", ksize: int = 15) -> np.ndarray:
    """对图像应用模糊"""
    if blur_type == "gaussian":
        return cv2.GaussianBlur(image, (ksize, ksize), 0)
    elif blur_type == "motion":
        kernel = np.zeros((ksize, ksize))
        kernel[int((ksize-1)/2), :] = np.ones(ksize)
        kernel = kernel / ksize
        return cv2.filter2D(image, -1, kernel)
    elif blur_type == "box":
        return cv2.blur(image, (ksize, ksize))
    return image

def add_compression_artifacts(image: np.ndarray, quality: int = 20) -> np.ndarray:
    """添加压缩失真"""
    # 创建临时JPEG文件以引入压缩失真
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    temp_file.close()
    
    # 保存为低质量JPEG
    cv2.imwrite(temp_file.name, image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    
    # 重新读取图像
    compressed_image = cv2.imread(temp_file.name)
    os.unlink(temp_file.name)
    
    return compressed_image

def add_occlusion(image: np.ndarray, x: int, y: int, width: int, height: int, color: tuple = (0, 0, 0)) -> np.ndarray:
    """添加矩形遮挡区域"""
    occluded_image = image.copy()
    cv2.rectangle(occluded_image, (x, y), (x + width, y + height), color, -1)
    return occluded_image

def add_color_distortion(image: np.ndarray, factor: float = 0.5) -> np.ndarray:
    """添加颜色失真"""
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float64)
    
    # 随机调整色调、饱和度和亮度
    image_hsv[:, :, 0] = image_hsv[:, :, 0] * (1 + factor * np.random.uniform(-1, 1))
    image_hsv[:, :, 1] = image_hsv[:, :, 1] * (1 + factor * np.random.uniform(-1, 1))
    image_hsv[:, :, 2] = image_hsv[:, :, 2] * (1 + factor * np.random.uniform(-1, 1))
    
    # 确保值在合理范围内
    image_hsv[:, :, 0] = np.clip(image_hsv[:, :, 0], 0, 179)
    image_hsv[:, :, 1] = np.clip(image_hsv[:, :, 1], 0, 255)
    image_hsv[:, :, 2] = np.clip(image_hsv[:, :, 2], 0, 255)
    
    image_bgr = cv2.cvtColor(image_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return image_bgr

def inject_video_faults(video_path: str, output_path: str, fault_types: List[str], config: Dict[str, Any]) -> str:
    """对视频注入故障"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    frame_count = 0
    frames_to_process = total_frames
    
    # 如果需要帧丢失，调整处理的帧数
    if 'frame_loss' in fault_types:
        loss_probability = config.get('frame_loss_probability', 0.1)
        frames_to_process = int(total_frames * (1 - loss_probability))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 对于帧丢失故障，随机跳过一些帧
        if 'frame_loss' in fault_types:
            if np.random.rand() < config.get('frame_loss_probability', 0.1):
                continue  # 跳过此帧，实现帧丢失
        
        # 对当前帧应用图像故障
        processed_frame = apply_image_faults(frame, fault_types, config)
        
        out.write(processed_frame)
        frame_count += 1
    
    cap.release()
    out.release()
    
    return output_path

def apply_image_faults(image: np.ndarray, fault_types: List[str], config: Dict[str, Any]) -> np.ndarray:
    """对单张图像应用多种故障"""
    processed_image = image.copy()
    
    for fault_type in fault_types:
        if fault_type == 'gaussian_noise':
            mean = config.get('gaussian_noise_mean', 0)
            std = config.get('gaussian_noise_std', 25)
            processed_image = add_gaussian_noise(processed_image, mean, std)
        
        elif fault_type == 'salt_pepper_noise':
            salt_prob = config.get('salt_prob', 0.01)
            pepper_prob = config.get('pepper_prob', 0.01)
            processed_image = add_salt_pepper_noise(processed_image, salt_prob, pepper_prob)
        
        elif fault_type == 'blur':
            blur_type = config.get('blur_type', 'gaussian')
            ksize = config.get('blur_kernel_size', 15)
            processed_image = blur_image(processed_image, blur_type, ksize)
        
        elif fault_type == 'compression':
            quality = config.get('compression_quality', 20)
            processed_image = add_compression_artifacts(processed_image, quality)
        
        elif fault_type == 'occlusion':
            x = config.get('occlusion_x', 0)
            y = config.get('occlusion_y', 0)
            width = config.get('occlusion_width', 100)
            height = config.get('occlusion_height', 100)
            color = config.get('occlusion_color', (0, 0, 0))
            processed_image = add_occlusion(processed_image, x, y, width, height, color)
        
        elif fault_type == 'color_distortion':
            factor = config.get('color_distortion_factor', 0.5)
            processed_image = add_color_distortion(processed_image, factor)
    
    return processed_image

def main(args=None):
    """
    主函数：创建视觉故障注入器
    接收源文件路径和故障类型参数，输出注入故障后的文件
    """
    import json
    
    print(f"DEBUG: args type: {type(args)}")
    print(f"DEBUG: args value: {args}")
    
    # 处理字符串输入
    if isinstance(args, str):
        print(f"DEBUG: Received string input: {args}")
        try:
            args = json.loads(args)
            print(f"DEBUG: Parsed as JSON: {args}")
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON parsing failed: {e}")
            # 如果不是有效的JSON，尝试解析为 key=value 格式
            args_dict = {}
            pairs = args.split(',')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 尝试解析value为JSON（处理嵌套对象）
                    try:
                        args_dict[key] = json.loads(value)
                    except json.JSONDecodeError:
                        # 如果不是JSON，保持为字符串
                        args_dict[key] = value
            args = args_dict
            print(f"DEBUG: Parsed as key=value: {args}")
    
    if args is None:
        args = {}
    
    source_path = args.get('source_path', '')
    fault_types = args.get('fault_types', [])
    output_path = args.get('output_path', '')
    config = args.get('config', {})
    
    # 验证输入参数
    if not source_path:
        return {
            'result': {'error': 'source_path is required'},
            'insights': ['Missing required parameter: source_path'],
            'next_skills': []
        }
    
    if not fault_types:
        return {
            'result': {'error': 'fault_types is required'},
            'insights': ['At least one fault type must be specified'],
            'next_skills': []
        }
    
    if not os.path.exists(source_path):
        return {
            'result': {'error': f'Source file does not exist: {source_path}'},
            'insights': [f'File {source_path} not found'],
            'next_skills': []
        }
    
    # 检查文件类型
    file_ext = os.path.splitext(source_path)[1].lower()
    is_video = file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    
    # 如果没有指定输出路径，生成一个临时路径
    if not output_path:
        temp_dir = tempfile.gettempdir()
        filename = os.path.splitext(os.path.basename(source_path))[0]
        output_path = os.path.join(temp_dir, f"{filename}_with_faults_{uuid.uuid4().hex}{file_ext}")
    
    try:
        if is_video:
            # 处理视频文件
            result_path = inject_video_faults(source_path, output_path, fault_types, config)
        else:
            # 处理图像文件
            image = cv2.imread(source_path)
            if image is None:
                return {
                    'result': {'error': f'Cannot read image: {source_path}'},
                    'insights': [f'Failed to read image file: {source_path}'],
                    'next_skills': []
                }
            
            # 对图像应用故障
            processed_image = apply_image_faults(image, fault_types, config)
            
            # 保存处理后的图像
            cv2.imwrite(output_path, processed_image)
            result_path = output_path
        
        return {
            'result': {
                'output_path': result_path,
                'fault_types_applied': fault_types,
                'source_path': source_path,
                'is_success': True
            },
            'insights': [
                f'Applied {len(fault_types)} fault types to {source_path}: {", ".join(fault_types)}',
                f'Output saved to: {result_path}'
            ],
            'memories': [
                {
                    'event_type': 'skill_executed',
                    'content': f'Visual fault injector executed on {source_path}, applied faults: {", ".join(fault_types)}',
                    'tags': ['visual_fault_injection', 'image_processing', 'video_processing']
                }
            ],
            'next_skills': []
        }
        
    except Exception as e:
        return {
            'result': {
                'error': str(e),
                'is_success': False
            },
            'insights': [f'Error occurred during fault injection: {str(e)}'],
            'next_skills': []
        }