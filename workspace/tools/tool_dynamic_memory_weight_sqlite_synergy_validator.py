# tool_name: dynamic_memory_weight_sqlite_synergy_validator
import json
import sqlite3
import os
import time
from typing import Dict, Any, List, Optional
from langchain.tools import tool

@tool
def dynamic_memory_weight_sqlite_synergy_validator(input_args: str = "") -> Dict[str, Any]:
    """
    动态记忆权重与SQLite索引协同验证工具
    
    这个工具专门用于验证动态记忆权重系统与现有SQLite索引的协同效果，
    不修改数据库结构，而是通过智能查询策略优化来实现认知效率最大化。
    
    Args:
        input_args (str): JSON字符串，包含以下可选参数:
            - action: 验证动作 ('validate_synergy', 'suggest_optimizations', 'benchmark_performance')
            - context: 当前上下文用于权重计算
            - query_patterns: 常见查询模式列表
            
    Returns:
        dict: 包含验证结果、优化建议和性能指标的字典
    """
    try:
        # 解析输入参数
        if input_args:
            try:
                params = json.loads(input_args)
            except json.JSONDecodeError:
                params = {}
        else:
            params = {}
        
        action = params.get('action', 'validate_synergy')
        context = params.get('context', '')
        query_patterns = params.get('query_patterns', [])
        
        # 获取数据库路径
        db_path = os.path.join(os.environ.get('ROOT_DIR', '.'), 'workspace', 'v3_episodic_memory.db')
        
        # 确保数据库存在
        if not os.path.exists(db_path):
            return {
                'success': False,
                'error': f'Database not found at {db_path}',
                'insights': [f'无法找到数据库文件: {db_path}'],
                'facts': [],
                'memories': []
            }
        
        # 获取动态记忆权重能力模块
        dynamic_memory_weighting_capability = load_capability_module("dynamic_memory_weighting_capability")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表结构信息
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        table_info = cursor.fetchall()
        columns = [col[1] for col in table_info]
        
        # 检查必要的列是否存在
        required_columns = ['memory_id', 'embedding_json', 'timestamp', 'content_text']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            return {
                'success': False,
                'error': f'Missing required columns: {missing_columns}',
                'insights': [f'数据库表缺少必要列: {missing_columns}'],
                'facts': [],
                'memories': []
            }
        
        # 执行不同的动作
        if action == 'validate_synergy':
            # 验证协同效果
            results = _validate_synergy(cursor, context, query_patterns, dynamic_memory_weighting_capability)
        elif action == 'suggest_optimizations':
            # 建议优化方案
            results = _suggest_optimizations(cursor, query_patterns, dynamic_memory_weighting_capability)
        elif action == 'benchmark_performance':
            # 性能基准测试
            results = _benchmark_performance(cursor, query_patterns, conn)
        else:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'insights': [f'不支持的操作: {action}'],
                'facts': [],
                'memories': []
            }
            
        conn.close()
        return results
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return {
            'success': False,
            'error': str(e),
            'insights': [f'执行过程中出现错误: {str(e)}'],
            'facts': [],
            'memories': []
        }

def _validate_synergy(cursor, context: str, query_patterns: List[str], dynamic_memory_weighting_capability) -> Dict[str, Any]:
    """验证动态记忆权重与SQLite索引的协同效果"""
    insights = []
    facts = []
    memories = []
    
    # 检查现有索引
    cursor.execute("PRAGMA index_list(memory_embeddings)")
    indexes = cursor.fetchall()
    index_names = [idx[1] for idx in indexes]
    
    insights.append(f"发现 {len(indexes)} 个现有索引: {index_names}")
    
    # 检查是否有针对重要查询模式的索引
    recommended_indexes = []
    table_columns = [col[1] for col in cursor.execute("PRAGMA table_info(memory_embeddings)").fetchall()]
    
    if "content_text" in table_columns:
        if not any("content_text" in idx_name for idx_name in index_names):
            recommended_indexes.append("CREATE INDEX idx_content_text ON memory_embeddings(content_text)")
            
    if "timestamp" in table_columns:
        if not any("timestamp" in idx_name for idx_name in index_names):
            recommended_indexes.append("CREATE INDEX idx_timestamp ON memory_embeddings(timestamp)")
    
    # 执行实际查询来评估性能
    actual_queries = []
    for pattern in query_patterns[:3]:  # 限制查询数量以避免性能问题
        try:
            # 使用EXPLAIN QUERY PLAN来分析查询计划
            explain_query = f"EXPLAIN QUERY PLAN {pattern}"
            cursor.execute(explain_query)
            query_plan = cursor.fetchall()
            
            # 检查是否使用了索引
            uses_index = any('SEARCH' in str(row) or 'INDEX' in str(row) for row in query_plan)
            
            actual_queries.append({
                'query': pattern,
                'uses_index': uses_index,
                'query_plan': str(query_plan)
            })
        except Exception as e:
            actual_queries.append({
                'query': pattern,
                'error': str(e)
            })
    
    # 使用动态记忆权重能力来评估权重分布
    try:
        # 获取当前记忆数据
        cursor.execute("SELECT memory_id, content_text, timestamp FROM memory_embeddings LIMIT 100")
        memory_data = cursor.fetchall()
        if memory_data:
            memories_list = []
            for row in memory_data:
                memory_item = {
                    'memory_id': row[0],
                    'content_text': row[1],
                    'timestamp': row[2]
                }
                memories_list.append(memory_item)
            
            # 计算权重
            weighted_results = dynamic_memory_weighting_capability.calculate_memory_weights_batch(
                memories_list, 
                context=context
            )
            
            # 添加权重信息到返回结果
            insights.append(f"计算了 {len(weighted_results)} 个记忆项的权重")
    except Exception as e:
        insights.append(f"权重计算过程中出现错误: {str(e)}")
    
    success = len(recommended_indexes) == 0  # 如果没有推荐的索引，则认为协同效果良好
    
    return {
        'success': success,
        'synergy_score': max(0.0, 1.0 - len(recommended_indexes) * 0.2),
        'existing_indexes': index_names,
        'recommended_indexes': recommended_indexes,
        'actual_queries': actual_queries,
        'insights': insights + [
            f"协同效果评分: {max(0.0, 1.0 - len(recommended_indexes) * 0.2):.2f}",
            f"建议创建 {len(recommended_indexes)} 个新索引以优化查询性能"
        ],
        'facts': facts,
        'memories': memories
    }

def _suggest_optimizations(cursor, query_patterns: List[str], dynamic_memory_weighting_capability) -> Dict[str, Any]:
    """建议SQLite索引优化方案"""
    insights = []
    facts = []
    memories = []
    
    # 分析查询模式中的列使用情况
    column_usage = {}
    table_columns = [col[1] for col in cursor.execute("PRAGMA table_info(memory_embeddings)").fetchall()]
    
    for pattern in query_patterns:
        for column in table_columns:
            if column in pattern:
                column_usage[column] = column_usage.get(column, 0) + 1
    
    # 生成优化建议
    optimization_suggestions = []
    existing_indexes = [idx[1] for idx in cursor.execute("PRAGMA index_list(memory_embeddings)").fetchall()]
    
    for column, usage_count in column_usage.items():
        # 检查是否已有索引
        has_index = any(column in idx_name for idx_name in existing_indexes)
        if not has_index and usage_count > 0:
            optimization_suggestions.append({
                'column': column,
                'usage_count': usage_count,
                'suggestion': f'CREATE INDEX idx_{column} ON memory_embeddings({column})'
            })
    
    # 使用动态记忆权重能力优化建议
    try:
        # 获取当前记忆数据
        cursor.execute("SELECT memory_id, content_text, timestamp FROM memory_embeddings LIMIT 100")
        memory_data = cursor.fetchall()
        if memory_data:
            memories_list = []
            for row in memory_data:
                memory_item = {
                    'memory_id': row[0],
                    'content_text': row[1],
                    'timestamp': row[2]
                }
                memories_list.append(memory_item)
            
            # 计算权重并建议基于权重的索引
            weighted_results = dynamic_memory_weighting_capability.calculate_memory_weights_batch(
                memories_list
            )
            
            # 基于权重信息生成额外建议
            high_weight_items = [item for item in weighted_results if item.get('weight', 0) > 0.7]
            if high_weight_items:
                insights.append(f"识别出 {len(high_weight_items)} 个高权重记忆项目，建议优先索引相关字段")
    except Exception as e:
        insights.append(f"权重计算过程中出现错误: {str(e)}")
    
    return {
        'success': True,
        'optimization_suggestions': optimization_suggestions,
        'insights': insights + [
            f"分析了 {len(query_patterns)} 个查询模式",
            f"识别出 {len(column_usage)} 个常用列",
            f"生成了 {len(optimization_suggestions)} 个索引优化建议"
        ],
        'facts': facts,
        'memories': memories
    }

def _benchmark_performance(cursor, query_patterns: List[str], conn) -> Dict[str, Any]:
    """执行性能基准测试"""
    insights = []
    facts = []
    memories = []
    
    benchmark_results = []
    
    # 执行每个查询并测量时间
    for pattern in query_patterns[:3]:  # 限制查询数量
        try:
            start_time = time.time()
            cursor.execute(pattern)
            result = cursor.fetchall()
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            benchmark_results.append({
                'query': pattern,
                'execution_time_ms': execution_time,
                'rows_returned': len(result)
            })
        except Exception as e:
            benchmark_results.append({
                'query': pattern,
                'execution_time_ms': -1,
                'error': str(e)
            })
    
    # 计算平均执行时间
    valid_times = [r['execution_time_ms'] for r in benchmark_results if r['execution_time_ms'] > 0]
    avg_time = sum(valid_times) / len(valid_times) if valid_times else 0
    
    return {
        'success': True,
        'benchmark_results': benchmark_results,
        'average_execution_time_ms': avg_time,
        'insights': insights + [
            f"执行了 {len([r for r in benchmark_results if r['execution_time_ms'] > 0])} 个查询的基准测试",
            f"平均执行时间: {avg_time:.2f}ms"
        ],
        'facts': facts,
        'memories': memories
    }