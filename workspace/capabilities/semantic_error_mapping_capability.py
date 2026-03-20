# capability_name: semantic_error_mapping_capability

import re
import traceback
import json
from typing import Dict, List, Any, Optional
from collections import defaultdict


class ErrorFeatureExtractor:
    @staticmethod
    def extract_features(error_obj: Exception) -> Dict[str, Any]:
        """从异常对象中提取结构化特征"""
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
            
            return {
                'error_type': error_type,
                'error_message': error_message,
                'stack_trace': stack_trace,
                'file_info': file_info,
                'keywords': keywords[:10],  # 限制关键词数量
                'timestamp': __import__('time').time()
            }
        except Exception as e:
            return {
                'error_type': 'FeatureExtractionError',
                'error_message': f'无法提取错误特征: {str(e)}',
                'stack_trace': [],
                'file_info': [],
                'keywords': [],
                'timestamp': __import__('time').time()
            }


class ContextAnalyzer:
    @staticmethod
    def analyze_context(context_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析当前执行上下文"""
        try:
            system_info = context_data.get('system_info', {})
            parameters = context_data.get('parameters', {})
            dependencies = context_data.get('dependencies', {})
            
            # 分析系统状态
            system_status = {
                'os': system_info.get('os', 'unknown'),
                'python_version': system_info.get('python_version', 'unknown'),
                'memory_usage': system_info.get('memory_usage', 'unknown'),
                'cpu_usage': system_info.get('cpu_usage', 'unknown')
            }
            
            # 分析参数
            param_analysis = {
                'param_count': len(parameters),
                'param_types': {k: type(v).__name__ for k, v in parameters.items()},
                'param_sizes': {k: len(str(v)) if hasattr(v, '__len__') else 1 for k, v in parameters.items()}
            }
            
            # 分析依赖
            dependency_analysis = {
                'dependency_count': len(dependencies),
                'dependency_versions': dependencies,
                'critical_deps': [k for k, v in dependencies.items() if 'critical' in k.lower()]
            }
            
            return {
                'system_status': system_status,
                'param_analysis': param_analysis,
                'dependency_analysis': dependency_analysis,
                'raw_context': context_data
            }
        except Exception as e:
            return {
                'system_status': {},
                'param_analysis': {},
                'dependency_analysis': {},
                'raw_context': context_data,
                'error': f'上下文分析失败: {str(e)}'
            }


class PatternMatcher:
    def __init__(self):
        self.pattern_database = []
        
    def add_pattern(self, pattern: Dict[str, Any]):
        """添加历史错误模式"""
        self.pattern_database.append(pattern)
        
    def match_patterns(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """匹配相似错误模式"""
        try:
            matched_patterns = []
            error_message = features.get('error_message', '').lower()
            keywords = features.get('keywords', [])
            
            for pattern in self.pattern_database:
                score = 0
                pattern_message = pattern.get('error_message', '').lower()
                
                # 基于错误消息的匹配
                if pattern_message in error_message:
                    score += 50
                
                # 基于关键词的匹配
                pattern_keywords = pattern.get('keywords', [])
                for kw in keywords:
                    if kw in pattern_keywords:
                        score += 10
                
                # 基于错误类型的匹配
                if pattern.get('error_type') == features.get('error_type'):
                    score += 30
                
                if score > 0:
                    matched_patterns.append({
                        'pattern': pattern,
                        'similarity_score': score
                    })
            
            # 按相似度排序
            matched_patterns.sort(key=lambda x: x['similarity_score'], reverse=True)
            return matched_patterns[:5]  # 返回前5个最相似的模式
        except Exception as e:
            return [{'error': f'模式匹配失败: {str(e)}'}]


class SemanticErrorClassifier:
    @staticmethod
    def classify_error(features: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """基于语义理解的错误分类"""
        try:
            error_type = features.get('error_type', 'UnknownError')
            error_message = features.get('error_message', '').lower()
            keywords = features.get('keywords', [])
            
            # 定义错误分类规则
            classification_rules = {
                'ParameterError': [
                    'parameter', 'argument', 'invalid', 'value', 'expected', 'got', 'type'
                ],
                'DependencyError': [
                    'import', 'module', 'not found', 'missing', 'require', 'dependency'
                ],
                'FileError': [
                    'file', 'directory', 'path', 'not found', 'access', 'permission'
                ],
                'RuntimeError': [
                    'runtime', 'execution', 'process', 'terminated', 'timeout'
                ],
                'ConnectionError': [
                    'connection', 'network', 'timeout', 'refused', 'unreachable'
                ],
                'ResourceError': [
                    'memory', 'resource', 'limit', 'insufficient', 'exhausted'
                ]
            }
            
            # 执行分类
            classification_scores = defaultdict(int)
            for category, category_keywords in classification_rules.items():
                for kw in keywords:
                    if kw in category_keywords:
                        classification_scores[category] += 10
                for cat_kw in category_keywords:
                    if cat_kw in error_message:
                        classification_scores[category] += 1
            
            # 选择最高分的分类
            if classification_scores:
                primary_classification = max(classification_scores, key=classification_scores.get)
                confidence = classification_scores[primary_classification] / sum(classification_scores.values())
            else:
                primary_classification = 'UnknownError'
                confidence = 0.0
            
            return {
                'primary_classification': primary_classification,
                'confidence': confidence,
                'all_classifications': dict(classification_scores),
                'semantic_features': {
                    'message_length': len(error_message),
                    'keyword_count': len(keywords),
                    'error_type': error_type
                }
            }
        except Exception as e:
            return {
                'primary_classification': 'ClassificationError',
                'confidence': 0.0,
                'all_classifications': {},
                'semantic_features': {},
                'error': f'语义分类失败: {str(e)}'
            }


class RepairSuggestionEngine:
    @staticmethod
    def generate_suggestions(classification: str, features: Dict[str, Any], 
                           context: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成针对性修复建议"""
        try:
            suggestions = []
            
            # 基于分类的建议规则
            suggestion_rules = {
                'ParameterError': [
                    {
                        'type': 'ParameterValidation',
                        'description': '检查参数类型和值是否符合预期',
                        'action': 'validate_parameters'
                    },
                    {
                        'type': 'ParameterFix',
                        'description': '使用默认值或转换参数类型',
                        'action': 'parameter_coercion'
                    }
                ],
                'DependencyError': [
                    {
                        'type': 'DependencyCheck',
                        'description': '检查依赖包是否正确安装',
                        'action': 'validate_dependencies'
                    },
                    {
                        'type': 'DependencyFix',
                        'description': '重新安装或更新依赖包',
                        'action': 'install_dependencies'
                    }
                ],
                'FileError': [
                    {
                        'type': 'PathValidation',
                        'description': '验证文件路径是否存在',
                        'action': 'check_path_exists'
                    },
                    {
                        'type': 'PermissionCheck',
                        'description': '检查文件访问权限',
                        'action': 'validate_permissions'
                    }
                ],
                'RuntimeError': [
                    {
                        'type': 'ProcessMonitor',
                        'description': '监控进程状态和资源使用',
                        'action': 'monitor_process'
                    },
                    {
                        'type': 'RestartProcess',
                        'description': '重启失败的进程',
                        'action': 'restart_process'
                    }
                ],
                'ConnectionError': [
                    {
                        'type': 'NetworkCheck',
                        'description': '检查网络连接状态',
                        'action': 'validate_network'
                    },
                    {
                        'type': 'RetryConnection',
                        'description': '重试网络连接',
                        'action': 'retry_connection'
                    }
                ],
                'ResourceError': [
                    {
                        'type': 'ResourceMonitor',
                        'description': '监控系统资源使用情况',
                        'action': 'monitor_resources'
                    },
                    {
                        'type': 'ResourceOptimization',
                        'description': '优化资源使用或清理资源',
                        'action': 'optimize_resources'
                    }
                ]
            }
            
            # 获取特定分类的建议
            if classification in suggestion_rules:
                suggestions.extend(suggestion_rules[classification])
            
            # 添加通用建议
            suggestions.extend([
                {
                    'type': 'LogError',
                    'description': '记录错误详情到日志',
                    'action': 'log_error_details'
                },
                {
                    'type': 'ErrorReport',
                    'description': '生成错误报告',
                    'action': 'generate_error_report'
                }
            ])
            
            return suggestions
        except Exception as e:
            return [
                {
                    'type': 'Error',
                    'description': f'建议生成失败: {str(e)}',
                    'action': 'error_in_suggestion_engine'
                }
            ]


def run_error_mapping_cycle(error_obj: Exception, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行错误映射周期，从异常对象和上下文数据生成标准化错误信息
    """
    try:
        # 1. 提取错误特征
        feature_extractor = ErrorFeatureExtractor()
        features = feature_extractor.extract_features(error_obj)
        
        # 2. 分析执行上下文
        context_analyzer = ContextAnalyzer()
        context_analysis = context_analyzer.analyze_context(context_data)
        
        # 3. 匹配历史错误模式
        pattern_matcher = PatternMatcher()
        # 这里可以加载历史模式数据
        matched_patterns = pattern_matcher.match_patterns(features)
        
        # 4. 语义错误分类
        classifier = SemanticErrorClassifier()
        classification_result = classifier.classify_error(features, context_analysis)
        
        # 5. 生成修复建议
        suggestion_engine = RepairSuggestionEngine()
        suggestions = suggestion_engine.generate_suggestions(
            classification_result.get('primary_classification', 'UnknownError'),
            features,
            context_analysis
        )
        
        # 6. 组装结果
        result = {
            'status': 'success',
            'error_features': features,
            'context_analysis': context_analysis,
            'matched_patterns': matched_patterns,
            'classification': classification_result,
            'suggestions': suggestions,
            'standardized_error_id': f"{classification_result.get('primary_classification', 'UnknownError')}_{hash(features.get('error_message', '')) % 10000}",
            'confidence_score': classification_result.get('confidence', 0.0),
            'timestamp': features.get('timestamp')
        }
        
        return result
    except Exception as e:
        return {
            'status': 'error',
            'error_type': 'ErrorMappingCycleError',
            'error_message': str(e),
            'timestamp': __import__('time').time()
        }


def check_error_mapping_capability() -> Dict[str, Any]:
    """检查错误映射能力的可用性"""
    try:
        # 创建一个测试异常
        test_error = ValueError("Invalid parameter value: expected integer, got string")
        
        # 测试上下文数据
        test_context = {
            'system_info': {
                'os': 'linux',
                'python_version': '3.9'
            },
            'parameters': {
                'input_value': 'test_string',
                'expected_type': 'integer'
            },
            'dependencies': {
                'numpy': '1.21.0',
                'pandas': '1.3.0'
            }
        }
        
        # 执行测试映射
        result = run_error_mapping_cycle(test_error, test_context)
        
        return {
            'status': 'available',
            'capability': 'semantic_error_mapping',
            'test_result': result.get('status'),
            'timestamp': __import__('time').time()
        }
    except Exception as e:
        return {
            'status': 'unavailable',
            'capability': 'semantic_error_mapping',
            'error': str(e),
            'timestamp': __import__('time').time()
        }