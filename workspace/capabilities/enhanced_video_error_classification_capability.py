# capability_name: enhanced_video_error_classification_capability

import re
import traceback
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict

class EnhancedErrorFeatureExtractor:
    @staticmethod
    def extract_features(error_obj: Exception) -> Dict[str, Any]:
        """从异常对象中提取结构化特征，特别关注视频处理相关特征"""
        try:
            error_type = type(error_obj).__name__
            error_message = str(error_obj)
            stack_trace = traceback.format_exception(type(error_obj), error_obj, error_obj.__traceback__)
            
            # 提取文件路径和行号
            file_info = []
            for line in stack_trace:
                if 'File "' in line and 'line' in line:
                    match = re.search(r'File "([^"]+)", line (\d+)', line)
                    if match:
                        file_info.append({
                            'file_path': match.group(1),
                            'line_number': int(match.group(2))
                        })
            
            # 提取关键错误信息
            keywords = re.findall(r'\w+', error_message.lower())
            keywords = [kw for kw in keywords if len(kw) > 3]
            
            # 特别提取视频处理相关特征
            video_features = {
                'codec_related': any(kw in ['codec', 'encoder', 'decoder', 'h264', 'hevc', 'avc'] for kw in keywords),
                'resolution_related': any(kw in ['resolution', 'width', 'height', '4k', '1080p', '720p'] for kw in keywords),
                'frame_related': any(kw in ['frame', 'fps', 'framerate', 'timestamp'] for kw in keywords),
                'physics_related': any(kw in ['physics', 'motion', 'velocity', 'acceleration', 'consistency'] for kw in keywords),
                'parameter_related': any(kw in ['parameter', 'argument', 'json', 'validation', 'contract'] for kw in keywords)
            }
            
            return {
                'error_type': error_type,
                'error_message': error_message,
                'stack_trace': stack_trace,
                'file_info': file_info,
                'keywords': keywords[:15],  # 增加关键词数量限制
                'video_features': video_features,
                'timestamp': __import__('time').time()
            }
        except Exception as e:
            return {
                'error_type': 'FeatureExtractionError',
                'error_message': f'无法提取错误特征: {str(e)}',
                'stack_trace': [],
                'file_info': [],
                'keywords': [],
                'video_features': {},
                'timestamp': __import__('time').time()
            }

class EnhancedSemanticErrorClassifier:
    @staticmethod
    def classify_error(features: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """基于语义理解的精细化错误分类，特别针对视频处理场景"""
        try:
            error_type = features.get('error_type', 'UnknownError')
            error_message = features.get('error_message', '').lower()
            keywords = features.get('keywords', [])
            video_features = features.get('video_features', {})
            
            # 定义精细化的错误分类规则
            classification_rules = {
                # 参数验证相关错误
                'ParameterValidationError': [
                    'parameter', 'argument', 'invalid', 'value', 'expected', 'got', 'type', 
                    'json', 'schema', 'validation', 'contract', 'missing', 'required'
                ],
                'JSONSerializationError': [
                    'json', 'serialize', 'deserialize', 'loads', 'dumps', 'string', 'dict', 
                    'object', 'parse', 'format', 'malformed'
                ],
                # 视频编解码相关错误
                'VideoCodecError': [
                    'codec', 'encoder', 'decoder', 'h264', 'hevc', 'avc', 'mpeg', 'compression',
                    'encode', 'decode', 'unsupported', 'format', 'container'
                ],
                'VideoResolutionError': [
                    'resolution', 'width', 'height', 'dimension', 'size', '4k', '1080p', '720p',
                    'scale', 'resize', 'aspect', 'ratio'
                ],
                'VideoFrameError': [
                    'frame', 'fps', 'framerate', 'timestamp', 'duration', 'keyframe', 'interframe',
                    'sequence', 'temporal', 'synchronization'
                ],
                # 物理合规性相关错误
                'PhysicsComplianceError': [
                    'physics', 'motion', 'velocity', 'acceleration', 'consistency', 'constraint',
                    'temporal', 'continuity', 'semantic', 'coherence', 'realistic'
                ],
                'TemporalConsistencyError': [
                    'temporal', 'consistency', 'continuity', 'sequence', 'flow', 'transition',
                    'smooth', 'jitter', 'artifact', 'discontinuity'
                ],
                # 依赖和环境相关错误
                'DependencyError': [
                    'import', 'module', 'not found', 'missing', 'require', 'dependency', 'package',
                    'install', 'library', 'ffmpeg', 'opencv', 'tesseract'
                ],
                'SystemResourceError': [
                    'memory', 'resource', 'limit', 'insufficient', 'exhausted', 'cpu', 'disk',
                    'buffer', 'overflow', 'timeout', 'performance'
                ],
                # 文件和路径相关错误
                'FileIOError': [
                    'file', 'directory', 'path', 'not found', 'access', 'permission', 'read',
                    'write', 'open', 'close', 'exists', 'create'
                ],
                # 网络和连接相关错误
                'NetworkError': [
                    'connection', 'network', 'timeout', 'refused', 'unreachable', 'dns', 'proxy',
                    'ssl', 'certificate', 'bandwidth', 'latency'
                ]
            }
            
            # 执行多维度分类
            classification_scores = defaultdict(int)
            
            # 1. 基于关键词的基础分类
            for category, category_keywords in classification_rules.items():
                for kw in keywords:
                    if kw in category_keywords:
                        classification_scores[category] += 15
                for cat_kw in category_keywords:
                    if cat_kw in error_message:
                        classification_scores[category] += 2
            
            # 2. 基于视频特征的增强分类
            if video_features.get('codec_related'):
                classification_scores['VideoCodecError'] += 20
            if video_features.get('resolution_related'):
                classification_scores['VideoResolutionError'] += 20
            if video_features.get('frame_related'):
                classification_scores['VideoFrameError'] += 20
            if video_features.get('physics_related'):
                classification_scores['PhysicsComplianceError'] += 25
                classification_scores['TemporalConsistencyError'] += 15
            if video_features.get('parameter_related'):
                classification_scores['ParameterValidationError'] += 20
                classification_scores['JSONSerializationError'] += 15
            
            # 3. 基于错误类型的权重调整
            error_type_weights = {
                'ValueError': {'ParameterValidationError': 10, 'JSONSerializationError': 8},
                'TypeError': {'ParameterValidationError': 12, 'JSONSerializationError': 10},
                'KeyError': {'ParameterValidationError': 8, 'JSONSerializationError': 15},
                'AttributeError': {'DependencyError': 10, 'FileIOError': 5},
                'FileNotFoundError': {'FileIOError': 25},
                'ImportError': {'DependencyError': 30},
                'MemoryError': {'SystemResourceError': 30},
                'TimeoutError': {'NetworkError': 15, 'SystemResourceError': 10}
            }
            
            if error_type in error_type_weights:
                for category, weight in error_type_weights[error_type].items():
                    classification_scores[category] += weight
            
            # 选择最高分的分类作为主要分类
            if classification_scores:
                primary_classification = max(classification_scores, key=classification_scores.get)
                max_score = classification_scores[primary_classification]
                total_score = sum(classification_scores.values())
                confidence = max_score / total_score if total_score > 0 else 0.0
                
                # 获取前3个最可能的分类
                top_classifications = sorted(classification_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            else:
                primary_classification = 'UnknownError'
                confidence = 0.0
                top_classifications = [('UnknownError', 0)]
            
            return {
                'primary_classification': primary_classification,
                'confidence': confidence,
                'top_classifications': top_classifications,
                'all_classifications': dict(classification_scores),
                'semantic_features': {
                    'message_length': len(error_message),
                    'keyword_count': len(keywords),
                    'error_type': error_type,
                    'video_specific_features': video_features
                }
            }
        except Exception as e:
            return {
                'primary_classification': 'ClassificationError',
                'confidence': 0.0,
                'top_classifications': [('ClassificationError', 0)],
                'all_classifications': {},
                'semantic_features': {},
                'error': f'语义分类失败: {str(e)}'
            }

class EnhancedRepairSuggestionEngine:
    @staticmethod
    def generate_suggestions(classification: str, features: Dict[str, Any], 
                           context: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成针对性修复建议，特别针对视频处理场景"""
        try:
            suggestions = []
            
            # 基于精细化分类的建议规则
            suggestion_rules = {
                # 参数验证相关
                'ParameterValidationError': [
                    {
                        'type': 'ParameterContractValidation',
                        'description': '验证参数契约是否符合要求',
                        'action': 'validate_parameter_contract',
                        'priority': 'high'
                    },
                    {
                        'type': 'ParameterTypeCoercion',
                        'description': '尝试自动转换参数类型（如字典转JSON字符串）',
                        'action': 'coerce_parameter_types',
                        'priority': 'high'
                    },
                    {
                        'type': 'ParameterDefaultFallback',
                        'description': '使用默认参数值进行回退',
                        'action': 'fallback_to_defaults',
                        'priority': 'medium'
                    }
                ],
                'JSONSerializationError': [
                    {
                        'type': 'JSONFormatValidation',
                        'description': '验证JSON格式是否正确',
                        'action': 'validate_json_format',
                        'priority': 'high'
                    },
                    {
                        'type': 'DictToStringSerialization',
                        'description': '将字典对象显式序列化为JSON字符串',
                        'action': 'serialize_dict_to_json',
                        'priority': 'critical'
                    },
                    {
                        'type': 'StringToDictParsing',
                        'description': '安全解析JSON字符串为字典对象',
                        'action': 'parse_json_to_dict',
                        'priority': 'high'
                    }
                ],
                # 视频编解码相关
                'VideoCodecError': [
                    {
                        'type': 'CodecSupportCheck',
                        'description': '检查系统是否支持所需的编解码器',
                        'action': 'check_codec_support',
                        'priority': 'high'
                    },
                    {
                        'type': 'AlternativeCodecFallback',
                        'description': '尝试使用备用编解码器',
                        'action': 'fallback_to_alternative_codec',
                        'priority': 'medium'
                    },
                    {
                        'type': 'HardwareAccelerationCheck',
                        'description': '检查硬件加速支持',
                        'action': 'validate_hardware_acceleration',
                        'priority': 'low'
                    }
                ],
                'VideoResolutionError': [
                    {
                        'type': 'ResolutionValidation',
                        'description': '验证分辨率参数是否有效',
                        'action': 'validate_resolution_parameters',
                        'priority': 'high'
                    },
                    {
                        'type': 'ResolutionScaling',
                        'description': '自动调整到支持的分辨率',
                        'action': 'auto_scale_resolution',
                        'priority': 'medium'
                    }
                ],
                'VideoFrameError': [
                    {
                        'type': 'FramerateValidation',
                        'description': '验证帧率参数是否合理',
                        'action': 'validate_framerate',
                        'priority': 'high'
                    },
                    {
                        'type': 'FrameSequenceRepair',
                        'description': '修复帧序列中的时间戳问题',
                        'action': 'repair_frame_timestamps',
                        'priority': 'medium'
                    }
                ],
                # 物理合规性相关
                'PhysicsComplianceError': [
                    {
                        'type': 'PhysicsConstraintValidation',
                        'description': '验证视频帧间物理约束是否满足',
                        'action': 'validate_physics_constraints',
                        'priority': 'critical'
                    },
                    {
                        'type': 'MotionSemanticAnalysis',
                        'description': '分析运动语义的合理性',
                        'action': 'analyze_motion_semantics',
                        'priority': 'high'
                    },
                    {
                        'type': 'PhysicalLawEnforcement',
                        'description': '强制执行物理定律约束',
                        'action': 'enforce_physical_laws',
                        'priority': 'critical'
                    }
                ],
                'TemporalConsistencyError': [
                    {
                        'type': 'TemporalContinuityCheck',
                        'description': '检查帧间时间连续性',
                        'action': 'validate_temporal_continuity',
                        'priority': 'critical'
                    },
                    {
                        'type': 'FrameInterpolation',
                        'description': '插入缺失的中间帧以保持连续性',
                        'action': 'interpolate_missing_frames',
                        'priority': 'high'
                    },
                    {
                        'type': 'MotionSmoothing',
                        'description': '平滑不连续的运动轨迹',
                        'action': 'smooth_motion_trajectory',
                        'priority': 'medium'
                    }
                ],
                # 依赖和环境相关
                'DependencyError': [
                    {
                        'type': 'DependencyInstallation',
                        'description': '自动安装缺失的依赖包',
                        'action': 'install_missing_dependencies',
                        'priority': 'critical'
                    },
                    {
                        'type': 'SystemPathValidation',
                        'description': '验证系统路径和可执行文件',
                        'action': 'validate_system_paths',
                        'priority': 'high'
                    }
                ],
                'SystemResourceError': [
                    {
                        'type': 'ResourceOptimization',
                        'description': '优化资源使用策略',
                        'action': 'optimize_resource_usage',
                        'priority': 'high'
                    },
                    {
                        'type': 'BatchProcessing',
                        'description': '切换到批处理模式以减少内存使用',
                        'action': 'switch_to_batch_processing',
                        'priority': 'medium'
                    }
                ],
                # 文件和路径相关
                'FileIOError': [
                    {
                        'type': 'PathExistenceCheck',
                        'description': '验证文件路径是否存在',
                        'action': 'check_path_existence',
                        'priority': 'critical'
                    },
                    {
                        'type': 'PermissionValidation',
                        'description': '检查文件访问权限',
                        'action': 'validate_file_permissions',
                        'priority': 'high'
                    }
                ],
                # 网络相关
                'NetworkError': [
                    {
                        'type': 'ConnectionRetry',
                        'description': '重试网络连接',
                        'action': 'retry_network_connection',
                        'priority': 'medium'
                    },
                    {
                        'type': 'OfflineModeFallback',
                        'description': '切换到离线模式',
                        'action': 'switch_to_offline_mode',
                        'priority': 'low'
                    }
                ]
            }
            
            # 获取特定分类的建议
            if classification in suggestion_rules:
                suggestions.extend(suggestion_rules[classification])
            
            # 添加通用建议
            suggestions.extend([
                {
                    'type': 'DetailedLogging',
                    'description': '记录详细的错误上下文信息',
                    'action': 'log_detailed_context',
                    'priority': 'low'
                },
                {
                    'type': 'RegressionTestCreation',
                    'description': '基于此错误创建回归测试用例',
                    'action': 'create_regression_test',
                    'priority': 'medium'
                }
            ])
            
            # 按优先级排序
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 999))
            
            return suggestions
        except Exception as e:
            return [
                {
                    'type': 'Error',
                    'description': f'建议生成失败: {str(e)}',
                    'action': 'error_in_suggestion_engine',
                    'priority': 'critical'
                }
            ]

def run_enhanced_error_mapping_cycle(error_obj: Exception, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行增强版错误映射周期，提供更精细的错误分类和针对性修复建议
    """
    try:
        # 1. 提取增强版错误特征
        feature_extractor = EnhancedErrorFeatureExtractor()
        features = feature_extractor.extract_features(error_obj)
        
        # 2. 分析执行上下文（复用现有分析器）
        from capabilities.semantic_error_mapping_capability import ContextAnalyzer
        context_analyzer = ContextAnalyzer()
        context_analysis = context_analyzer.analyze_context(context_data)
        
        # 3. 增强版语义错误分类
        classifier = EnhancedSemanticErrorClassifier()
        classification_result = classifier.classify_error(features, context_analysis)
        
        # 4. 生成精细化修复建议
        suggestion_engine = EnhancedRepairSuggestionEngine()
        suggestions = suggestion_engine.generate_suggestions(
            classification_result.get('primary_classification', 'UnknownError'),
            features,
            context_analysis
        )
        
        # 5. 组装结果
        result = {
            'status': 'success',
            'error_features': features,
            'context_analysis': context_analysis,
            'classification': classification_result,
            'suggestions': suggestions,
            'standardized_error_id': f"{classification_result.get('primary_classification', 'UnknownError')}_{hash(features.get('error_message', '')) % 100000}",
            'confidence_score': classification_result.get('confidence', 0.0),
            'timestamp': features.get('timestamp'),
            'enhanced_mapping': True
        }
        
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error_type': 'EnhancedErrorMappingCycleError',
            'error_message': str(e),
            'timestamp': __import__('time').time(),
            'enhanced_mapping': False
        }

def check_enhanced_error_mapping_capability() -> Dict[str, Any]:
    """检查增强版错误映射能力的可用性"""
    try:
        # 创建一个测试异常
        test_error = ValueError("Missing required parameter: video_path must be provided as JSON string")
        
        # 测试上下文数据
        test_context = {
            'system_info': {
                'os': 'linux',
                'python_version': '3.9'
            },
            'parameters': {
                'input_args': {'some_dict': 'value'},
                'expected_format': 'json_string'
            },
            'dependencies': {
                'numpy': '1.21.0',
                'opencv-python': '4.5.0'
            }
        }
        
        # 执行测试映射
        result = run_enhanced_error_mapping_cycle(test_error, test_context)
        
        return {
            'status': 'available',
            'capability': 'enhanced_video_error_classification',
            'test_result': result.get('status'),
            'timestamp': __import__('time').time()
        }
    except Exception as e:
        return {
            'status': 'unavailable',
            'capability': 'enhanced_video_error_classification',
            'error': str(e),
            'timestamp': __import__('time').time()
        }