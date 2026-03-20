"""
自动生成的技能模块
需求: 锻造一个技能：分析技能执行结果中的错误模式，统计成功率与失败模式的关联性。需要查询skill_results表，分析result_json中包含error或failed等关键词的记录，计算整体成功率，并按技能类型分组统计错误分布。
生成时间: 2026-03-11 11:15:23
"""

# skill_name: skill_error_analysis_reporter
import json
import sqlite3
import os
from collections import defaultdict

def main(args=None):
    """
    分析技能执行结果中的错误模式，统计成功率与失败模式的关联性。
    查询skill_results表，分析result_json中包含error或failed等关键词的记录，
    计算整体成功率，并按技能类型分组统计错误分布。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径是否有效
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'}, 
            'insights': ['无法访问数据库']
        }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 获取所有技能执行结果
        cursor.execute("SELECT skill_name, result_json FROM skill_results")
        rows = cursor.fetchall()
        
        total_executions = len(rows)
        if total_executions == 0:
            return {
                'result': {'error': '没有技能执行记录'},
                'insights': ['数据库中没有技能执行记录']
            }
        
        # 初始化统计数据
        success_count = 0
        failed_count = 0
        skill_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0, 'errors': []})
        
        for skill_name, result_json in rows:
            try:
                result_data = json.loads(result_json) if result_json else {}
            except json.JSONDecodeError:
                result_data = {}
            
            # 检查是否为失败的执行
            is_error = False
            error_msg = ""
            
            # 检查result_json中是否包含错误信息
            if isinstance(result_data, dict):
                result_str = json.dumps(result_data, ensure_ascii=False).lower()
                if 'error' in result_str or 'failed' in result_str or 'exception' in result_str:
                    is_error = True
                    error_msg = result_str[:200]  # 只取前200字符作为错误摘要
            else:
                # 如果result_json不是有效字典，可能是错误情况
                is_error = True
                error_msg = str(result_json)[:200] if result_json else "empty_result"
            
            # 更新统计
            skill_stats[skill_name]['total'] += 1
            
            if is_error:
                skill_stats[skill_name]['failed'] += 1
                skill_stats[skill_name]['errors'].append(error_msg)
                failed_count += 1
            else:
                skill_stats[skill_name]['success'] += 1
                success_count += 1
        
        # 计算整体成功率
        overall_success_rate = (success_count / total_executions) * 100 if total_executions > 0 else 0
        
        # 生成详细的技能统计
        detailed_stats = {}
        for skill, stats in skill_stats.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            detailed_stats[skill] = {
                'total_executions': stats['total'],
                'success_count': stats['success'],
                'failure_count': stats['failed'],
                'success_rate': success_rate,
                'error_samples': stats['errors'][:5]  # 只取前5个错误样本作为示例
            }
        
        # 识别错误模式
        error_patterns = defaultdict(int)
        for skill, stats in skill_stats.items():
            for error in stats['errors']:
                # 简单的错误模式识别
                if 'timeout' in error.lower():
                    error_patterns['timeout'] += 1
                elif 'connection' in error.lower():
                    error_patterns['connection_error'] += 1
                elif 'not found' in error.lower() or '404' in error.lower():
                    error_patterns['not_found'] += 1
                elif 'permission' in error.lower() or 'forbidden' in error.lower():
                    error_patterns['permission_denied'] += 1
                elif 'memory' in error.lower():
                    error_patterns['memory_error'] += 1
                elif 'value' in error.lower():
                    error_patterns['value_error'] += 1
                else:
                    error_patterns['other'] += 1
        
        # 准备返回结果
        analysis_result = {
            'summary': {
                'total_executions': total_executions,
                'successful_executions': success_count,
                'failed_executions': failed_count,
                'overall_success_rate': round(overall_success_rate, 2)
            },
            'skill_breakdown': detailed_stats,
            'error_patterns': dict(error_patterns)
        }
        
        # 生成洞察
        insights = [
            f"整体技能执行成功率为 {overall_success_rate:.2f}%",
            f"共分析了 {len(skill_stats)} 种不同技能的执行结果",
            f"最常见的错误类型为: {max(error_patterns, key=error_patterns.get) if error_patterns else '无'}"
        ]
        
        # 如果成功率低于80%，添加警告洞察
        if overall_success_rate < 80:
            insights.append(f"警告: 整体成功率低于80%，需要关注技能执行稳定性")
        
        return {
            'result': analysis_result,
            'insights': insights
        }
        
    except Exception as e:
        return {
            'result': {'error': f'分析过程中发生错误: {str(e)}'},
            'insights': [f'技能错误分析执行失败: {str(e)}']
        }
    finally:
        conn.close()