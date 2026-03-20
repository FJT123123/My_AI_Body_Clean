"""
自动生成的技能模块
需求: 创建一个技能，用于诊断其他技能的执行失败原因。该技能接收技能名称作为输入，检查该技能文件是否存在、语法是否正确、是否缺少必要的上下文参数，并分析其最近的执行记录以确定失败模式。
生成时间: 2026-03-11 16:08:56
"""

# skill_name: skill_execution_failure_analyzer

import os
import ast
import json
import sqlite3
from pathlib import Path


def main(args=None):
    """
    技能执行失败诊断器：接收技能名称作为输入，检查该技能文件是否存在、语法是否正确、
    是否缺少必要的上下文参数，并分析其最近的执行记录以确定失败模式。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 获取输入的技能名称
    skill_name = args.get('skill_name', '')
    if not skill_name:
        return {
            'result': {'error': '缺少技能名称参数'},
            'insights': ['技能执行失败诊断需要提供技能名称']
        }
    
    # 检查数据库是否可用
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': [f'无法访问数据库，无法分析技能 {skill_name} 的执行记录']
        }
    
    # 准备分析结果
    analysis_results = {
        'skill_name': skill_name,
        'file_exists': False,
        'syntax_valid': False,
        'missing_context_params': [],
        'recent_execution_records': [],
        'failure_patterns': [],
        'recommendations': []
    }
    
    insights = []
    
    # 检查技能文件是否存在
    skill_file_path = Path(f"{skill_name}.py")
    if skill_file_path.exists():
        analysis_results['file_exists'] = True
        insights.append(f"技能文件 {skill_name}.py 存在")
        
        # 读取文件内容并验证语法
        try:
            with open(skill_file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # 尝试解析语法
            tree = ast.parse(code_content)
            analysis_results['syntax_valid'] = True
            insights.append(f"技能 {skill_name}.py 语法正确")
            
            # 分析上下文依赖
            context_params = []
            main_func = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'main':
                    main_func = node
                    break
            
            if main_func:
                # 检查main函数中的上下文访问
                for node in ast.walk(main_func):
                    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == 'args':
                        if isinstance(node.slice, ast.Constant) and node.slice.value == '__context__':
                            context_params.append('__context__')
                        elif isinstance(node.slice, ast.Str) and node.slice.s == '__context__':
                            context_params.append('__context__')
                    elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Subscript):
                        if isinstance(node.value.value, ast.Name) and node.value.value.id == 'args':
                            if isinstance(node.value.slice, ast.Constant) and node.value.slice.value == '__context__':
                                context_params.append(f"__context__['{node.attr}']")
            
            analysis_results['missing_context_params'] = list(set(context_params))
        except SyntaxError as e:
            analysis_results['syntax_valid'] = False
            analysis_results['syntax_error'] = f"语法错误: {e.msg} at line {e.lineno}"
            insights.append(f"技能 {skill_name}.py 存在语法错误")
        except Exception as e:
            analysis_results['syntax_valid'] = False
            analysis_results['syntax_error'] = f"解析错误: {str(e)}"
            insights.append(f"解析技能 {skill_name}.py 文件时出错")
    else:
        analysis_results['file_exists'] = False
        insights.append(f"技能文件 {skill_name}.py 不存在")
    
    # 查询数据库中该技能的执行记录
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, skill_name, input_args, result_json, result_summary, timestamp
            FROM skill_results
            WHERE skill_name = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """, (skill_name,))
        
        rows = cursor.fetchall()
        execution_records = []
        
        for row in rows:
            record = {
                'id': row[0],
                'skill_name': row[1],
                'input_args': row[2],
                'result_json': row[3],
                'result_summary': row[4],
                'timestamp': row[5]
            }
            execution_records.append(record)
        
        # 分析失败模式
        failure_count = 0
        success_count = 0
        error_types = {}
        
        for record in execution_records:
            result_json = record['result_json']
            if result_json:
                try:
                    result_data = json.loads(result_json)
                    if isinstance(result_data, dict) and 'error' in result_data:
                        failure_count += 1
                        error_msg = result_data['error']
                        if error_msg in error_types:
                            error_types[error_msg] += 1
                        else:
                            error_types[error_msg] = 1
                    else:
                        success_count += 1
                except json.JSONDecodeError:
                    failure_count += 1
                    if 'json_decode_error' in error_types:
                        error_types['json_decode_error'] += 1
                    else:
                        error_types['json_decode_error'] = 1
            else:
                success_count += 1
        
        analysis_results['recent_execution_records'] = execution_records
        analysis_results['execution_summary'] = {
            'total_executions': len(execution_records),
            'success_count': success_count,
            'failure_count': failure_count,
            'error_types': error_types
        }
        
        # 生成失败模式分析
        if failure_count > 0:
            failure_patterns = []
            for error_msg, count in error_types.items():
                failure_patterns.append({
                    'error_type': error_msg,
                    'occurrence_count': count,
                    'percentage': round((count / failure_count) * 100, 2)
                })
            analysis_results['failure_patterns'] = failure_patterns
            insights.append(f"技能 {skill_name} 最近执行中失败 {failure_count} 次，成功 {success_count} 次")
        
        conn.close()
    except Exception as e:
        analysis_results['database_error'] = f"查询执行记录时出错: {str(e)}"
        insights.append(f"查询数据库以获取 {skill_name} 执行记录时出错")
    
    # 生成建议
    recommendations = []
    if not analysis_results['file_exists']:
        recommendations.append(f"创建技能文件 {skill_name}.py")
    elif not analysis_results['syntax_valid']:
        recommendations.append(f"修复技能文件 {skill_name}.py 的语法错误")
    
    if analysis_results.get('execution_summary', {}).get('failure_count', 0) > 0:
        recommendations.append(f"根据失败模式分析，优化技能 {skill_name} 的错误处理逻辑")
    
    if not recommendations:
        recommendations.append(f"技能 {skill_name} 似乎正常运行，没有发现明显问题")
    
    analysis_results['recommendations'] = recommendations
    
    # 记录洞察
    insights.append(f"完成对技能 {skill_name} 的执行失败诊断分析")
    
    # 如果存在显著的失败模式，记录为洞察
    if analysis_results.get('execution_summary', {}).get('failure_count', 0) > 0:
        insights.append(f"技能 {skill_name} 存在执行失败问题，需进一步修复")
    
    return {
        'result': analysis_results,
        'insights': insights,
        'facts': [
            {
                'subject': skill_name,
                'relation': 'has_file_existence',
                'object': str(analysis_results['file_exists'])
            },
            {
                'subject': skill_name,
                'relation': 'has_syntax_validity',
                'object': str(analysis_results['syntax_valid'])
            }
        ],
        'memories': [
            {
                'event_type': 'skill_health_check',
                'content': f"技能 {skill_name} 执行失败诊断结果: {json.dumps(analysis_results, ensure_ascii=False)}",
                'importance': 0.8
            }
        ]
    }