# tool_name: dynamic_memory_chunk_index_optimizer
from typing import Dict, Any, List, Optional
import json
import sqlite3
from datetime import datetime
import logging
from langchain.tools import tool

def load_capability_module(capability_name: str):
    """Runtime capability loader"""
    import importlib
    return importlib.import_module(f"openclaw_continuity.capabilities.{capability_name}")

def calculate_memory_weights_batch(memories, context=None, current_time=None, time_decay_rate=0.1):
    """Helper to calculate memory weights"""
    capability = load_capability_module("dynamic_memory_weighting_capability")
    return capability.calculate_memory_weights_batch(memories, context, current_time, time_decay_rate)

def analyze_memory_weights_distribution(db_path: str) -> Dict[str, Any]:
    """Analyze the current memory weights distribution in memory_chunks table"""
    conn = sqlite3.connect(db_path)
    try:
        # Get memory weights statistics
        query = """
        SELECT 
            AVG(importance) as avg_importance,
            MIN(importance) as min_importance,
            MAX(importance) as max_importance,
            COUNT(*) as total_memories,
            COUNT(CASE WHEN importance > 0.8 THEN 1 END) as high_importance,
            COUNT(CASE WHEN importance BETWEEN 0.5 AND 0.8 THEN 1 END) as medium_importance,
            COUNT(CASE WHEN importance < 0.5 THEN 1 END) as low_importance
        FROM memory_chunks
        """
        cursor = conn.execute(query)
        stats = cursor.fetchone()
        
        return {
            "avg_importance": stats[0],
            "min_importance": stats[1],
            "max_importance": stats[2],
            "total_memories": stats[3],
            "high_importance": stats[4],
            "medium_importance": stats[5],
            "low_importance": stats[6],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_current_indexes(db_path: str) -> List[Dict[str, Any]]:
    """Get current indexes on memory_chunks table"""
    conn = sqlite3.connect(db_path)
    try:
        # Get indexes for memory_chunks table
        cursor = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='memory_chunks'")
        indexes = cursor.fetchall()
        
        return [{"name": idx[0], "sql": idx[1]} for idx in indexes]
    except Exception as e:
        raise e
    finally:
        conn.close()

def analyze_query_performance(db_path: str) -> Dict[str, Any]:
    """Analyze current query performance for memory_chunks table"""
    conn = sqlite3.connect(db_path)
    try:
        # Analyze query patterns based on importance weights
        query_analysis = """
        SELECT 
            importance,
            COUNT(*) as count,
            AVG(LENGTH(content)) as avg_content_length,
            AVG(LENGTH(metadata)) as avg_metadata_length
        FROM memory_chunks
        GROUP BY importance
        ORDER BY importance DESC
        LIMIT 10
        """
        cursor = conn.execute(query_analysis)
        results = cursor.fetchall()
        
        performance_metrics = []
        for row in results:
            performance_metrics.append({
                "importance": row[0],
                "count": row[1],
                "avg_content_length": row[2],
                "avg_metadata_length": row[3]
            })
        
        return {
            "query_performance": performance_metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise e
    finally:
        conn.close()

def recommend_indexes(db_path: str) -> Dict[str, Any]:
    """Recommend optimal indexes based on memory weights and query patterns"""
    # Analyze current state
    weights_stats = analyze_memory_weights_distribution(db_path)
    current_indexes = get_current_indexes(db_path)
    
    recommendations = []
    
    # Recommend index on importance for weighted queries
    importance_index_exists = any("importance" in idx["sql"] for idx in current_indexes)
    if not importance_index_exists:
        recommendations.append({
            "type": "importance_weight",
            "sql": "CREATE INDEX idx_memory_chunks_importance ON memory_chunks(importance DESC)",
            "reason": "Optimize queries filtering by importance weight",
            "impact": "High"
        })
    
    # Recommend composite index for common access patterns
    content_importance_index_exists = any("content" in idx["sql"] and "importance" in idx["sql"] for idx in current_indexes)
    if not content_importance_index_exists and weights_stats["total_memories"] > 1000:
        recommendations.append({
            "type": "content_importance",
            "sql": "CREATE INDEX idx_memory_chunks_content_importance ON memory_chunks(content, importance DESC)",
            "reason": "Optimize content search with importance weighting",
            "impact": "Medium"
        })
    
    # Recommend timestamp + importance for temporal queries
    timestamp_importance_index_exists = any("timestamp" in idx["sql"] and "importance" in idx["sql"] for idx in current_indexes)
    if not timestamp_importance_index_exists:
        recommendations.append({
            "type": "temporal_importance",
            "sql": "CREATE INDEX idx_memory_chunks_timestamp_importance ON memory_chunks(timestamp DESC, importance DESC)",
            "reason": "Optimize temporal queries with importance weighting",
            "impact": "Medium"
        })
    
    return {
        "recommendations": recommendations,
        "current_indexes": current_indexes,
        "weights_analysis": weights_stats,
        "timestamp": datetime.now().isoformat()
    }

def apply_index_recommendations(db_path: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply the recommended indexes to the database"""
    conn = sqlite3.connect(db_path)
    applied_indexes = []
    
    try:
        for rec in recommendations:
            try:
                conn.execute(rec["sql"])
                conn.commit()
                applied_indexes.append({
                    "index_name": f"idx_memory_chunks_{rec['type']}",
                    "sql": rec["sql"],
                    "status": "applied"
                })
            except sqlite3.Error as e:
                applied_indexes.append({
                    "index_name": f"idx_memory_chunks_{rec['type']}",
                    "sql": rec["sql"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "applied_indexes": applied_indexes,
            "total_applied": len([idx for idx in applied_indexes if idx["status"] == "applied"]),
            "total_failed": len([idx for idx in applied_indexes if idx["status"] == "failed"]),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise e
    finally:
        conn.close()

@tool
def dynamic_memory_chunk_index_optimizer(input_args: str) -> Dict[str, Any]:
    """
    动态记忆权重SQLite索引优化工具：专门针对memory_chunks表的智能索引推荐和性能验证
    该工具基于memory_chunks表的真实结构（包含importance权重列）进行智能分析，
    为动态记忆权重系统提供最优的SQLite索引策略

    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action: 操作类型 ("analyze", "recommend", "apply", "full")
            - db_path: SQLite数据库路径 (可选，默认为"memory.db")
            - memory_weights: 可选的记忆权重数据 (用于apply操作)

    Returns:
        Dict[str, Any]: 包含分析结果、推荐索引、应用状态的JSON可序列化字典
    """
    try:
        args = json.loads(input_args)
        action = args.get("action", "full")
        db_path = args.get("db_path", "memory.db")
        
        if action == "analyze":
            # Analyze current memory weights and performance
            weights_stats = analyze_memory_weights_distribution(db_path)
            perf_metrics = analyze_query_performance(db_path)
            current_indexes = get_current_indexes(db_path)
            
            return {
                "action": "analyze",
                "status": "success",
                "weights_analysis": weights_stats,
                "performance_metrics": perf_metrics,
                "current_indexes": current_indexes,
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "recommend":
            # Recommend optimal indexes based on memory weights
            recommendations = recommend_indexes(db_path)
            return {
                "action": "recommend",
                "status": "success",
                "recommendations": recommendations["recommendations"],
                "current_indexes": recommendations["current_indexes"],
                "weights_analysis": recommendations["weights_analysis"],
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "apply":
            # Apply recommended indexes to database
            recommendations = recommend_indexes(db_path)
            apply_result = apply_index_recommendations(db_path, recommendations["recommendations"])
            
            return {
                "action": "apply",
                "status": "success",
                "apply_result": apply_result,
                "recommendations_applied": recommendations["recommendations"],
                "timestamp": datetime.now().isoformat()
            }
        
        elif action == "full":
            # Complete analysis -> recommend -> apply cycle
            weights_stats = analyze_memory_weights_distribution(db_path)
            current_indexes = get_current_indexes(db_path)
            recommendations = recommend_indexes(db_path)
            apply_result = apply_index_recommendations(db_path, recommendations["recommendations"])
            
            return {
                "action": "full",
                "status": "success",
                "weights_analysis": weights_stats,
                "current_indexes": current_indexes,
                "recommendations": recommendations["recommendations"],
                "apply_result": apply_result,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "supported_actions": ["analyze", "recommend", "apply", "full"],
                "timestamp": datetime.now().isoformat()
            }
    
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"Invalid JSON input: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }