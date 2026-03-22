# tool_name: cross_tool_structure_repair

from typing import Dict, Any, List, Optional, Union
from langchain.tools import tool
import json
import os
import sys
import traceback
from datetime import datetime

def invoke_tool(tool_name: str, input_args: str) -> Dict[str, Any]:
    """运行时工具调用接口"""
    import importlib
    import sys
    import os
    
    # 确保 workspace 目录在 Python 路径中
    current_dir = os.path.dirname(__file__)
    workspace_dir = os.path.join(current_dir, '..')
    if workspace_dir not in sys.path:
        sys.path.insert(0, workspace_dir)
    
    try:
        # 尝试从 tools 目录导入
        tool_module = importlib.import_module(f"tools.tool_{tool_name}")
        tool_func = getattr(tool_module, tool_name)
        return tool_func(input_args)
    except Exception as e:
        # 如果失败，尝试直接导入（兼容旧格式）
        try:
            tool_module = importlib.import_module(f"tool_{tool_name}")
            tool_func = getattr(tool_module, tool_name)
            return tool_func(input_args)
        except Exception as e2:
            return {"error": f"Primary import error: {str(e)}, Fallback import error: {str(e2)}", "success": False}

def detect_structure_incompatibility(original_result: Dict[str, Any], expected_structure: Dict[str, Any]) -> Dict[str, Any]:
    """检测结果结构不兼容性"""
    issues = {
        'missing_keys': [],
        'extra_keys': [],
        'type_mismatches': [],
        'nested_structure_issues': []
    }
    
    def compare_structures(orig, expected, path=""):
        if isinstance(expected, dict) and isinstance(orig, dict):
            # 检查缺失的键
            for key in expected:
                if key not in orig:
                    issues['missing_keys'].append(f"{path}.{key}" if path else key)
                else:
                    compare_structures(orig[key], expected[key], f"{path}.{key}" if path else key)
            
            # 检查多余的键
            for key in orig:
                if key not in expected:
                    issues['extra_keys'].append(f"{path}.{key}" if path else key)
                    
        elif isinstance(expected, list) and isinstance(orig, list):
            if len(expected) > 0 and len(orig) > 0:
                compare_structures(orig[0], expected[0], path)
        elif type(expected) != type(orig):
            issues['type_mismatches'].append({
                'path': path,
                'expected_type': type(expected).__name__,
                'actual_type': type(orig).__name__,
                'expected_value': str(expected)[:100],
                'actual_value': str(orig)[:100]
            })
    
    compare_structures(original_result, expected_structure)
    return issues

def auto_repair_structure(original_result: Dict[str, Any], expected_structure: Dict[str, Any], issues: Dict[str, Any]) -> Dict[str, Any]:
    """自动修复结果结构"""
    repaired_result = original_result.copy()
    
    # 修复缺失的键
    def add_missing_keys(result_dict, expected_dict, current_path=""):
        if isinstance(expected_dict, dict) and isinstance(result_dict, dict):
            for key, expected_value in expected_dict.items():
                full_path = f"{current_path}.{key}" if current_path else key
                
                if key not in result_dict:
                    # 添加缺失的键，使用默认值
                    if isinstance(expected_value, dict):
                        result_dict[key] = {}
                        add_missing_keys(result_dict[key], expected_value, full_path)
                    elif isinstance(expected_value, list):
                        result_dict[key] = []
                    elif expected_value is None:
                        result_dict[key] = None
                    elif isinstance(expected_value, (str, int, float, bool)):
                        result_dict[key] = expected_value
                    else:
                        result_dict[key] = str(expected_value)
                elif isinstance(expected_value, dict) and isinstance(result_dict.get(key), dict):
                    add_missing_keys(result_dict[key], expected_value, full_path)
    
    add_missing_keys(repaired_result, expected_structure)
    
    # 修复类型不匹配
    for mismatch in issues['type_mismatches']:
        path_parts = mismatch['path'].split('.') if mismatch['path'] else []
        current = repaired_result
        
        # 导航到问题位置
        for part in path_parts[:-1]:
            if part in current and isinstance(current[part], dict):
                current = current[part]
            else:
                break
        else:
            last_part = path_parts[-1] if path_parts else ""
            if last_part in current:
                expected_type = mismatch['expected_type']
                actual_value = current[last_part]
                
                # 尝试类型转换
                try:
                    if expected_type == 'str':
                        current[last_part] = str(actual_value)
                    elif expected_type == 'int':
                        current[last_part] = int(float(str(actual_value))) if str(actual_value).replace('.', '').replace('-', '').isdigit() else 0
                    elif expected_type == 'float':
                        current[last_part] = float(str(actual_value)) if str(actual_value).replace('.', '').replace('-', '').isdigit() else 0.0
                    elif expected_type == 'bool':
                        current[last_part] = bool(actual_value)
                    elif expected_type == 'dict':
                        current[last_part] = {} if not isinstance(actual_value, dict) else actual_value
                    elif expected_type == 'list':
                        current[last_part] = [] if not isinstance(actual_value, list) else actual_value
                except (ValueError, TypeError):
                    # 如果转换失败，使用默认值
                    if expected_type == 'str':
                        current[last_part] = ""
                    elif expected_type == 'int':
                        current[last_part] = 0
                    elif expected_type == 'float':
                        current[last_part] = 0.0
                    elif expected_type == 'bool':
                        current[last_part] = False
                    elif expected_type == 'dict':
                        current[last_part] = {}
                    elif expected_type == 'list':
                        current[last_part] = []
    
    return repaired_result

def validate_repaired_structure(repaired_result: Dict[str, Any], expected_structure: Dict[str, Any]) -> bool:
    """验证修复后的结构是否符合预期"""
    issues = detect_structure_incompatibility(repaired_result, expected_structure)
    return len(issues['missing_keys']) == 0 and len(issues['type_mismatches']) == 0

@tool
def cross_tool_structure_repair(input_args: str) -> Dict[str, Any]:
    """
    跨工具结果结构兼容性自动修复工具
    
    这个工具专门用于检测和自动修复跨工具调用中结果结构不兼容的问题。
    它能够：
    1. 检测结果结构中的不兼容性（缺失键、多余键、类型不匹配等）
    2. 自动修复结构问题，确保结果符合预期格式
    3. 验证修复后的结果结构完整性
    4. 提供详细的修复报告和见解
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - original_result: 原始工具返回的结果（字典格式）
            - expected_structure: 期望的结果结构（字典格式，包含示例值）
            - source_tool: 源工具名称
            - target_tool: 目标工具名称
            - context: 当前执行上下文
            
    Returns:
        dict: 包含修复结果的字典，包括成功状态、修复后的结果、详细报告、见解、事实和记忆
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
            
        original_result = params.get('original_result', {})
        expected_structure = params.get('expected_structure', {})
        source_tool = params.get('source_tool', 'unknown_source')
        target_tool = params.get('target_tool', 'unknown_target')
        context = params.get('context', 'cross_tool_structure_repair')
        
        results = {
            'success': False,
            'repaired_result': {},
            'repair_applied': False,
            'detailed_report': {},
            'insights': [],
            'facts': [],
            'memories': []
        }
        
        # 检测结构不兼容性
        structure_issues = detect_structure_incompatibility(original_result, expected_structure)
        results['detailed_report']['detected_issues'] = structure_issues
        
        # 检查是否需要修复
        needs_repair = (
            len(structure_issues['missing_keys']) > 0 or 
            len(structure_issues['type_mismatches']) > 0
        )
        
        if needs_repair:
            results['insights'].append(f"检测到跨工具结果结构不兼容问题：{len(structure_issues['missing_keys'])}个缺失键，{len(structure_issues['type_mismatches'])}个类型不匹配")
            
            # 执行自动修复
            repaired_result = auto_repair_structure(original_result, expected_structure, structure_issues)
            results['repaired_result'] = repaired_result
            results['repair_applied'] = True
            
            # 验证修复结果
            repair_successful = validate_repaired_structure(repaired_result, expected_structure)
            results['success'] = repair_successful
            
            if repair_successful:
                results['insights'].append("跨工具结果结构自动修复成功！所有结构问题已解决")
            else:
                results['insights'].append("跨工具结果结构自动修复部分成功，仍有未解决的问题")
                
        else:
            # 结构已经兼容，无需修复
            results['repaired_result'] = original_result
            results['success'] = True
            results['insights'].append("跨工具结果结构兼容性验证通过，无需修复")
        
        # 生成详细报告
        results['detailed_report']['source_tool'] = source_tool
        results['detailed_report']['target_tool'] = target_tool
        results['detailed_report']['context'] = context
        results['detailed_report']['repair_summary'] = {
            'missing_keys_fixed': len(structure_issues['missing_keys']),
            'type_mismatches_fixed': len(structure_issues['type_mismatches']),
            'extra_keys_preserved': len(structure_issues['extra_keys']),
            'repair_successful': results['success']
        }
        
        # 记录事实和记忆
        results['facts'].append(f"跨工具结果结构兼容性自动修复完成：源工具={source_tool}, 目标工具={target_tool}, 修复状态={'成功' if results['success'] else '失败'}")
        
        results['memories'].append({
            'content': f"跨工具结果结构兼容性自动修复结果：{'成功' if results['success'] else '失败'}",
            'context': context,
            'source_tool': source_tool,
            'target_tool': target_tool,
            'timestamp': datetime.now().isoformat(),
            'repair_applied': results['repair_applied']
        })
        
        return results
        
    except Exception as e:
        error_str = f"跨工具结果结构兼容性自动修复失败: {str(e)}"
        return {
            'success': False,
            'error': error_str,
            'repaired_result': {},
            'repair_applied': False,
            'detailed_report': {'error': str(e), 'traceback': traceback.format_exc()},
            'insights': [error_str],
            'facts': [],
            'memories': []
        }