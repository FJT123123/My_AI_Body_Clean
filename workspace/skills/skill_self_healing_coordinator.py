"""
自动生成的技能模块
需求: 创建一个自我修复协调器技能，能够检测任务执行中的错误，分析错误类型，并执行适当的修复操作。该技能应能处理依赖缺失、参数错误、路径问题等常见错误，并在修复后验证修复是否成功。技能应包含以下功能：1) 错误检测与分类；2) 依赖检查与安装；3) 参数验证与修正；4) 路径验证与修复；5) 修复验证与结果报告。
生成时间: 2026-03-13 16:21:01
"""

# skill_name: self_healing_coordinator
import os
import subprocess
import json
import re
import sys
from pathlib import Path


def main(args=None):
    """
    自我修复协调器技能：检测任务执行中的错误，分析错误类型，并执行适当的修复操作。
    能够处理依赖缺失、参数错误、路径问题等常见错误，并在修复后验证修复是否成功。
    """
    import json
    
    # 处理字符串输入
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，创建一个默认的错误信息
            args = {"error_info": {"error_message": args}, "task_context": {}}
    
    if args is None:
        args = {}
    
    error_info = args.get('error_info', {})
    task_context = args.get('task_context', {})
    repair_strategy = args.get('repair_strategy', 'auto')
    validation_type = args.get('validation_type', None)
    
    print(f"DEBUG: args = {args}")
    print(f"DEBUG: error_info = {error_info}")
    
    # 直接验证模式：如果提供了validation_type，直接执行验证而不进行错误修复
    if validation_type == 'file_output':
        target_dir = args.get('target_dir')
        expected_count = args.get('expected_count', 0)
        file_pattern = args.get('file_pattern', '*')
        
        validation_result = validate_file_output(target_dir, expected_count, file_pattern)
        
        return {
            'result': {
                'validation_type': 'file_output',
                'validation_result': validation_result,
                'direct_validation': True
            },
            'insights': [f"直接执行文件产出验证: {validation_result.get('validation_result', '未知结果')}"],
            'facts': []
        }
    
    result = {
        'repair_performed': False,
        'repair_type': None,
        'repair_result': None,
        'validation_result': None,
        'next_action': 'retry_task'
    }
    
    insights = []
    facts = []
    
    # 1. 错误检测与分类
    error_type = classify_error(error_info)
    result['detected_error_type'] = error_type
    insights.append(f"检测到错误类型: {error_type}")
    
    # 2. 根据错误类型执行修复
    if error_type == 'dependency_missing':
        repair_result = handle_dependency_missing(error_info)
        result['repair_type'] = 'dependency_repair'
        result['repair_result'] = repair_result
        result['repair_performed'] = True
        
        if repair_result['success']:
            validation_result = validate_dependency_installation(repair_result['dependency'])
            result['validation_result'] = validation_result
            if validation_result['success']:
                insights.append(f"依赖修复成功: {repair_result['dependency']}")
            else:
                insights.append(f"依赖修复验证失败: {repair_result['dependency']}")
                result['next_action'] = 'abort_task'
        else:
            insights.append(f"依赖修复失败: {repair_result['dependency']}")
            result['next_action'] = 'abort_task'
    
    elif error_type == 'parameter_error':
        repair_result = handle_parameter_error(error_info, task_context)
        result['repair_type'] = 'parameter_repair'
        result['repair_result'] = repair_result
        result['repair_performed'] = True
        
        if repair_result['success']:
            validation_result = validate_parameters(repair_result['corrected_params'])
            result['validation_result'] = validation_result
            if validation_result['success']:
                insights.append("参数修复成功")
            else:
                insights.append("参数修复验证失败")
                result['next_action'] = 'abort_task'
        else:
            insights.append("参数修复失败")
            result['next_action'] = 'abort_task'
    
    elif error_type == 'path_error':
        repair_result = handle_path_error(error_info, task_context)
        result['repair_type'] = 'path_repair'
        result['repair_result'] = repair_result
        result['repair_performed'] = True
        
        if repair_result['success']:
            validation_result = validate_path(repair_result['corrected_path'])
            result['validation_result'] = validation_result
            if validation_result['success']:
                insights.append("路径修复成功")
            else:
                insights.append("路径修复验证失败")
                result['next_action'] = 'abort_task'
        else:
            insights.append("路径修复失败")
            result['next_action'] = 'abort_task'
    
    else:
        insights.append("未知错误类型，无法执行自动修复")
        result['next_action'] = 'manual_intervention'
    
    # 添加知识三元组
    if result['repair_performed']:
        facts.append({
            'subject': 'self_healing_coordinator',
            'relation': 'performed_repair',
            'object': result['repair_type'],
            'source': 'error_handling'
        })
    
    return {
        'result': result,
        'insights': insights,
        'facts': facts
    }

# 导入动态错误向量化器（如果可用）
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from typing import List, Tuple
    
    class DynamicErrorVectorizerSingleton:
        """动态错误语义向量化单例类，避免重复初始化模型"""
        _instance = None
        _initialized = False
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super(DynamicErrorVectorizerSingleton, cls).__new__(cls)
            return cls._instance
        
        def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
            if not self._initialized:
                self.model = SentenceTransformer(model_name)
                self.error_type_vectors = {}
                self.similarity_threshold = 0.7
                self._initialized = True
                # 初始化已知错误类型
                self._initialize_error_types()
        
        def _initialize_error_types(self):
            """初始化已知错误类型及其示例"""
            self.add_error_type("dependency_missing", [
                "No module named", "ModuleNotFoundError", "command not found", 
                "ImportError", "failed to import", "dependency missing",
                "cannot import name", "No command found", "FileNotFoundError"
            ])
            self.add_error_type("parameter_error", [
                "missing required", "缺少必需", "invalid parameter", 
                "参数验证失败", "required field missing", "argument required",
                "缺少字段", "missing argument", "required parameter"
            ])
            self.add_error_type("path_error", [
                "file not found", "directory does not exist", "path does not exist",
                "文件不存在", "目录不存在", "路径无效", "no such file"
            ])
            
        def add_error_type(self, error_type: str, examples: List[str]):
            """添加新的错误类型及其示例消息"""
            if not examples:
                return
                
            # 计算该错误类型的平均向量
            vectors = self.model.encode(examples)
            avg_vector = np.mean(vectors, axis=0)
            self.error_type_vectors[error_type] = avg_vector
            
        def vectorize_error(self, error_message: str) -> np.ndarray:
            """将错误消息转换为向量"""
            return self.model.encode([error_message])[0]
            
        def classify_error(self, error_message: str) -> Tuple[str, float]:
            """分类错误消息，返回最匹配的错误类型和置信度"""
            if not self.error_type_vectors:
                return "unknown_error", 0.0
                
            error_vector = self.vectorize_error(error_message)
            best_match = "unknown_error"
            best_similarity = 0.0
            
            for error_type, type_vector in self.error_type_vectors.items():
                similarity = np.dot(error_vector, type_vector) / (
                    np.linalg.norm(error_vector) * np.linalg.norm(type_vector)
                )
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = error_type
                    
            if best_similarity < self.similarity_threshold:
                return "unknown_error", 0.0
                
            return best_match, best_similarity

    def enhanced_classify_error_with_semantics_local(error_info):
        """增强版错误分类函数，结合语义向量化（单例模式）"""
        # 首先处理不同类型的error_info输入
        if isinstance(error_info, dict):
            error_message = error_info.get('error_message', '')
        elif isinstance(error_info, str):
            error_message = error_info
        else:
            error_message = str(error_info)
        
        if not error_message.strip():
            return 'unknown_error'
        
        # 使用单例模式的向量化器进行分类
        vectorizer = DynamicErrorVectorizerSingleton()
        error_type, confidence = vectorizer.classify_error(error_message)
        return error_type

except ImportError:
    # 如果sentence-transformers不可用，定义一个空函数
    def enhanced_classify_error_with_semantics_local(error_info):
        return 'unknown_error'

def classify_error(error_info):
    """错误分类函数 - 增强语义向量化版"""
    print(f"DEBUG classify_error: error_info type = {type(error_info)}")
    print(f"DEBUG classify_error: error_info value = {error_info}")
    
    # 首先处理不同类型的error_info输入
    if isinstance(error_info, dict):
        error_message = error_info.get('error_message', '')
    elif isinstance(error_info, str):
        error_message = error_info
    else:
        error_message = str(error_info)
    
    if not error_message.strip():
        return 'unknown_error'
    
    # 尝试使用语义向量化进行分类
    try:
        semantic_result = enhanced_classify_error_with_semantics_local(error_message)
        if semantic_result != 'unknown_error':
            print(f"DEBUG: Semantic classification result: {semantic_result}")
            return semantic_result
        else:
            print("DEBUG: Semantic classification returned unknown_error, falling back to regex")
    except Exception as e:
        print(f"DEBUG: Semantic classification failed: {e}, falling back to regex")
    
    # 回退到原有的正则表达式分类逻辑
    print(f"DEBUG: Error message: {error_message}")
    print(f"DEBUG: Error message repr: {repr(error_message)}")
    
    # 检查是否是依赖缺失错误
    dependency_patterns = [
        r".*module.*not found.*",
        r".*command.*not found.*",
        r".*package.*not found.*",
        r".*No module named.*",
        r".*ImportError.*No module named.*",
        r".*ImportError:.*",
        r".*cannot import name.*",
        r".*dependency.*missing.*",
        r".*failed to import.*",
        r".*No command.*found.*",
        r".*FileNotFoundError.*",
        r".*FileNotFoundError:.*",
        r".*command not found.*",
        r".*ModuleNotFoundError.*",
        r".*no module named.*"
    ]
    
    for pattern in dependency_patterns:
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            print(f"DEBUG: Matched pattern '{pattern}' with error message")
            return 'dependency_missing'
    
    # 后备：直接字符串包含检查
    if "no module named" in error_message.lower() or "importerror" in error_message.lower():
        print("DEBUG: Matched via string contains check")
        return 'dependency_missing'
    
    # 检查是否是参数错误（包括中文错误信息）
    param_patterns = [
        r'argument.*required',
        r'argument.*expected',
        r'invalid.*argument',
        r'argument.*invalid',
        r'too few arguments',
        r'too many arguments',
        r'invalid value',
        r'invalid parameter',
        r'parameter.*error',
        r'args.*error',
        r'argparse',
        r'type.*error',
        r'.*value.*error.*',
        r'.*type.*error.*',
        r'invalid.*value',
        r'value.*invalid',
        r'wrong.*type',
        r'type.*mismatch',
        # 中文参数错误模式
        r'缺少.*字段',
        r'必需.*字段',
        r'无效.*参数',
        r'参数.*错误',
        r'类型.*错误',
        r'值.*无效',
        r'schema.*错误',
        r'格式.*错误',
        # 新增模式：直接匹配"缺少.*参数"和简单缺失模式
        r'缺少.*参数',
        r'missing.*parameter',
        r'missing.*arg',
        r'required.*missing',
        r'field.*required'
    ]
    
    print(f"DEBUG: Checking parameter patterns for error: {error_message}")
    for pattern in param_patterns:
        if re.search(pattern, error_message, re.IGNORECASE):
            print(f"DEBUG: Matched parameter pattern '{pattern}'")
            return 'parameter_error'
        else:
            print(f"DEBUG: Parameter pattern '{pattern}' did not match")
    
    # 检查是否是路径错误
    path_patterns = [
        r'directory.*not found',
        r'file.*not found',
        r'path.*invalid',
        r'path.*not exist',
        r'no such file',
        r'no such directory',
        r'directory does not exist',
        r'file does not exist',
        r'path error',
        r'invalid path',
        # 中文路径错误模式
        r'目录.*不存在',
        r'文件.*不存在',
        r'路径.*无效',
        r'路径.*不存在'
    ]
    
    for pattern in path_patterns:
        if re.search(pattern, error_message, re.IGNORECASE):
            return 'path_error'
    
    # 检查是否是权限错误
    permission_patterns = [
        r'permission denied',
        r'access denied',
        r'permission error',
        r'access error',
        # 中文权限错误模式
        r'权限.*拒绝',
        r'访问.*拒绝',
        r'权限.*错误',
        r'访问.*错误'
    ]
    
    for pattern in permission_patterns:
        if re.search(pattern, error_message, re.IGNORECASE):
            return 'permission_error'
    
    # 检查是否是网络错误
    network_patterns = [
        r'network error',
        r'connection error',
        r'connection refused',
        r'connection timeout',
        r'network unreachable',
        r'request failed',
        r'HTTP Error',
        r'URLError',
        # 中文网络错误模式
        r'网络.*错误',
        r'连接.*错误',
        r'连接.*拒绝',
        r'连接.*超时',
        r'网络.*不可达',
        r'请求.*失败'
    ]
    
    for pattern in network_patterns:
        if re.search(pattern, error_message, re.IGNORECASE):
            return 'network_error'
    
    return 'unknown_error'

def handle_dependency_missing(error_info):
    """处理依赖缺失错误"""
    error_message = error_info.get('error_message', '')
    
    # 提取缺失的模块/包名
    module_match = re.search(r"module ['\"]([^'\"]+)['\"] not found", error_message)
    if not module_match:
        module_match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_message)
    if not module_match:
        module_match = re.search(r"command ['\"]([^'\"]+)['\"] not found", error_message)
    
    if module_match:
        dependency = module_match.group(1)
        
        # 特殊处理ffmpeg依赖
        if dependency == 'ffmpeg':
            return handle_ffmpeg_installation()
        
        # 尝试安装依赖
        try:
            # 首先检查是否是系统命令
            if is_system_command(dependency):
                return {
                    'success': False,
                    'dependency': dependency,
                    'reason': 'system command not found, manual installation required'
                }
            
            # 尝试使用pip安装
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', dependency], 
                                  capture_output=True, text=True, timeout=60)

            
            if result.returncode == 0:
                return {
                    'success': True,
                    'dependency': dependency,
                    'install_output': result.stdout
                }
            else:
                # 如果pip安装失败，尝试conda安装
                try:
                    result = subprocess.run(['conda', 'install', '-y', dependency], 
                                          capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        return {
                            'success': True,
                            'dependency': dependency,
                            'install_output': result.stdout
                        }
                    else:
                        return {
                            'success': False,
                            'dependency': dependency,
                            'error': result.stderr
                        }
                except FileNotFoundError:
                    return {
                        'success': False,
                        'dependency': dependency,
                        'error': result.stderr
                    }
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'dependency': dependency,
                'reason': 'installation timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'dependency': dependency,
                'error': str(e)
            }
    
    return {
        'success': False,
        'dependency': 'unknown',
        'reason': 'could not extract dependency name'
    }

def handle_ffmpeg_installation():
    """专门处理ffmpeg安装"""
    try:
        # 检查是否已经安装了ffprobe（通常与ffmpeg一起安装）
        ffprobe_result = subprocess.run(['which', 'ffprobe'], 
                                      capture_output=True, text=True, timeout=10)
        
        if ffprobe_result.returncode == 0:
            # ffprobe已安装，尝试重新安装ffmpeg
            install_result = subprocess.run(['brew', 'reinstall', 'ffmpeg'], 
                                          capture_output=True, text=True, timeout=300)
        else:
            # 完全安装ffmpeg
            install_result = subprocess.run(['brew', 'install', 'ffmpeg'], 
                                          capture_output=True, text=True, timeout=300)
        
        if install_result.returncode == 0:
            return {
                'success': True,
                'dependency': 'ffmpeg',
                'install_output': install_result.stdout
            }
        else:
            return {
                'success': False,
                'dependency': 'ffmpeg',
                'error': install_result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'dependency': 'ffmpeg',
            'reason': 'installation timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'dependency': 'ffmpeg',
            'error': str(e)
        }

def is_system_command(command):
    """检查是否是系统命令"""
    try:
        result = subprocess.run(['which', command], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def handle_parameter_error(error_info, task_context):
    """处理参数错误"""
    error_message = error_info.get('error_message', '')
    original_params = task_context.get('params', {})
    
    # 分析错误信息，尝试修复参数
    corrected_params = {}
    
    # 检查是否是常见的参数错误类型
    if 'argument' in error_message and 'required' in error_message:
        # 检查是否有缺失的必需参数
        missing_param_match = re.search(r"the following arguments are required: (.+)", error_message)
        if missing_param_match:
            missing_params = missing_param_match.group(1).replace("'", "").split(', ')
            for param in missing_params:
                if param.startswith('--'):
                    # 尝试从上下文中获取默认值
                    param_name = param[2:]
                    if param_name in original_params:
                        corrected_params[param] = original_params[param_name]
                    else:
                        corrected_params[param] = get_default_value_for_param(param_name)
    
    # 如果没有自动修复参数，返回原始参数
    if not corrected_params:
        corrected_params = original_params
    
    return {
        'success': True,
        'corrected_params': corrected_params,
        'original_error': error_message
    }

def get_default_value_for_param(param_name):
    """获取参数的默认值"""
    defaults = {
        'output': './output',
        'input': './input',
        'verbose': False,
        'debug': False,
        'force': False,
        'timeout': 30,
        'retries': 3
    }
    
    return defaults.get(param_name, '')

def handle_path_error(error_info, task_context):
    """处理路径错误"""
    error_message = error_info.get('error_message', '')
    original_path = task_context.get('path', '')
    
    # 从错误信息中提取路径
    path_match = re.search(r"['\"]([^'\"]*[/\\][^'\"]*)['\"]", error_message)
    if not path_match:
        path_match = re.search(r"path ['\"]([^'\"]+)['\"]", error_message, re.IGNORECASE)
    
    if path_match:
        problematic_path = path_match.group(1)
    else:
        problematic_path = original_path
    
    if not problematic_path:
        return {
            'success': False,
            'reason': 'no path found in error message or context'
        }
    
    # 尝试创建路径目录
    path_obj = Path(problematic_path)
    
    # 如果是文件路径，创建其所在的目录
    if path_obj.is_file() or problematic_path.endswith('/'):
        parent_dir = path_obj.parent
    else:
        parent_dir = path_obj
    
    try:
        parent_dir.mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'corrected_path': str(parent_dir),
            'action': 'directory_created'
        }
    except PermissionError:
        return {
            'success': False,
            'corrected_path': problematic_path,
            'reason': 'permission denied to create directory'
        }
    except Exception as e:
        return {
            'success': False,
            'corrected_path': problematic_path,
            'error': str(e)
        }

def validate_dependency_installation(dependency):
    """验证依赖安装是否成功"""
    try:
        # 尝试导入模块
        result = subprocess.run([sys.executable, '-c', f'import {dependency}'], 
                              capture_output=True, text=True, timeout=10)

        
        if result.returncode == 0:
            return {
                'success': True,
                'dependency': dependency,
                'validation_output': result.stdout
            }
        else:
            # 如果是系统命令，检查命令是否存在
            result = subprocess.run(['which', dependency], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return {
                    'success': True,
                    'dependency': dependency,
                    'validation_output': 'System command exists'
                }
            else:
                return {
                    'success': False,
                    'dependency': dependency,
                    'error': result.stderr
                }
    except:
        return {
            'success': False,
            'dependency': dependency,
            'error': 'validation failed'
        }

def validate_parameters(params):
    """验证参数是否有效"""
    if not isinstance(params, dict):
        return {
            'success': False,
            'error': 'parameters are not in dictionary format'
        }
    
    # 基本参数验证
    for key, value in params.items():
        if key.startswith('--') and value is None:
            return {
                'success': False,
                'error': f'parameter {key} has None value'
            }
    
    return {
        'success': True,
        'validation_result': 'parameters are valid'
    }

def validate_path(path):
    """验证路径是否有效"""
    try:
        path_obj = Path(path)
        # 检查路径是否存在或其父目录是否存在
        if path_obj.exists():
            return {
                'success': True,
                'path': path,
                'validation_result': 'path exists'
            }
        elif path_obj.parent.exists():
            return {
                'success': True,
                'path': path,
                'validation_result': 'parent directory exists'
            }
        else:
            return {
                'success': False,
                'path': path,
                'error': 'path does not exist and parent directory does not exist'
            }
    except Exception as e:
        return {
            'success': False,
            'path': path,
            'error': str(e)
        }

def validate_file_output(target_dir, expected_count, file_pattern="*"):
    """验证指定目录下是否存在符合预期数量和命名模式的文件"""
    try:
        target_path = Path(target_dir)
        if not target_path.exists() or not target_path.is_dir():
            return {
                'success': False,
                'target_dir': str(target_path),
                'expected_count': expected_count,
                'actual_count': 0,
                'error': '目标目录不存在或不是目录'
            }
        
        # 获取匹配的文件列表
        files = list(target_path.glob(file_pattern))
        actual_count = len(files)
        
        success = (actual_count == expected_count)
        
        return {
            'success': success,
            'target_dir': str(target_path),
            'expected_count': expected_count,
            'actual_count': actual_count,
            'file_pattern': file_pattern,
            'matched_files': [str(f) for f in files],
            'validation_result': '文件产出验证成功' if success else f'期望 {expected_count} 个文件，实际找到 {actual_count} 个'
        }
    except Exception as e:
        return {
            'success': False,
            'target_dir': target_dir,
            'expected_count': expected_count,
            'actual_count': 0,
            'error': str(e)
        }