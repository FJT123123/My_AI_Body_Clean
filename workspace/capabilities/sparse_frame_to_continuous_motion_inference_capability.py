# capability_name: sparse_frame_to_continuous_motion_inference_capability

import numpy as np
import cv2
from typing import Dict, List, Any, Optional, Tuple
import math
from dataclasses import dataclass
from scipy.interpolate import interp1d
from scipy.optimize import minimize


@dataclass
class MotionVector:
    x: float
    y: float
    magnitude: float
    angle: float


@dataclass
class MotionTrajectory:
    object_id: str
    positions: List[Tuple[float, float]]  # (x, y) coordinates
    velocities: List[MotionVector]
    accelerations: List[MotionVector]


def calculate_motion_vector(start_pos: Tuple[float, float], end_pos: Tuple[float, float], dt: float) -> MotionVector:
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    magnitude = math.sqrt(dx**2 + dy**2)
    angle = math.atan2(dy, dx)
    return MotionVector(dx/dt, dy/dt, magnitude/dt, angle)


def apply_physical_constraints(trajectory: MotionTrajectory, gravity: float = 9.8, friction: float = 0.1) -> MotionTrajectory:
    """Apply physical constraints to refine the trajectory"""
    # Apply gravity and friction to the motion
    refined_positions = []
    refined_velocities = []
    
    prev_pos = trajectory.positions[0]
    prev_vel = trajectory.velocities[0]
    
    refined_positions.append(prev_pos)
    refined_velocities.append(prev_vel)
    
    for i in range(1, len(trajectory.positions)):
        # Calculate time step
        dt = 1.0 / len(trajectory.positions)  # Simplified assumption
        
        # Apply friction to velocity
        new_vx = prev_vel.x * (1 - friction * dt)
        new_vy = prev_vel.y + gravity * dt  # Apply gravity
        new_vy = new_vy * (1 - friction * dt)
        
        # Calculate new position
        new_x = prev_pos[0] + new_vx * dt
        new_y = prev_pos[1] + new_vy * dt
        
        new_pos = (new_x, new_y)
        new_vel = MotionVector(new_vx, new_vy, math.sqrt(new_vx**2 + new_vy**2), math.atan2(new_vy, new_vx))
        
        refined_positions.append(new_pos)
        refined_velocities.append(new_vel)
        
        prev_pos = new_pos
        prev_vel = new_vel
    
    return MotionTrajectory(trajectory.object_id, refined_positions, refined_velocities, [])


def interpolate_motion(trajectory: MotionTrajectory, target_frames: int) -> MotionTrajectory:
    """Interpolate motion to generate more intermediate frames"""
    if len(trajectory.positions) < 2:
        return trajectory
    
    # Extract x and y coordinates
    x_coords = [pos[0] for pos in trajectory.positions]
    y_coords = [pos[1] for pos in trajectory.positions]
    
    # Create interpolation functions
    t = np.linspace(0, 1, len(trajectory.positions))
    f_x = interp1d(t, x_coords, kind='cubic', fill_value='extrapolate')
    f_y = interp1d(t, y_coords, kind='cubic', fill_value='extrapolate')
    
    # Generate new time points
    new_t = np.linspace(0, 1, target_frames)
    new_x_coords = f_x(new_t)
    new_y_coords = f_y(new_t)
    
    # Create new trajectory with interpolated positions
    new_positions = [(float(x), float(y)) for x, y in zip(new_x_coords, new_y_coords)]
    
    # Calculate new velocities
    new_velocities = []
    for i in range(len(new_positions)):
        if i == 0:
            # Use first available velocity if exists
            if trajectory.velocities:
                new_velocities.append(trajectory.velocities[0])
            else:
                new_velocities.append(MotionVector(0, 0, 0, 0))
        else:
            # Calculate velocity from position difference
            dt = 1.0 / target_frames
            vx = (new_positions[i][0] - new_positions[i-1][0]) / dt
            vy = (new_positions[i][1] - new_positions[i-1][1]) / dt
            mag = math.sqrt(vx**2 + vy**2)
            angle = math.atan2(vy, vx)
            new_velocities.append(MotionVector(vx, vy, mag, angle))
    
    return MotionTrajectory(trajectory.object_id, new_positions, new_velocities, [])


def extract_feature_points(frame: np.ndarray) -> List[Dict[str, Any]]:
    """Extract feature points from a frame"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Use Shi-Tomasi corner detector
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
    
    features = []
    if corners is not None:
        for i, corner in enumerate(corners):
            x, y = corner.ravel()
            features.append({
                'id': f'point_{i}',
                'position': (float(x), float(y)),
                'type': 'corner'
            })
    
    # Also try with SIFT for more robust features
    sift = cv2.SIFT_create()
    kp, descriptors = sift.detectAndCompute(gray, None)
    
    if kp:
        for i, keypoint in enumerate(kp):
            # Only add if not already in the corner list (avoid duplicates)
            x, y = keypoint.pt
            is_duplicate = False
            for feat in features:
                if abs(feat['position'][0] - x) < 5 and abs(feat['position'][1] - y) < 5:
                    is_duplicate = True
                    break
            if not is_duplicate:
                features.append({
                    'id': f'sift_{i}',
                    'position': (float(x), float(y)),
                    'type': 'sift',
                    'descriptor': descriptors[i].tolist() if descriptors is not None and i < len(descriptors) else None
                })
    
    return features


def match_feature_points(prev_features: List[Dict[str, Any]], curr_features: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Match feature points between frames"""
    matches = {}
    
    for prev_feat in prev_features:
        best_match = None
        best_distance = float('inf')
        
        for curr_feat in curr_features:
            # Calculate Euclidean distance
            prev_pos = prev_feat['position']
            curr_pos = curr_feat['position']
            dist = math.sqrt((prev_pos[0] - curr_pos[0])**2 + (prev_pos[1] - curr_pos[1])**2)
            
            if dist < best_distance and dist < 50:  # Threshold to avoid wrong matches
                best_distance = dist
                best_match = curr_feat
        
        if best_match:
            matches[prev_feat['id']] = {
                'prev_pos': prev_feat['position'],
                'curr_pos': best_match['position'],
                'distance': best_distance
            }
    
    return matches


def extract_objects(frame: np.ndarray) -> List[Dict[str, Any]]:
    """Extract objects from a frame using simple contour detection"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    objects = []
    for i, contour in enumerate(contours):
        if cv2.contourArea(contour) > 100:  # Filter small contours
            # Calculate bounding box
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w / 2
            center_y = y + h / 2
            
            objects.append({
                'id': f'obj_{i}',
                'position': (float(center_x), float(center_y)),
                'bbox': (int(x), int(y), int(w), int(h)),
                'area': float(cv2.contourArea(contour))
            })
    
    return objects


def run_motion_inference_cycle(frames: List[np.ndarray], 
                              target_frame_count: int = 30, 
                              physical_constraints: bool = True) -> Dict[str, Any]:
    """Main function to infer continuous motion from sparse frames"""
    try:
        if not frames or len(frames) < 2:
            return {
                'success': False,
                'error': 'At least 2 frames are required',
                'motion_trajectories': [],
                'interpolated_frames': []
            }
        
        # Extract features and objects from each frame
        frame_features = []
        frame_objects = []
        
        for i, frame in enumerate(frames):
            features = extract_feature_points(frame)
            objects = extract_objects(frame)
            frame_features.append(features)
            frame_objects.append(objects)
        
        # Match features between consecutive frames
        all_matches = []
        for i in range(len(frames) - 1):
            matches = match_feature_points(frame_features[i], frame_features[i + 1])
            all_matches.append(matches)
        
        # Calculate motion trajectories for each object
        trajectories = []
        
        for obj_idx, obj in enumerate(frame_objects[0]):
            # Track this object through all frames
            positions = [obj['position']]
            velocities = []
            
            # Try to find this object in subsequent frames
            for frame_idx in range(1, len(frame_objects)):
                best_match = None
                min_dist = float('inf')
                
                for next_obj in frame_objects[frame_idx]:
                    dist = math.sqrt(
                        (obj['position'][0] - next_obj['position'][0])**2 + 
                        (obj['position'][1] - next_obj['position'][1])**2
                    )
                    if dist < min_dist:
                        min_dist = dist
                        best_match = next_obj
                
                if best_match and min_dist < 100:  # Threshold for reasonable object tracking
                    positions.append(best_match['position'])
                    # Calculate velocity from position difference
                    if len(positions) > 1:
                        dt = 1.0  # Assume 1 time unit between frames
                        last_pos = positions[-2]
                        curr_pos = positions[-1]
                        velocity = calculate_motion_vector(last_pos, curr_pos, dt)
                        velocities.append(velocity)
            
            if len(positions) >= 2:
                # Create trajectory object
                trajectory = MotionTrajectory(
                    object_id=f'obj_{obj_idx}',
                    positions=positions,
                    velocities=velocities,
                    accelerations=[]
                )
                
                # Apply physical constraints if requested
                if physical_constraints:
                    trajectory = apply_physical_constraints(trajectory)
                
                # Interpolate to generate more intermediate frames
                trajectory = interpolate_motion(trajectory, target_frame_count)
                
                trajectories.append({
                    'object_id': trajectory.object_id,
                    'positions': [(float(x), float(y)) for x, y in trajectory.positions],
                    'velocities': [
                        {
                            'x': float(v.x),
                            'y': float(v.y),
                            'magnitude': float(v.magnitude),
                            'angle': float(v.angle)
                        } for v in trajectory.velocities
                    ]
                })
        
        # Generate interpolated frames based on trajectories
        interpolated_frames = []
        for i in range(target_frame_count):
            # Create a new frame based on the positions of objects in this time step
            if frames:
                # Use the first frame as a base
                base_frame = frames[0].copy()
                
                # Draw current positions of objects
                for traj in trajectories:
                    if i < len(traj['positions']):
                        pos = traj['positions'][i]
                        cv2.circle(base_frame, (int(pos[0]), int(pos[1])), 10, (0, 255, 0), -1)
                
                interpolated_frames.append(base_frame.tolist())
        
        return {
            'success': True,
            'motion_trajectories': trajectories,
            'interpolated_frames_count': len(interpolated_frames),
            'feature_matches': [list(matches.keys()) for matches in all_matches],
            'object_count': len(frame_objects[0]) if frame_objects else 0
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'motion_trajectories': [],
            'interpolated_frames': []
        }


def validate_motion_consistency(trajectories: List[Dict[str, Any]], threshold: float = 0.5) -> Dict[str, Any]:
    """Validate the consistency of inferred motion"""
    try:
        inconsistencies = []
        
        for traj in trajectories:
            positions = traj['positions']
            velocities = traj['velocities']
            
            # Check for position jumps (unrealistic motion)
            for i in range(1, len(positions)):
                dx = positions[i][0] - positions[i-1][0]
                dy = positions[i][1] - positions[i-1][1]
                dist = math.sqrt(dx**2 + dy**2)
                
                # If distance is too large compared to average velocity, it's inconsistent
                if velocities and i-1 < len(velocities):
                    avg_vel = velocities[i-1]['magnitude']
                    if avg_vel > 0 and dist > avg_vel * threshold * 10:  # Threshold for inconsistency
                        inconsistencies.append({
                            'object_id': traj['object_id'],
                            'frame_idx': i,
                            'position': positions[i],
                            'velocity': velocities[i-1],
                            'distance': dist,
                            'issue': 'position_jump'
                        })
        
        return {
            'valid': len(inconsistencies) == 0,
            'inconsistencies': inconsistencies,
            'consistency_score': 1.0 - min(len(inconsistencies) / max(len(trajectories), 1), 1.0)
        }
    
    except Exception as e:
        return {
            'valid': False,
            'inconsistencies': [{'error': str(e)}],
            'consistency_score': 0.0
        }


def run_inference_with_validation(frames: List[np.ndarray], 
                                target_frame_count: int = 30, 
                                physical_constraints: bool = True,
                                validate: bool = True) -> Dict[str, Any]:
    """Run motion inference with optional validation"""
    try:
        result = run_motion_inference_cycle(frames, target_frame_count, physical_constraints)
        
        if not result['success']:
            return result
        
        if validate:
            validation_result = validate_motion_consistency(result['motion_trajectories'])
            result['validation'] = validation_result
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'motion_trajectories': [],
            'interpolated_frames': []
        }