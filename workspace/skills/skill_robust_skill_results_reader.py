"""
自动生成的技能模块
需求: 创建一个 robust_skill_results_reader 技能，能够安全地从 skill_results 表中读取并汇总技能执行结果。该技能应处理可能的 JSON 解析错误，提供清晰的错误信息，并返回结构化的结果摘要，包括成功/失败统计、执行时间分布和最近的执行记录。
生成时间: 2026-03-11 21:39:06
"""

# skill_name: robust_skill_results_reader
import json
import sqlite3
import os
from datetime import datetime

def main(args=None):
    """
    安全地从skill_results表中读取并汇总技能执行结果。
    该技能处理可能的JSON解析错误，提供清晰的错误信息，并返回结构化的结果摘要，
    包括成功/失败统计、执行时间分布和最近的执行记录。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'}, 
            'insights': ['无法访问数据库']
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询所有技能结果
        cursor.execute("""
            SELECT skill_name, result_json, timestamp 
            FROM skill_results 
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        
        total_executions = len(rows)
        successful_executions = 0
        failed_executions = 0
        skill_stats = {}
        recent_executions = []
        
        for row in rows:
            skill_name, result_json_str, timestamp = row
            
            # 统计技能执行次数
            if skill_name not in skill_stats:
                skill_stats[skill_name] = {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'executions': []
                }
            
            skill_stats[skill_name]['total'] += 1
            
            # 尝试解析result_json
            try:
                result_data = json.loads(result_json_str) if result_json_str else {}
                
                # 检查是否有错误信息
                if 'error' in result_data or (isinstance(result_data, dict) and 
                                              any('error' in str(v).lower() for v in result_data.values())):
                    failed_executions += 1
                    skill_stats[skill_name]['failed'] += 1
                else:
                    successful_executions += 1
                    skill_stats[skill_name]['success'] += 1
                
            except json.JSONDecodeError:
                # JSON解析失败，认为是失败的执行
                failed_executions += 1
                skill_stats[skill_name]['failed'] += 1
            
            # 记录最近的执行记录（限制为最近10条）
            if len(recent_executions) < 10:
                try:
                    result_data = json.loads(result_json_str) if result_json_str else {}
                except json.JSONDecodeError:
                    result_data = {"raw_result": result_json_str}
                
                recent_executions.append({
                    'skill_name': skill_name,
                    'timestamp': timestamp,
                    'result': result_data
                })
        
        conn.close()
        
        # 计算成功率
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # 构建结果摘要
        summary = {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'skill_statistics': skill_stats,
            'recent_executions': recent_executions
        }
        
        insights = [
            f"总共执行了 {total_executions} 次技能",
            f"成功执行 {successful_executions} 次，失败 {failed_executions} 次",
            f"整体成功率为 {success_rate:.2f}%"
        ]
        
        # 添加各技能的统计信息到insights
        for skill, stats in skill_stats.items():
            skill_success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            insights.append(f"技能 {skill}: 执行 {stats['total']} 次，成功率 {skill_success_rate:.2f}%")
        
        return {
            'result': summary,
            'insights': insights
        }
        
    except Exception as e:
        return {
            'result': {'error': f'读取技能结果时发生错误: {str(e)}'},
            'insights': [f'技能结果读取失败: {str(e)}']
        }