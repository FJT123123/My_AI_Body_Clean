"""
自动生成的技能模块
需求: 分析技能执行历史中特定技能的调用模式和参数分布，识别潜在的迁移等价类结构。输入为技能名称，输出包括调用频率、参数模式、执行结果的稳定性指标。
生成时间: 2026-03-11 12:47:27
"""

# skill_name: skill_execution_pattern_analyzer
import sqlite3
import os
import json
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple

def main(args=None):
    """
    分析技能执行历史中特定技能的调用模式和参数分布，识别潜在的迁移等价类结构。
    输入为技能名称，输出包括调用频率、参数模式、执行结果的稳定性指标。
    """
    if args is None:
        args = {}

    # 处理字符串格式的输入（如 "skill_name=xxx"）
    if isinstance(args, str):
        if args.startswith("skill_name="):
            args = {'skill_name': args.split("=", 1)[1]}
        else:
            return {'result': {'error': '无法解析字符串参数'}, 'insights': ['参数格式应为 "skill_name=技能名称"']}

    context = args.get('__context__', {})
    db_path = context.get('db_path', '')

    # 获取输入参数
    skill_name = args.get('skill_name')
    if not skill_name:
        return {'result': {'error': '缺少skill_name参数'}, 'insights': ['需要提供要分析的技能名称']}
    
    # 检查数据库路径
    if not db_path or not os.path.exists(db_path):
        return {'result': {'error': 'db_path 不可用'}, 'insights': ['无法访问数据库']}
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 查询技能执行历史
        query = """
            SELECT skill_name, input_args, result_json, result_summary, timestamp
            FROM skill_results
            WHERE skill_name LIKE ?
        """
        rows = conn.execute(query, (f'%{skill_name}%',)).fetchall()
        
        conn.close()
        
        if not rows:
            return {'result': {'error': f'未找到技能 {skill_name} 的执行记录'}, 'insights': [f'技能 {skill_name} 从未被执行过']}
        
        # 分析调用模式
        total_calls = len(rows)
        timestamp_list = [row[4] for row in rows]
        
        # 解析输入参数并统计模式
        input_arg_patterns = []
        result_summaries = []
        
        for row in rows:
            try:
                input_args_str = row[1]
                if input_args_str:
                    if input_args_str.startswith('{'):
                        input_args = json.loads(input_args_str)
                    else:
                        input_args = {"raw_input": input_args_str}
                else:
                    input_args = {}
                input_arg_patterns.append(input_args)

                result_summary = row[3] if row[3] else "无结果摘要"
                result_summaries.append(result_summary)
            except Exception:
                input_arg_patterns.append({})
        
        # 统计参数分布
        param_distribution = defaultdict(list)
        for args_dict in input_arg_patterns:
            if isinstance(args_dict, dict):
                for key, value in args_dict.items():
                    param_distribution[key].append(str(value))
        
        # 分析参数模式
        parameter_patterns = {}
        for key, values in param_distribution.items():
            value_counts = Counter(values)
            parameter_patterns[key] = {
                'unique_values': len(value_counts),
                'most_common': value_counts.most_common(3),
                'value_distribution': dict(value_counts)
            }
        
        # 分析结果稳定性
        result_summary_counts = Counter(result_summaries)
        stability_score = len(set(result_summaries)) / max(len(result_summaries), 1)
        
        # 生成分析结果
        analysis_result = {
            'skill_name': skill_name,
            'total_calls': total_calls,
            'call_frequency_analysis': {
                'first_call': min(timestamp_list) if timestamp_list else None,
                'last_call': max(timestamp_list) if timestamp_list else None,
                'time_span_days': None
            },
            'parameter_distribution': parameter_patterns,
            'result_stability': {
                'stability_score': stability_score,
                'unique_result_types': len(set(result_summaries)),
                'result_type_distribution': dict(result_summary_counts)
            },
            'migration_equivalence_indicators': {
                'parameter_consistency_score': calculate_parameter_consistency(parameter_patterns),
                'result_consistency_score': calculate_result_consistency(result_summaries),
                'call_pattern_stability': stability_score
            }
        }
        
        # 计算时间跨度
        if timestamp_list:
            first = min(timestamp_list)
            last = max(timestamp_list)
            # 假设时间格式为 'YYYY-MM-DD HH:MM:SS'，简化计算天数
            try:
                from datetime import datetime
                first_time = datetime.fromisoformat(first.replace('Z', '+00:00')) if 'Z' in first else datetime.fromisoformat(first)
                last_time = datetime.fromisoformat(last.replace('Z', '+00:00')) if 'Z' in last else datetime.fromisoformat(last)
                time_span = (last_time - first_time).days
                analysis_result['call_frequency_analysis']['time_span_days'] = time_span
            except:
                analysis_result['call_frequency_analysis']['time_span_days'] = '无法解析时间格式'
        
        insights = [
            f"技能 {skill_name} 总共被调用了 {total_calls} 次",
            f"结果稳定性评分为 {stability_score:.2f} (值越低表示结果越一致)",
            f"识别到 {len(parameter_patterns)} 个不同的参数类型"
        ]
        
        return {
            'result': analysis_result,
            'insights': insights,
            'facts': [
                {
                    'subject': skill_name,
                    'relation': 'has_call_frequency',
                    'object': str(total_calls)
                },
                {
                    'subject': skill_name,
                    'relation': 'has_stability_score',
                    'object': str(stability_score)
                }
            ]
        }
    
    except Exception as e:
        return {
            'result': {'error': f'分析过程中出现错误: {str(e)}'},
            'insights': [f'分析失败: {str(e)}']
        }

def calculate_parameter_consistency(param_patterns: Dict[str, Any]) -> float:
    """计算参数一致性评分"""
    if not param_patterns:
        return 1.0
    
    total_consistency = 0
    num_params = 0
    
    for param_data in param_patterns.values():
        unique_vals = param_data.get('unique_values', 1)
        # 参数值越单一，一致性越高
        consistency = 1.0 / unique_vals if unique_vals > 0 else 1.0
        total_consistency += consistency
        num_params += 1
    
    return total_consistency / num_params if num_params > 0 else 1.0

def calculate_result_consistency(result_summaries: List[str]) -> float:
    """计算结果一致性评分"""
    if not result_summaries:
        return 1.0
    
    unique_count = len(set(result_summaries))
    return unique_count / len(result_summaries) if result_summaries else 1.0