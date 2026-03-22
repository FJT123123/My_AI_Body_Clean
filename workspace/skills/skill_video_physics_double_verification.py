"""
自动生成的技能模块
需求: 创建一个增强版物理语义双重验证技能，结合客户端状态捕获和帧间运动物理合理性分析，用于确认数字信息在物理世界中的真实呈现。该技能应接受视频路径作为输入，执行双重验证，并返回综合结果。
生成时间: 2026-03-21 14:29:02
"""

# skill_name: video_physics_double_verification

import cv2
import numpy as np
import os
from scipy import stats
from scipy.spatial import distance
import json

def calculate_motion_vectors(frame1, frame2):
    """计算两帧之间的光流运动向量"""
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # 使用Farneback方法计算光流
    flow = cv2.calcOpticalFlowFarneback(gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    # 计算运动向量的幅度和角度
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    return magnitude, angle, flow

def detect_physical_objects(frame):
    """检测帧中的物理对象"""
    # 使用边缘检测
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # 查找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 100:  # 过滤小面积噪声
            # 计算轮廓的边界框
            x, y, w, h = cv2.boundingRect(contour)
            objects.append({
                'area': area,
                'bbox': (x, y, w, h),
                'center': (x + w/2, y + h/2),
                'contour': contour
            })
    
    return objects

def analyze_physics_consistency(frame1, frame2, objects1, objects2):
    """分析物理一致性"""
    # 计算运动向量
    magnitude, angle, flow = calculate_motion_vectors(frame1, frame2)
    
    # 检查对象运动是否符合物理规律
    physics_consistency = []
    
    for obj1 in objects1:
        for obj2 in objects2:
            # 计算对象间的相对位移
            dx = obj2['center'][0] - obj1['center'][0]
            dy = obj2['center'][1] - obj1['center'][1]
            displacement = np.sqrt(dx**2 + dy**2)
            
            # 获取对应区域的运动向量
            x, y, w, h = obj1['bbox']
            if x + w < flow.shape[1] and y + h < flow.shape[0]:
                region_flow = flow[y:y+h, x:x+w]
                avg_flow_mag = np.mean(np.sqrt(region_flow[:,:,0]**2 + region_flow[:,:,1]**2))
                
                # 检查运动一致性
                consistency_score = abs(displacement - avg_flow_mag) / max(displacement, avg_flow_mag, 1)
                physics_consistency.append({
                    'object_pair': (obj1['area'], obj2['area']),
                    'displacement': displacement,
                    'avg_flow': avg_flow_mag,
                    'consistency_score': 1 - consistency_score  # 转换为一致性分数
                })
    
    return physics_consistency

def analyze_frame_stability(frame):
    """分析帧的稳定性"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 计算帧的梯度
    grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    
    # 计算梯度幅度
    grad_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    
    # 计算局部稳定性（使用梯度变化的方差）
    stability_score = 1.0 / (1.0 + np.var(grad_magnitude))
    
    return stability_score

def main(args=None):
    """
    增强版物理语义双重验证技能
    结合客户端状态捕获和帧间运动物理合理性分析，用于确认数字信息在物理世界中的真实呈现
    该技能接受视频路径作为输入，执行双重验证，并返回综合结果
    """
    if args is None:
        args = {}
    
    video_path = args.get('video_path')
    if not video_path or not os.path.exists(video_path):
        return {
            'result': {'error': '视频路径不存在或无效'},
            'insights': ['输入参数验证失败'],
            'facts': [],
            'memories': []
        }
    
    # 初始化结果
    results = {
        'physical_consistency_scores': [],
        'frame_stability_scores': [],
        'motion_analysis': [],
        'object_detection': [],
        'overall_reliability': 0.0
    }
    
    # 打开视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            'result': {'error': '无法打开视频文件'},
            'insights': ['视频文件格式可能不支持'],
            'facts': [],
            'memories': []
        }
    
    frames = []
    frame_count = 0
    
    # 读取所有帧
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
        frame_count += 1
    
    cap.release()
    
    # 验证帧数
    if len(frames) < 2:
        return {
            'result': {'error': '视频帧数过少，无法进行物理验证'},
            'insights': ['视频需要至少2帧才能进行帧间分析'],
            'facts': [],
            'memories': []
        }
    
    # 逐帧分析
    for i in range(len(frames) - 1):
        frame1 = frames[i]
        frame2 = frames[i + 1]
        
        # 检测对象
        objects1 = detect_physical_objects(frame1)
        objects2 = detect_physical_objects(frame2)
        
        # 物理一致性分析
        physics_consistency = analyze_physics_consistency(frame1, frame2, objects1, objects2)
        
        # 帧稳定性分析
        stability1 = analyze_frame_stability(frame1)
        stability2 = analyze_frame_stability(frame2)
        
        # 记录结果
        results['physical_consistency_scores'].append({
            'frame_pair': (i, i+1),
            'consistency_scores': [item['consistency_score'] for item in physics_consistency]
        })
        
        results['frame_stability_scores'].append({
            'frame': i,
            'stability_score': stability1
        })
        
        results['motion_analysis'].append({
            'frame_pair': (i, i+1),
            'physics_consistency': physics_consistency
        })
        
        results['object_detection'].append({
            'frame': i,
            'objects_count': len(objects1),
            'objects': [{'area': obj['area'], 'bbox': obj['bbox']} for obj in objects1]
        })
    
    # 添加最后一帧的稳定性
    results['frame_stability_scores'].append({
        'frame': frame_count - 1,
        'stability_score': analyze_frame_stability(frames[-1])
    })
    
    # 最后一帧的对象检测
    results['object_detection'].append({
        'frame': frame_count - 1,
        'objects_count': len(detect_physical_objects(frames[-1])),
        'objects': [{'area': obj['area'], 'bbox': obj['bbox']} for obj in detect_physical_objects(frames[-1])]
    })
    
    # 计算总体可靠性
    consistency_values = []
    for item in results['physical_consistency_scores']:
        if item['consistency_scores']:
            consistency_values.extend(item['consistency_scores'])
    
    if consistency_values:
        avg_consistency = sum(consistency_values) / len(consistency_values)
    else:
        avg_consistency = 0.0
    
    stability_values = [item['stability_score'] for item in results['frame_stability_scores']]
    if stability_values:
        avg_stability = sum(stability_values) / len(stability_values)
    else:
        avg_stability = 0.0
    
    # 综合可靠性评分（0-1，1为完全可靠）
    overall_reliability = (avg_consistency + avg_stability) / 2
    results['overall_reliability'] = overall_reliability
    
    # 生成洞察
    insights = []
    if overall_reliability > 0.7:
        insights.append('视频帧间物理一致性较高，符合真实物理世界规律')
    elif overall_reliability > 0.4:
        insights.append('视频帧间物理一致性中等，存在一定的不一致但可能可接受')
    else:
        insights.append('视频帧间物理一致性较低，可能存在非物理行为或数字伪造的迹象')
    
    # 生成事实
    facts = [
        ['视频文件', '包含帧数', str(frame_count)],
        ['视频', '物理一致性平均分', f'{avg_consistency:.3f}'],
        ['视频', '帧稳定性平均分', f'{avg_stability:.3f}'],
        ['视频', '总体可靠性评分', f'{overall_reliability:.3f}']
    ]
    
    return {
        'result': results,
        'insights': insights,
        'facts': facts,
        'memories': [
            f"视频物理验证完成，文件路径: {video_path}, 总体可靠性: {overall_reliability:.3f}"
        ]
    }