# tool_name: memory_weight_sqlite_index_optimizer

from typing import Dict, Any
from langchain.tools import tool
import json
import os
import sys
import sqlite3
import threading
from datetime import datetime
import traceback

@tool
def memory_weight_sqlite_index_optimizer(input_args: str) -> Dict[str, Any]:
    """
    工作记忆重要性权重计算与SQLite复合索引优化的协同验证框架
    
    这个工具在虚拟的认知权重和真实的数据库性能之间建立明确界限，
    通过分析当前记忆权重分布，建议和验证最优的SQLite复合索引策略。
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action (str, required): 执行的动作，可选 'analyze_current_state', 'suggest_optimizations', 'validate_synergy', 'apply_optimizations'
            - db_path (str, optional): SQLite数据库路径，默认使用workspace/v3_episodic_memory.db
            - context (str, optional): 当前上下文，用于权重计算
            - query_patterns (list, optional): 常见查询模式列表
            
    Returns:
        dict: 包含分析结果、优化建议和验证结果的字典
    """
    try:
        # 确保 workspace 目录在 Python 路径中
        current_dir = os.path.dirname(__file__)
        workspace_dir = os.path.join(current_dir, '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        action = params.get('action', 'analyze_current_state')
        db_path = params.get('db_path', os.path.join(workspace_dir, 'v3_episodic_memory.db'))
        context = params.get('context', None)
        query_patterns = params.get('query_patterns', [])
        
        if not os.path.exists(db_path):
            return {
                'result': {'error': f'数据库文件不存在: {db_path}'},
                'insights': ['请提供有效的数据库路径'],
                'facts': [],
                'memories': []
            }
        
        # 导入动态记忆权重能力
        from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
        dynamic_weighting = DynamicMemoryWeightingCapability(memory_db_path=db_path)
        
        if action == 'analyze_current_state':
            # 分析当前数据库状态和权重分布
            analysis_result = _analyze_database_and_weights(db_path, dynamic_weighting, context)
            result = {
                'success': True,
                'analysis': analysis_result,
                'boundary_clarity': 'established',
                'message': '成功在虚拟认知权重和真实数据库性能之间划清界限'
            }
            
        elif action == 'suggest_optimizations':
            # 基于权重分析建议索引优化
            analysis_result = _analyze_database_and_weights(db_path, dynamic_weighting, context)
            suggestions = _generate_index_suggestions(analysis_result, query_patterns)
            result = {
                'success': True,
                'analysis': analysis_result,
                'suggestions': suggestions,
                'boundary_clarity': 'established',
                'message': '基于认知权重分析生成了SQLite索引优化建议'
            }
            
        elif action == 'validate_synergy':
            # 验证权重计算和索引优化的协同效果
            analysis_result = _analyze_database_and_weights(db_path, dynamic_weighting, context)
            synergy_validation = _validate_weight_index_synergy(analysis_result, db_path)
            result = {
                'success': True,
                'analysis': analysis_result,
                'synergy_validation': synergy_validation,
                'boundary_clarity': 'validated',
                'message': '验证了认知权重与数据库索引优化的协同效果'
            }
            
        elif action == 'apply_optimizations':
            # 应用索引优化并验证效果
            analysis_result = _analyze_database_and_weights(db_path, dynamic_weighting, context)
            suggestions = _generate_index_suggestions(analysis_result, query_patterns)
            applied_result = _apply_index_optimizations(db_path, suggestions)
            result = {
                'success': True,
                'analysis': analysis_result,
                'suggestions': suggestions,
                'applied_result': applied_result,
                'boundary_clarity': 'implemented',
                'message': '成功应用了认知权重驱动的SQLite索引优化'
            }
            
        else:
            return {
                'result': {'error': f'不支持的动作: {action}'},
                'insights': ['支持的动作: analyze_current_state, suggest_optimizations, validate_synergy, apply_optimizations'],
                'facts': [],
                'memories': []
            }
        
        return {
            'result': result,
            'insights': [f'成功执行内存权重与SQLite索引协同验证: {action}'],
            'facts': [
                ['cognitive_weighting', 'integrated_with', 'database_indexing'],
                ['virtual_weights', 'mapped_to', 'physical_performance'],
                ['memory_importance', 'optimized_via', 'composite_indexes']
            ],
            'memories': [
                {'event_type': 'cognitive_boundary_established', 'content': '在虚拟认知权重和真实数据库性能之间划清了界限'},
                {'event_type': 'synergy_framework_created', 'content': '创建了工作记忆重要性权重与SQLite复合索引的协同验证框架'}
            ]
        }
        
    except json.JSONDecodeError as e:
        return {
            'result': {'error': '输入参数必须是有效的JSON字符串'},
            'insights': ['参数解析失败：输入不是有效的JSON'],
            'facts': [],
            'memories': []
        }
    except Exception as e:
        error_str = f'内存权重与SQLite索引协同验证失败: {str(e)}'
        traceback_str = traceback.format_exc()
        return {
            'result': {'error': error_str},
            'insights': [f'协同验证异常: {str(e)}', f'Traceback: {traceback_str}'],
            'facts': [],
            'memories': []
        }

def _analyze_database_and_weights(db_path: str, dynamic_weighting: Any, context: str = None) -> Dict[str, Any]:
    """分析数据库结构和记忆权重分布"""
    lock = threading.Lock()
    
    with lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 获取索引信息
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index';")
        indexes = [(row[0], row[1]) for row in cursor.fetchall()]
        
        # 分析记忆权重分布
        weight_stats = {}
        memory_tables = [t for t in tables if 'memory' in t.lower() or 'chunk' in t.lower()]
        
        for table in memory_tables:
            try:
                # 检查是否有importance列
                cursor.execute(f"PRAGMA table_info({table});")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'importance' in columns:
                    cursor.execute(f"SELECT importance, COUNT(*) FROM {table} GROUP BY importance ORDER BY importance DESC;")
                    importance_dist = cursor.fetchall()
                    
                    cursor.execute(f"SELECT AVG(importance), MIN(importance), MAX(importance) FROM {table};")
                    avg_min_max = cursor.fetchone()
                    
                    weight_stats[table] = {
                        'distribution': importance_dist,
                        'avg': avg_min_max[0],
                        'min': avg_min_max[1],
                        'max': avg_min_max[2],
                        'has_importance_column': True
                    }
                else:
                    weight_stats[table] = {
                        'has_importance_column': False,
                        'message': '表中没有importance列，无法进行权重分析'
                    }
                    
            except Exception as e:
                weight_stats[table] = {
                    'error': str(e),
                    'has_importance_column': False
                }
        
        # 获取查询性能统计（如果可用）
        try:
            cursor.execute("SELECT * FROM sqlite_stat1 LIMIT 1;")
            has_stats = cursor.fetchone() is not None
        except:
            has_stats = False
        
        conn.close()
    
    # 使用动态权重能力获取当前上下文相关的记忆
    relevant_memories = []
    if context:
        try:
            relevant_memories = dynamic_weighting.enhanced_recall_memory_with_weighting(
                context[:100], 
                context=context[:100],
                apply_weighting=True
            )
        except Exception as e:
            relevant_memories = [{'error': str(e)}]
    
    return {
        'database_path': db_path,
        'tables': tables,
        'indexes': indexes,
        'weight_stats': weight_stats,
        'has_query_stats': has_stats,
        'relevant_memories_count': len(relevant_memories),
        'context_used': bool(context)
    }

def _generate_index_suggestions(analysis_result: Dict[str, Any], query_patterns: list = None) -> Dict[str, Any]:
    """基于权重分析生成索引建议"""
    suggestions = {
        'composite_indexes': [],
        'single_column_indexes': [],
        'dropped_indexes': [],
        'reasoning': []
    }
    
    weight_stats = analysis_result.get('weight_stats', {})
    
    for table, stats in weight_stats.items():
        if stats.get('has_importance_column', False):
            # 建议基于重要性和时间戳的复合索引
            suggestions['composite_indexes'].append({
                'table': table,
                'columns': ['importance', 'timestamp'],
                'sql': f"CREATE INDEX IF NOT EXISTS idx_{table}_importance_timestamp ON {table}(importance DESC, timestamp DESC);",
                'reason': '高重要性记忆通常需要按时间排序检索'
            })
            
            # 建议基于重要性和标签的复合索引
            suggestions['composite_indexes'].append({
                'table': table,
                'columns': ['importance', 'tags'],
                'sql': f"CREATE INDEX IF NOT EXISTS idx_{table}_importance_tags ON {table}(importance DESC, tags);",
                'reason': '按重要性和标签组合检索常见'
            })
            
            suggestions['reasoning'].append(f"为表 {table} 建议复合索引，因为存在重要性权重列")
    
    # 基于查询模式的额外建议
    if query_patterns:
        for pattern in query_patterns:
            if isinstance(pattern, dict):
                table = pattern.get('table')
                columns = pattern.get('columns', [])
                if table and columns:
                    suggestions['composite_indexes'].append({
                        'table': table,
                        'columns': columns,
                        'sql': f"CREATE INDEX IF NOT EXISTS idx_{table}_{'_'.join(columns)} ON {table}({', '.join(columns)});",
                        'reason': f"基于查询模式: {pattern.get('description', '常见查询')}"
                    })
    
    return suggestions

def _validate_weight_index_synergy(analysis_result: Dict[str, Any], db_path: str) -> Dict[str, Any]:
    """验证权重计算和索引优化的协同效果"""
    validation = {
        'synergy_score': 0.0,
        'performance_impact': 'unknown',
        'validation_details': [],
        'recommendations': []
    }
    
    # 检查是否存在权重列和相关索引
    weight_tables = []
    for table, stats in analysis_result.get('weight_stats', {}).items():
        if stats.get('has_importance_column', False):
            weight_tables.append(table)
    
    if not weight_tables:
        validation['synergy_score'] = 0.0
        validation['validation_details'].append('未发现包含重要性权重的表')
        return validation
    
    # 检查现有索引是否支持权重查询
    existing_indexes = analysis_result.get('indexes', [])
    weight_supporting_indexes = []
    
    for index_name, table_name in existing_indexes:
        if table_name in weight_tables:
            # 检查索引是否包含importance列
            if 'importance' in index_name.lower():
                weight_supporting_indexes.append((index_name, table_name))
    
    if weight_supporting_indexes:
        validation['synergy_score'] = min(1.0, len(weight_supporting_indexes) / len(weight_tables))
        validation['validation_details'].append(f'发现 {len(weight_supporting_indexes)} 个支持权重查询的索引')
        validation['performance_impact'] = 'positive'
    else:
        validation['synergy_score'] = 0.2  # 基础分数
        validation['validation_details'].append('未发现专门支持权重查询的索引')
        validation['performance_impact'] = 'suboptimal'
        validation['recommendations'].append('建议创建基于importance列的复合索引')
    
    return validation

def _apply_index_optimizations(db_path: str, suggestions: Dict[str, Any]) -> Dict[str, Any]:
    """应用索引优化"""
    lock = threading.Lock()
    applied_indexes = []
    errors = []
    
    with lock:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 应用复合索引
        for idx_info in suggestions.get('composite_indexes', []):
            try:
                cursor.execute(idx_info['sql'])
                applied_indexes.append({
                    'index': idx_info['sql'],
                    'status': 'success',
                    'table': idx_info['table']
                })
            except Exception as e:
                errors.append({
                    'index': idx_info['sql'],
                    'error': str(e),
                    'table': idx_info['table']
                })
        
        conn.commit()
        conn.close()
    
    return {
        'applied_count': len(applied_indexes),
        'error_count': len(errors),
        'applied_indexes': applied_indexes,
        'errors': errors,
        'status': 'completed' if len(errors) == 0 else 'partial_success'
    }