"""
自动生成的技能模块
需求: 创建一个技能，能够查询skill_results表并返回所有技能执行记录的汇总信息，包括技能名称、执行时间、时间戳等关键字段。
生成时间: 2026-03-12 06:35:32
"""

# skill_name: skill_execution_history_analyzer

def main(args=None):
    """
    查询skill_results表并返回所有技能执行记录的汇总信息，包括技能名称、执行时间、时间戳等关键字段。
    该技能用于分析历史技能执行情况，提供技能执行概览。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    import sqlite3
    import os
    
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'}, 
            'insights': ['无法访问数据库']
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询skill_results表的所有记录
        query = """
        SELECT skill_name, input_args, result_json, result_summary, timestamp
        FROM skill_results
        ORDER BY timestamp DESC
        """
        
        rows = cursor.execute(query).fetchall()
        
        # 构建结果列表
        execution_records = []
        for row in rows:
            record = {
                'skill_name': row[0],
                'input_args': row[1],
                'result_json': row[2],
                'result_summary': row[3],
                'timestamp': row[4]
            }
            execution_records.append(record)
        
        conn.close()
        
        # 生成一些洞察信息
        insights = []
        if execution_records:
            skill_names = [record['skill_name'] for record in execution_records]
            unique_skills = set(skill_names)
            insights.append(f"共执行了 {len(execution_records)} 次技能调用")
            insights.append(f"涉及 {len(unique_skills)} 个不同技能")
            insights.append(f"最近执行的技能: {skill_names[0] if skill_names else 'None'}")
        else:
            insights.append("没有找到技能执行记录")
        
        result = {
            'total_executions': len(execution_records),
            'unique_skills_count': len(set(record['skill_name'] for record in execution_records)),
            'execution_records': execution_records
        }
        
        return {
            'result': result,
            'insights': insights
        }
        
    except Exception as e:
        return {
            'result': {'error': str(e)},
            'insights': [f'查询技能执行历史时发生错误: {str(e)}']
        }