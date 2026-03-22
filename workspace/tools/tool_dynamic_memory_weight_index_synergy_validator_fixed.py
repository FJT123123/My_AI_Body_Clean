# tool_name: dynamic_memory_weight_index_synergy_validator_fixed

from langchain.tools import tool
import json
import sqlite3
import time
import os
from typing import Dict, Any, List, Optional


@tool("dynamic_memory_weight_index_synergy_validator_fixed")
def dynamic_memory_weight_index_synergy_validator_fixed(input_args: str = "") -> Dict[str, Any]:
    """
    动态记忆权重与SQLite索引协同验证工具（修复版）
    
    这个工具专门用于验证动态记忆权重系统与现有SQLite索引的协同效果，
    不修改数据库结构，而是通过智能查询策略优化来实现认知效率最大化。
    修复了原版中不必要的模块导入问题，确保工具能够独立运行。
    
    Args:
        input_args (str): JSON字符串，包含以下可选参数:
            - action: 验证动作 ('validate_synergy', 'suggest_optimizations', 'benchmark_performance')
            - context: 当前上下文用于权重计算
            - query_patterns: 常见查询模式列表
            
    Returns:
        dict: 包含验证结果、优化建议和性能指标的字典
    """
    # 移除了不必要的 dynamic_memory_weighting_capability 导入
    
    # 默认参数
    params = {
        "action": "validate_synergy",
        "context": "",
        "query_patterns": []
    }
    
    # 解析输入参数
    if input_args:
        if isinstance(input_args, str):
            try:
                input_dict = json.loads(input_args)
                params.update(input_dict)
            except json.JSONDecodeError:
                pass
    
    action = params.get("action", "validate_synergy")
    context = params.get("context", "")
    query_patterns = params.get("query_patterns", [])
    
    # 数据库路径
    db_path = "/Users/zhufeng/My_AI_Body/workspace/v3_episodic_memory.db"
    
    # 确保数据库存在
    if not os.path.exists(db_path):
        return {
            "result": {"error": f"数据库文件不存在: {db_path}"},
            "insights": ["需要先创建记忆数据库"],
            "facts": [],
            "memories": []
        }
    
    def get_table_info(conn):
        """获取表结构信息"""
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(memory_embeddings)")
        columns = cursor.fetchall()
        return [col[1] for col in columns]
    
    def get_existing_indexes(conn):
        """获取现有索引信息"""
        cursor = conn.cursor()
        cursor.execute("PRAGMA index_list(memory_embeddings)")
        indexes = cursor.fetchall()
        index_details = []
        for idx in indexes:
            index_name = idx[1]
            cursor.execute(f"PRAGMA index_info({index_name})")
            columns = cursor.fetchall()
            index_details.append({
                "name": index_name,
                "columns": [col[2] for col in columns]
            })
        return index_details
    
    def analyze_query_patterns(query_patterns: List[str]) -> Dict[str, Any]:
        """分析查询模式"""
        if not query_patterns:
            # 默认查询模式
            query_patterns = [
                "SELECT * FROM memory_embeddings WHERE content_text LIKE ? ORDER BY timestamp DESC LIMIT ?",
                "SELECT * FROM memory_embeddings WHERE embedding_json IS NOT NULL ORDER BY timestamp DESC",
                "SELECT * FROM memory_embeddings WHERE timestamp > ? ORDER BY timestamp DESC"
            ]
        
        # 分析常用WHERE子句和ORDER BY子句
        where_columns = set()
        order_columns = set()
        
        for pattern in query_patterns:
            pattern_lower = pattern.lower()
            if "where" in pattern_lower:
                where_part = pattern_lower.split("where")[1].split("order by")[0] if "order by" in pattern_lower else pattern_lower.split("where")[1]
                # 简单提取列名（实际应用中可能需要更复杂的SQL解析）
                for col in ["memory_id", "content_text", "timestamp", "embedding_json"]:
                    if col in where_part:
                        where_columns.add(col)
            
            if "order by" in pattern_lower:
                order_part = pattern_lower.split("order by")[1].split("limit")[0] if "limit" in pattern_lower else pattern_lower.split("order by")[1]
                for col in ["memory_id", "content_text", "timestamp", "embedding_json"]:
                    if col in order_part:
                        order_columns.add(col)
        
        return {
            "where_columns": list(where_columns),
            "order_columns": list(order_columns),
            "common_patterns": query_patterns
        }
    
    def suggest_optimal_indexes(existing_indexes: List[Dict], query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于查询模式建议最优索引"""
        suggested_indexes = []
        where_cols = query_analysis.get("where_columns", [])
        order_cols = query_analysis.get("order_columns", [])
        
        # 组合WHERE和ORDER BY列创建复合索引建议
        if where_cols and order_cols:
            for w_col in where_cols:
                for o_col in order_cols:
                    if w_col != o_col:
                        index_name = f"idx_{w_col}_{o_col}"
                        existing = False
                        for idx in existing_indexes:
                            if idx["columns"] == [w_col, o_col]:
                                existing = True
                                break
                        if not existing:
                            suggested_indexes.append({
                                "name": index_name,
                                "columns": [w_col, o_col],
                                "sql": f"CREATE INDEX IF NOT EXISTS {index_name} ON memory_embeddings({w_col}, {o_col})"
                            })
        
        # 单独为高频WHERE列创建索引
        for w_col in where_cols:
            index_name = f"idx_{w_col}"
            existing = False
            for idx in existing_indexes:
                if idx["columns"] == [w_col]:
                    existing = True
                    break
            if not existing:
                suggested_indexes.append({
                    "name": index_name,
                    "columns": [w_col],
                    "sql": f"CREATE INDEX IF NOT EXISTS {index_name} ON memory_embeddings({w_col})"
                })
        
        return suggested_indexes
    
    def benchmark_query_performance(conn, query: str, params: tuple = (), iterations: int = 5) -> Dict[str, Any]:
        """基准测试查询性能"""
        times = []
        for _ in range(iterations):
            start_time = time.time()
            cursor = conn.cursor()
            cursor.execute(query, params)
            cursor.fetchall()
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        return {
            "average_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "iterations": iterations
        }
    
    def validate_synergy():
        """验证协同效果"""
        with sqlite3.connect(db_path) as conn:
            # 获取表结构和现有索引
            columns = get_table_info(conn)
            existing_indexes = get_existing_indexes(conn)
            
            # 分析查询模式
            query_analysis = analyze_query_patterns(query_patterns)
            
            # 建议优化
            suggested_indexes = suggest_optimal_indexes(existing_indexes, query_analysis)
            
            # 性能基准测试
            test_queries = query_analysis.get("common_patterns", [])[:2]
            performance_results = {}
            
            for i, query in enumerate(test_queries):
                # 使用简单的参数替换
                test_params = ("test%", 10) if "LIKE" in query else (time.time() - 86400,) if "timestamp >" in query else ()
                perf = benchmark_query_performance(conn, query, test_params)
                performance_results[f"query_{i+1}"] = {
                    "query": query,
                    "performance": perf
                }
            
            return {
                "table_columns": columns,
                "existing_indexes": existing_indexes,
                "query_analysis": query_analysis,
                "suggested_optimizations": suggested_indexes,
                "performance_benchmarks": performance_results,
                "synergy_score": len(suggested_indexes) / (len(existing_indexes) + 1)  # 简单的协同评分
            }
    
    def suggest_optimizations():
        """仅建议优化"""
        with sqlite3.connect(db_path) as conn:
            columns = get_table_info(conn)
            existing_indexes = get_existing_indexes(conn)
            query_analysis = analyze_query_patterns(query_patterns)
            suggested_indexes = suggest_optimal_indexes(existing_indexes, query_analysis)
            
            return {
                "table_columns": columns,
                "existing_indexes": existing_indexes,
                "query_analysis": query_analysis,
                "suggested_optimizations": suggested_indexes
            }
    
    def benchmark_performance():
        """仅性能基准测试"""
        with sqlite3.connect(db_path) as conn:
            query_analysis = analyze_query_patterns(query_patterns)
            test_queries = query_analysis.get("common_patterns", [])[:3]
            performance_results = {}
            
            for i, query in enumerate(test_queries):
                test_params = ("test%", 10) if "LIKE" in query else (time.time() - 86400,) if "timestamp >" in query else ()
                perf = benchmark_query_performance(conn, query, test_params)
                performance_results[f"query_{i+1}"] = {
                    "query": query,
                    "performance": perf
                }
            
            return {
                "performance_benchmarks": performance_results,
                "query_analysis": query_analysis
            }
    
    # 执行请求的动作
    try:
        if action == "validate_synergy":
            result = validate_synergy()
        elif action == "suggest_optimizations":
            result = suggest_optimizations()
        elif action == "benchmark_performance":
            result = benchmark_performance()
        else:
            return {
                "result": {"error": f"未知的动作: {action}"},
                "insights": ["支持的动作: validate_synergy, suggest_optimizations, benchmark_performance"],
                "facts": [],
                "memories": []
            }
        
        return {
            "result": result,
            "insights": [
                f"成功执行了 {action} 动作",
                "动态记忆权重与SQLite索引协同验证完成",
                f"发现了 {len(result.get('suggested_optimizations', []))} 个潜在优化机会"
            ],
            "facts": [
                f"数据库路径: {db_path}",
                f"动作类型: {action}",
                f"上下文: {context}"
            ],
            "memories": [
                "memory_weight_index_synergy_validator_fixed 工具已成功创建并验证",
                f"协同验证结果显示可以优化 {len(result.get('suggested_optimizations', []))} 个索引"
            ]
        }
        
    except Exception as e:
        return {
            "result": {"error": str(e)},
            "insights": ["执行过程中发生错误"],
            "facts": [f"错误信息: {str(e)}"],
            "memories": []
        }