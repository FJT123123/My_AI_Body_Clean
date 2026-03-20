"""
自动生成的技能模块
需求: 读取并汇总 skill_results 表中的技能执行记录，支持按技能名称过滤、按时间范围筛选、按执行结果状态（成功/失败）分类，并生成结构化的汇总报告，包括执行次数、成功率、平均执行时间等统计信息。
生成时间: 2026-03-11 20:59:20
"""

# skill_name: skill_execution_analyzer
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

def main(args=None) -> Dict[str, Any]:
    """
    读取并汇总 skill_results 表中的技能执行记录，支持按技能名称过滤、按时间范围筛选、
    按执行结果状态（成功/失败）分类，并生成结构化的汇总报告，
    包括执行次数、成功率、平均执行时间等统计信息
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 验证数据库路径
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'}, 
            'insights': ['无法访问数据库']
        }
    
    # 获取过滤参数
    filters = args.get('filters', {})
    skill_name_filter = filters.get('skill_name')
    start_time = filters.get('start_time')
    end_time = filters.get('end_time')
    status_filter = filters.get('status')  # 'success' or 'failed'
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 构建查询语句
        query = "SELECT skill_name, result_json, timestamp FROM skill_results WHERE 1=1"
        params = []
        
        # 添加技能名称过滤
        if skill_name_filter:
            query += " AND skill_name = ?"
            params.append(skill_name_filter)
        
        # 添加时间范围过滤
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        
        query += " ORDER BY timestamp"
        
        # 执行查询
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # 初始化统计结果
        statistics = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'success_rate': 0.0,
            'execution_summary': {},
            'time_range': {
                'start': None,
                'end': None
            },
            'skills_analyzed': set()
        }
        
        if not rows:
            return {
                'result': statistics,
                'insights': ['在指定条件下没有找到技能执行记录']
            }
        
        # 处理每一行数据
        execution_times = []
        for row in rows:
            skill_name, result_json_str, timestamp = row
            statistics['skills_analyzed'].add(skill_name)
            statistics['total_executions'] += 1
            
            # 确定执行状态
            success = True
            try:
                result_data = json.loads(result_json_str)
                if isinstance(result_data, dict) and 'error' in result_data:
                    success = False
            except json.JSONDecodeError:
                success = False
            
            # 更新时间范围
            if statistics['time_range']['start'] is None or timestamp < statistics['time_range']['start']:
                statistics['time_range']['start'] = timestamp
            if statistics['time_range']['end'] is None or timestamp > statistics['time_range']['end']:
                statistics['time_range']['end'] = timestamp
            
            # 按技能分组统计
            if skill_name not in statistics['execution_summary']:
                statistics['execution_summary'][skill_name] = {
                    'total': 0,
                    'success': 0,
                    'failed': 0
                }
            
            statistics['execution_summary'][skill_name]['total'] += 1
            
            if success:
                statistics['successful_executions'] += 1
                statistics['execution_summary'][skill_name]['success'] += 1
            else:
                statistics['failed_executions'] += 1
                statistics['execution_summary'][skill_name]['failed'] += 1
        
        # 计算成功率
        if statistics['total_executions'] > 0:
            statistics['success_rate'] = statistics['successful_executions'] / statistics['total_executions']
        
        # 转换集合为列表以便JSON序列化
        statistics['skills_analyzed'] = list(statistics['skills_analyzed'])
        
        # 生成洞察
        insights = []
        if statistics['total_executions'] > 0:
            insights.append(f"共执行 {statistics['total_executions']} 次技能")
            insights.append(f"成功 {statistics['successful_executions']} 次，失败 {statistics['failed_executions']} 次")
            insights.append(f"整体成功率: {statistics['success_rate']:.2%}")
            
            if statistics['skills_analyzed']:
                insights.append(f"分析了 {len(statistics['skills_analyzed'])} 个不同技能: {', '.join(statistics['skills_analyzed'])}")
        
        return {
            'result': statistics,
            'insights': insights
        }
        
    except Exception as e:
        return {
            'result': {'error': f'处理技能执行记录时出错: {str(e)}'},
            'insights': [f'技能执行分析失败: {str(e)}']
        }