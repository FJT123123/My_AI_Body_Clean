# tool_name: interaction_weighting_capability_defense_layer

from typing import Dict, Any, Optional, Union
from langchain.tools import tool
import json
import os
import sys
import traceback
import re
from datetime import datetime

@tool
def interaction_weighting_capability_defense_layer(input_args: str) -> Dict[str, Any]:
    """
    ToolInteractionWeightingCapability的异常参数防御层与调试信息逃逸检测机制
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'validate_input', 'detect_debug_escape', 'apply_defense_layer', 'test_boundary_conditions', 'validate_output'
            - input_data (Union[dict, str], required): 要验证的输入数据或输出数据
            - tool_name (str, optional): 目标工具名称
            - context (str, optional): 当前上下文
            
    Returns:
        dict: 包含防御层处理结果的字典
    """
    try:
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 安全解析输入参数
        parsed_input = _safe_parse_input(input_args)
        if isinstance(parsed_input, dict) and 'error' in parsed_input:
            return parsed_input
        
        action = parsed_input.get('action')
        input_data = parsed_input.get('input_data')
        tool_name = parsed_input.get('tool_name')
        context = parsed_input.get('context', '')
        
        if not action or input_data is None:
            return {
                'result': {'error': '缺少必需参数: action 和 input_data'},
                'insights': ['参数校验失败：必须提供action和input_data'],
                'facts': [],
                'memories': []
            }
        
        # 执行不同的防御操作
        if action == 'validate_input':
            result = _validate_input_parameters(input_data, tool_name)
        elif action == 'detect_debug_escape':
            result = _detect_debug_information_escape(input_data)
        elif action == 'apply_defense_layer':
            result = _apply_comprehensive_defense_layer(input_data, tool_name, context)
        elif action == 'test_boundary_conditions':
            result = _test_boundary_conditions(input_data)
        elif action == 'validate_output':
            result = _validate_output_structure(input_data)
        else:
            return {
                'result': {'error': f'不支持的动作: {action}'},
                'insights': ['支持的动作: validate_input, detect_debug_escape, apply_defense_layer, test_boundary_conditions, validate_output'],
                'facts': [],
                'memories': []
            }
        
        return {
            'result': result,
            'insights': [f'成功执行防御层操作: {action}'],
            'facts': [],
            'memories': []
        }
        
    except Exception as e:
        error_str = f'防御层执行失败: {str(e)}'
        traceback_str = traceback.format_exc()
        # 确保不泄露敏感调试信息
        sanitized_error = _sanitize_error_message(str(e))
        return {
            'result': {'error': sanitized_error},
            'insights': [f'防御层异常: {sanitized_error}'],
            'facts': [],
            'memories': []
        }

def _safe_parse_input(input_args: Union[str, dict]) -> Union[dict, Dict[str, Any]]:
    """安全解析输入参数，防止JSON注入和其他攻击"""
    try:
        if isinstance(input_args, str):
            # 检查输入长度限制
            if len(input_args) > 100000:  # 100KB限制
                return {
                    'result': {'error': '输入数据过大，超过100KB限制'},
                    'insights': ['安全防护：输入数据大小限制触发'],
                    'facts': [],
                    'memories': []
                }
            
            # 检查潜在的危险字符模式
            dangerous_patterns = [
                r'__.*__',  # 双下划线属性
                r'\.py[cod]$',  # Python编译文件
                r'exec\(',  # exec函数调用
                r'eval\(',  # eval函数调用
                r'os\.',  # os模块调用
                r'sys\.',  # sys模块调用
                r'import ',  # import语句
                r'delattr',  # 删除属性
                r'setattr',  # 设置属性
                r'globals\(\)',  # 全局变量访问
                r'locals\(\)',  # 局部变量访问
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, input_args, re.IGNORECASE):
                    return {
                        'result': {'error': '检测到潜在的危险输入模式'},
                        'insights': ['安全防护：危险输入模式检测触发'],
                        'facts': [],
                        'memories': []
                    }
            
            # 安全解析JSON
            params = json.loads(input_args)
        else:
            params = input_args
        
        # 验证参数结构
        if not isinstance(params, dict):
            return {
                'result': {'error': '输入参数必须是字典或JSON字符串'},
                'insights': ['参数校验失败：输入不是有效的字典结构'],
                'facts': [],
                'memories': []
            }
        
        return params
        
    except json.JSONDecodeError as e:
        return {
            'result': {'error': '输入参数必须是有效的JSON字符串'},
            'insights': ['参数解析失败：输入不是有效的JSON'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        sanitized_error = _sanitize_error_message(str(e))
        return {
            'result': {'error': f'输入解析失败: {sanitized_error}'},
            'insights': ['输入解析异常'],
            'facts': [],
            'memories': []
        }

def _sanitize_error_message(error_msg: str) -> str:
    """清理错误消息，防止敏感信息泄露"""
    # 移除文件路径、行号等敏感信息
    sanitized = re.sub(r'/[^ ]*?/workspace/', '/workspace/', error_msg)
    sanitized = re.sub(r'File ".*?", line \d+', 'File "<redacted>", line <redacted>', sanitized)
    sanitized = re.sub(r'Traceback \(most recent call last\):.*', '', sanitized, flags=re.DOTALL)
    
    # 限制错误消息长度
    if len(sanitized) > 500:
        sanitized = sanitized[:497] + "..."

    return sanitized.strip()

def _validate_input_parameters(input_data: Union[dict, str], tool_name: Optional[str] = None) -> Dict[str, Any]:
    """验证输入参数的安全性和有效性"""
    validation_result = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'sanitized_data': None,
        'confidence_score': 1.0
    }
    
    # 处理字符串输入
    if isinstance(input_data, str):
        if len(input_data) > 50000:  # 50KB字符串限制
            validation_result['valid'] = False
            validation_result['errors'].append('字符串输入过大，超过50KB限制')
            validation_result['confidence_score'] = 0.0
            return validation_result
        
        # 检查字符串内容
        if _contains_suspicious_content(input_data):
            validation_result['valid'] = False
            validation_result['errors'].append('检测到可疑内容')
            validation_result['confidence_score'] = 0.0
            return validation_result
        
        validation_result['sanitized_data'] = input_data
        return validation_result
    
    # 处理字典输入
    if not isinstance(input_data, dict):
        validation_result['valid'] = False
        validation_result['errors'].append('输入数据必须是字典或字符串')
        validation_result['confidence_score'] = 0.0
        return validation_result
    
    # 检查字典深度和大小
    if _get_dict_depth(input_data) > 10:
        validation_result['valid'] = False
        validation_result['errors'].append('输入数据嵌套过深，超过10层限制')
        validation_result['confidence_score'] = 0.0
        return validation_result
    
    if _get_dict_size(input_data) > 1000:
        validation_result['valid'] = False
        validation_result['errors'].append('输入数据项过多，超过1000项限制')
        validation_result['confidence_score'] = 0.0
        return validation_result
    
    # 递归验证每个字段
    sanitized_data = {}
    for key, value in input_data.items():
        # 验证键名
        if not isinstance(key, str):
            validation_result['valid'] = False
            validation_result['errors'].append(f'键名必须是字符串，发现类型: {type(key).__name__}')
            continue
        
        if len(key) > 100:
            validation_result['valid'] = False
            validation_result['errors'].append(f'键名过长: {key[:20]}...')
            continue
        
        # 检查键名是否包含危险字符
        if re.search(r'[<>{}[\]|;]', key):
            validation_result['valid'] = False
            validation_result['errors'].append(f'键名包含危险字符: {key}')
            continue
        
        # 验证值
        field_validation = _validate_field_value(value, key)
        if not field_validation['valid']:
            validation_result['valid'] = False
            validation_result['errors'].extend(field_validation['errors'])
        else:
            sanitized_data[key] = field_validation['sanitized_value']
    
    validation_result['sanitized_data'] = sanitized_data
    
    if validation_result['errors']:
        validation_result['confidence_score'] = max(0.0, 1.0 - len(validation_result['errors']) * 0.2)
    
    return validation_result

def _validate_field_value(value: Any, field_name: str) -> Dict[str, Any]:
    """验证单个字段值"""
    result = {
        'valid': True,
        'errors': [],
        'sanitized_value': value
    }
    
    if value is None:
        return result
    
    if isinstance(value, str):
        if len(value) > 10000:  # 单个字符串10KB限制
            result['valid'] = False
            result['errors'].append(f'字段 {field_name} 值过大，超过10KB限制')
            return result
        
        if _contains_suspicious_content(value):
            result['valid'] = False
            result['errors'].append(f'字段 {field_name} 包含可疑内容')
            return result
        
    elif isinstance(value, (int, float)):
        if abs(value) > 1e15:  # 数值范围限制
            result['valid'] = False
            result['errors'].append(f'字段 {field_name} 数值过大')
            return result
    
    elif isinstance(value, list):
        if len(value) > 1000:  # 列表长度限制
            result['valid'] = False
            result['errors'].append(f'字段 {field_name} 列表过长，超过1000项')
            return result
        
        # 递归验证列表元素
        sanitized_list = []
        for i, item in enumerate(value):
            item_validation = _validate_field_value(item, f"{field_name}[{i}]")
            if not item_validation['valid']:
                result['valid'] = False
                result['errors'].extend(item_validation['errors'])
            else:
                sanitized_list.append(item_validation['sanitized_value'])
        result['sanitized_value'] = sanitized_list
    
    elif isinstance(value, dict):
        # 递归验证字典
        dict_validation = _validate_input_parameters(value)
        if not dict_validation['valid']:
            result['valid'] = False
            result['errors'].extend([f'字段 {field_name}: {err}' for err in dict_validation['errors']])
        else:
            result['sanitized_value'] = dict_validation['sanitized_data']
    
    return result

def _contains_suspicious_content(text: str) -> bool:
    """检查文本是否包含可疑内容"""
    suspicious_patterns = [
        r'{{.*?}}',  # Jinja2模板
        r'<%.*?%>',  # ASP模板
        r'\$\{.*?\}',  # Shell变量
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',  # SQL关键字
        r'\b(UNION|SELECT)\s+.*\b(FROM|WHERE)\b',  # SQL注入模式
        r'javascript:',  # JavaScript协议
        r'data:',  # Data协议
        r'vbscript:',  # VBScript协议
        r'on\w+\s*=',
        r'<script',
        r'</script>',
        r'<iframe',
        r'</iframe>',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'os\.system',
        r'subprocess\.call',
        r'popen',
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def _get_dict_depth(d: dict, current_depth: int = 0) -> int:
    """计算字典的嵌套深度"""
    if current_depth > 20:  # 防止无限递归
        return current_depth
    
    max_depth = current_depth
    for value in d.values():
        if isinstance(value, dict):
            depth = _get_dict_depth(value, current_depth + 1)
            max_depth = max(max_depth, depth)
    
    return max_depth

def _get_dict_size(d: dict) -> int:
    """计算字典的总项数"""
    size = len(d)
    for value in d.values():
        if isinstance(value, dict):
            size += _get_dict_size(value)
        elif isinstance(value, list):
            size += len(value)
            for item in value:
                if isinstance(item, dict):
                    size += _get_dict_size(item)
    
    return min(size, 10000)  # 限制最大计算量

def _detect_debug_information_escape(input_data: Union[dict, str]) -> Dict[str, Any]:
    """检测调试信息逃逸"""
    detection_result = {
        'debug_info_detected': False,
        'sensitive_patterns': [],
        'risk_level': 'low',
        'recommendations': []
    }
    
    # 转换为字符串进行分析
    if isinstance(input_data, dict):
        text_to_analyze = json.dumps(input_data, indent=2, default=str)
    else:
        text_to_analyze = str(input_data)
    
    # 检测敏感信息模式
    sensitive_patterns = {
        'file_paths': r'/[a-zA-Z0-9_/.-]+\.py:\d+',
        'tracebacks': r'Traceback \(most recent call last\)',
        'memory_addresses': r'0x[0-9a-fA-F]{8,}',
        'environment_variables': r'\$\{?[A-Z_][A-Z0-9_]*\}?',
        'api_keys': r'(?:api[_-]?key|token|secret)["\']?\s*[:=]\s*["\'][a-zA-Z0-9+/=]{20,}',
        'passwords': r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\'][^"\']{8,}',
        'internal_ips': r'192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+',
        'localhost': r'localhost|127\.0\.0\.1',
        'database_urls': r'dburl|database_url|mongodb://|postgresql://|mysql://',
    }
    
    detected_patterns = []
    for pattern_name, pattern in sensitive_patterns.items():
        if re.search(pattern, text_to_analyze, re.IGNORECASE):
            detected_patterns.append(pattern_name)
    
    if detected_patterns:
        detection_result['debug_info_detected'] = True
        detection_result['sensitive_patterns'] = detected_patterns
        detection_result['risk_level'] = 'high' if any(p in ['api_keys', 'passwords'] for p in detected_patterns) else 'medium'
        detection_result['recommendations'] = [
            '清理输入数据中的敏感信息',
            '使用参数化查询代替直接字符串拼接',
            '实施输入数据白名单验证'
        ]
    
    return detection_result

def _apply_comprehensive_defense_layer(input_data: Union[dict, str], tool_name: Optional[str] = None, context: str = '') -> Dict[str, Any]:
    """应用综合防御层"""
    # 第一步：输入验证
    validation_result = _validate_input_parameters(input_data, tool_name)
    if not validation_result['valid']:
        return {
            'defense_applied': True,
            'blocked': True,
            'reason': '输入验证失败',
            'validation_errors': validation_result['errors'],
            'confidence_score': 0.0
        }
    
    # 第二步：调试信息检测
    debug_detection = _detect_debug_information_escape(validation_result['sanitized_data'])
    if debug_detection['debug_info_detected']:
        return {
            'defense_applied': True,
            'blocked': True,
            'reason': '检测到调试信息逃逸',
            'sensitive_patterns': debug_detection['sensitive_patterns'],
            'risk_level': debug_detection['risk_level'],
            'confidence_score': 0.0
        }
    
    # 第三步：上下文感知的额外验证
    context_validation = _apply_context_aware_validation(validation_result['sanitized_data'], tool_name, context)
    if not context_validation['valid']:
        return {
            'defense_applied': True,
            'blocked': True,
            'reason': '上下文感知验证失败',
            'context_errors': context_validation['errors'],
            'confidence_score': context_validation['confidence_score']
        }
    
    # 第四步：应用认知权重增强（如果适用）
    enhanced_data = validation_result['sanitized_data']
    if tool_name and context:
        try:
            from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
            dynamic_weighting = DynamicMemoryWeightingCapability()
            weighted_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                context,
                context=context,
                apply_weighting=True
            )
            
            if isinstance(enhanced_data, dict):
                enhanced_data['_weighted_context'] = {
                    'memories': weighted_memories[:5],
                    'context': context,
                    'tool_name': tool_name
                }
        except Exception:
            # 如果认知权重模块不可用，继续使用原始数据
            pass
    
    return {
        'defense_applied': True,
        'blocked': False,
        'enhanced_data': enhanced_data,
        'confidence_score': validation_result['confidence_score'],
        'security_level': 'high'
    }

def _apply_context_aware_validation(input_data: Union[dict, str], tool_name: Optional[str], context: str) -> Dict[str, Any]:
    """应用上下文感知的验证"""
    result = {
        'valid': True,
        'errors': [],
        'confidence_score': 1.0
    }
    
    if not tool_name:
        return result
    
    # 工具特定的验证规则
    tool_specific_rules = {
        'run_skill': {
            'required_fields': ['skill_name'],
            'max_string_length': 100,
            'allowed_skill_names': None  # 动态获取
        },
        'read_workspace_file': {
            'required_fields': ['filename'],
            'max_string_length': 200,
            'disallowed_patterns': [r'\.\.', r'/etc', r'/root', r'~']
        },
        'write_workspace_file': {
            'required_fields': ['filename', 'content'],
            'max_string_length': 200,
            'max_content_length': 100000,
            'disallowed_patterns': [r'\.\.', r'/etc', r'/root', r'~']
        }
    }
    
    if tool_name in tool_specific_rules:
        rules = tool_specific_rules[tool_name]
        
        if isinstance(input_data, dict):
            # 检查必需字段
            for required_field in rules.get('required_fields', []):
                if required_field not in input_data or not input_data[required_field]:
                    result['valid'] = False
                    result['errors'].append(f'缺少必需字段: {required_field}')
            
            # 检查字符串长度
            max_length = rules.get('max_string_length')
            if max_length:
                for key, value in input_data.items():
                    if isinstance(value, str) and len(value) > max_length:
                        result['valid'] = False
                        result['errors'].append(f'字段 {key} 超过最大长度 {max_length}')
            
            # 检查内容长度
            max_content_length = rules.get('max_content_length')
            if max_content_length and 'content' in input_data:
                content = input_data['content']
                if isinstance(content, str) and len(content) > max_content_length:
                    result['valid'] = False
                    result['errors'].append(f'内容超过最大长度 {max_content_length}')
            
            # 检查不允许的模式
            disallowed_patterns = rules.get('disallowed_patterns', [])
            for key, value in input_data.items():
                if isinstance(value, str):
                    for pattern in disallowed_patterns:
                        if re.search(pattern, value):
                            result['valid'] = False
                            result['errors'].append(f'字段 {key} 包含不允许的模式: {pattern}')
    
    if result['errors']:
        result['confidence_score'] = max(0.0, 1.0 - len(result['errors']) * 0.3)
    
    return result

def _test_boundary_conditions(test_config: dict) -> Dict[str, Any]:
    """测试边界条件"""
    test_results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'test_details': []
    }
    
    # 默认测试配置
    default_tests = [
        {'name': 'empty_input', 'input': {}},
        {'name': 'null_input', 'input': None},
        {'name': 'large_string', 'input': {'test': 'x' * 60000}},  # 超过限制
        {'name': 'deep_nesting', 'input': _create_deep_nested_dict(15)},  # 超过深度限制
        {'name': 'suspicious_content', 'input': {'test': 'SELECT * FROM users'}},
        {'name': 'normal_input', 'input': {'test': 'normal data'}},
        # 输出验证测试用例
        {'name': 'valid_output_structure', 'input': {'result': {'data': 'test'}, 'insights': [], 'facts': [], 'memories': []}, 'expected_to_fail': False, 'is_output_test': True},
        {'name': 'missing_result_field', 'input': {'insights': [], 'facts': [], 'memories': []}, 'expected_to_fail': True, 'is_output_test': True},
        {'name': 'invalid_insights_type', 'input': {'result': {'data': 'test'}, 'insights': 'not a list', 'facts': [], 'memories': []}, 'expected_to_fail': True, 'is_output_test': True},
        {'name': 'output_redirection_attempt', 'input': {'result': 'redirect to http://malicious.com', 'insights': [], 'facts': [], 'memories': []}, 'expected_to_fail': True, 'is_output_test': True},
    ]
    
    tests_to_run = test_config.get('custom_tests', default_tests)
    
    for test_case in tests_to_run:
        test_results['tests_run'] += 1
        try:
            # 检查是否是输出验证测试
            if test_case.get('is_output_test', False):
                # 测试输出验证
                validation_result = _validate_output_structure(test_case['input'])
                expected_to_fail = test_case.get('expected_to_fail', False)
                
                if expected_to_fail and not validation_result['valid']:
                    test_results['tests_passed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'passed',
                        'message': '正确拒绝了无效输出结构'
                    })
                elif not expected_to_fail and validation_result['valid']:
                    test_results['tests_passed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'passed',
                        'message': '正确接受了有效输出结构'
                    })
                else:
                    test_results['tests_failed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'failed',
                        'message': f'意外结果: valid={validation_result["valid"]}, expected_to_fail={expected_to_fail}'
                    })
            else:
                # 测试输入验证
                validation_result = _validate_input_parameters(test_case['input'])
                expected_to_fail = test_case.get('expected_to_fail', False)
                
                if expected_to_fail and not validation_result['valid']:
                    test_results['tests_passed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'passed',
                        'message': '正确拒绝了无效输入'
                    })
                elif not expected_to_fail and validation_result['valid']:
                    test_results['tests_passed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'passed',
                        'message': '正确接受了有效输入'
                    })
                else:
                    test_results['tests_failed'] += 1
                    test_results['test_details'].append({
                        'name': test_case['name'],
                        'status': 'failed',
                        'message': f'意外结果: valid={validation_result["valid"]}, expected_to_fail={expected_to_fail}'
                    })
                    
        except Exception as e:
            test_results['tests_failed'] += 1
            test_results['test_details'].append({
                'name': test_case['name'],
                'status': 'failed',
                'message': f'测试异常: {str(e)}'
            })
    
    test_results['success_rate'] = test_results['tests_passed'] / test_results['tests_run'] if test_results['tests_run'] > 0 else 0
    
    return test_results

def _create_deep_nested_dict(depth: int) -> dict:
    """创建深度嵌套的字典用于测试"""
    if depth <= 0:
        return {'leaf': 'value'}
    
    return {'level': _create_deep_nested_dict(depth - 1)}

def _validate_output_structure(output_data: Dict[str, Any]) -> Dict[str, Any]:
    """验证工具输出的结构完整性"""
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'confidence_score': 1.0
    }
    
    # 检查必需字段
    required_fields = ['result', 'insights', 'facts', 'memories']
    for field in required_fields:
        if field not in output_data:
            validation_result['valid'] = False
            validation_result['errors'].append(f'缺少必需字段: {field}')
    
    # 验证字段类型
    if 'result' in output_data:
        if not isinstance(output_data['result'], (str, dict, list, type(None))):
            validation_result['valid'] = False
            validation_result['errors'].append('result字段必须是字符串、字典、列表或None')
    
    for field in ['insights', 'facts', 'memories']:
        if field in output_data:
            if not isinstance(output_data[field], list):
                validation_result['valid'] = False
                validation_result['errors'].append(f'{field}字段必须是列表')
            else:
                # 检查列表内容
                for i, item in enumerate(output_data[field]):
                    if not isinstance(item, (str, dict)):
                        validation_result['warnings'].append(f'{field}[{i}]包含非字符串/字典类型')
                    elif isinstance(item, str) and len(item) > 1000:
                        validation_result['warnings'].append(f'{field}[{i}]字符串过长')
    
    # 检测输出重定向尝试
    redirection_detected = _detect_output_redirection(output_data)
    if redirection_detected:
        validation_result['valid'] = False
        validation_result['errors'].append('检测到潜在的输出重定向尝试')
    
    # 计算置信度分数
    if validation_result['errors']:
        validation_result['confidence_score'] = max(0.0, 1.0 - len(validation_result['errors']) * 0.5)
    elif validation_result['warnings']:
        validation_result['confidence_score'] = max(0.5, 1.0 - len(validation_result['warnings']) * 0.1)
    
    return validation_result

def _detect_output_redirection(output_data: Dict[str, Any]) -> bool:
    """检测潜在的输出重定向尝试"""
    if 'result' not in output_data:
        return False
    
    result_value = output_data['result']
    
    # 如果result是字符串，检查可疑内容
    if isinstance(result_value, str):
        suspicious_patterns = [
            r'http[s]?://',  # URL
            r'redirect',     # 重定向关键词
            r'forward',      # 转发关键词
            r'execute',      # 执行关键词
            r'run\s+',       # 运行命令
            r'command',      # 命令关键词
            r'shell',        # shell关键词
            r'system',       # 系统关键词
            r'exec\s*\(',    # exec函数调用
            r'eval\s*\(',    # eval函数调用
            r'import\s+',    # import语句
            r'/[a-zA-Z]',    # 绝对路径
            r'\.\./',        # 相对路径遍历
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, result_value, re.IGNORECASE):
                return True
    
    # 如果result是字典，递归检查
    elif isinstance(result_value, dict):
        for key, value in result_value.items():
            if isinstance(value, str):
                for pattern in [r'http[s]?://', r'redirect', r'execute', r'/[a-zA-Z]', r'\.\./']:
                    if re.search(pattern, value, re.IGNORECASE):
                        return True
    
    return False