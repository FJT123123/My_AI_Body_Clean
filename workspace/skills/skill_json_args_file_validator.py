"""
自动生成的技能模块
需求: 直接解析args参数作为JSON字符串的文件检查技能
生成时间: 2026-03-21 13:32:44
"""

# skill_name: json_args_file_validator

import json
import os
from typing import Dict, Any, List

def main(args=None) -> Dict[str, Any]:
    """
    解析args参数作为JSON字符串并验证文件存在性
    
    该技能接收包含JSON字符串的args参数，解析其中的文件路径信息，
    并验证这些文件在系统中的存在性，返回验证结果和相关洞察。
    
    Args:
        args: 包含JSON字符串的参数字典，可能包含文件路径信息
        
    Returns:
        Dict[str, Any]: 包含验证结果、文件存在性状态、洞察和建议的结构化数据
    """
    if args is None:
        args = {}
    
    result = {
        'parsed_data': None,
        'file_checks': {},
        'valid_files': [],
        'missing_files': [],
        'error': None
    }
    
    insights = []
    facts = []
    
    try:
        # 尝试将args解析为JSON数据
        if isinstance(args, str):
            parsed_data = json.loads(args)
        elif isinstance(args, dict) and len(args) == 1 and isinstance(list(args.values())[0], str):
            # 检查是否是包含JSON字符串的字典
            potential_json = list(args.values())[0]
            try:
                parsed_data = json.loads(potential_json)
            except json.JSONDecodeError:
                parsed_data = args
        else:
            parsed_data = args
        
        result['parsed_data'] = parsed_data
        
        # 从解析的数据中提取文件路径
        file_paths = []
        if isinstance(parsed_data, dict):
            # 检查字典中的所有值，查找可能的文件路径
            for key, value in parsed_data.items():
                if isinstance(value, str) and os.path.exists(value):
                    file_paths.append(value)
                elif isinstance(value, list):
                    # 如果值是列表，检查其中的字符串是否为文件路径
                    for item in value:
                        if isinstance(item, str) and os.path.exists(item):
                            file_paths.append(item)
        elif isinstance(parsed_data, list):
            # 如果是列表，检查其中的字符串元素是否为文件路径
            for item in parsed_data:
                if isinstance(item, str) and os.path.exists(item):
                    file_paths.append(item)
        
        # 检查文件是否存在
        for file_path in file_paths:
            exists = os.path.exists(file_path)
            result['file_checks'][file_path] = exists
            
            if exists:
                result['valid_files'].append(file_path)
            else:
                result['missing_files'].append(file_path)
        
        # 生成洞察
        if result['valid_files']:
            insights.append(f"发现 {len(result['valid_files'])} 个有效文件")
        if result['missing_files']:
            insights.append(f"发现 {len(result['missing_files'])} 个缺失文件")
        
        if not file_paths:
            insights.append("未找到任何有效的文件路径")
        
        # 生成事实三元组
        facts.append(("file_validation", "has_valid_files_count", str(len(result['valid_files']))))
        facts.append(("file_validation", "has_missing_files_count", str(len(result['missing_files']))))
        
        # 根据结果提供建议
        next_skills = []
        if result['missing_files']:
            next_skills.append("skill_file_generator")  # 如果有缺失文件，建议生成文件
        if result['valid_files']:
            next_skills.append("skill_file_analyzer")  # 如果有有效文件，建议分析文件
    
    except json.JSONDecodeError as e:
        result['error'] = f"JSON解析错误: {str(e)}"
        insights.append("参数不是有效的JSON格式")
    except Exception as e:
        result['error'] = f"处理过程中发生错误: {str(e)}"
        insights.append(f"处理过程中发生错误: {str(e)}")
    
    return {
        'result': result,
        'insights': insights,
        'facts': facts,
        'next_skills': next_skills if result['valid_files'] or result['missing_files'] else []
    }