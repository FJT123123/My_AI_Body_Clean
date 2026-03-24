# tool_name: adaptive_memory_index_optimizer
from langchain.tools import tool
import json
import sqlite3
import time
from typing import Dict, Any, List, Optional

def get_memory_db_connection():
    """获取记忆数据库连接"""
    import os
    from pathlib import Path
    
    # 尝试获取记忆数据库路径
    memory_db_path = os.getenv("MEMORY_DB_PATH", str(Path.home() / ".openclaw" / "memory.db"))
    if not os.path.exists(memory_db_path):
        # 如果不存在，尝试创建
        os.makedirs(os.path.dirname(memory_db_path), exist_ok=True)
        conn = sqlite3.connect(memory_db_path)
        # 初始化基本表结构
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                content TEXT,
                embedding_vector TEXT,
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    return sqlite3.connect(memory_db_path)

def analyze_memory_query_patterns(conn) -> Dict[str, Any]:
    """分析记忆查询模式"""
    try:
        # 获取当前索引信息
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        existing_indexes = cursor.fetchall()
        
        # 分析表结构
        cursor.execute("PRAGMA table_info(memories)")
        table_info = cursor.fetchall()
        
        # 获取内存权重分布统计
        weight_stats = cursor.execute("SELECT AVG(weight), MAX(weight), MIN(weight) FROM memories").fetchone()
        
        # 分析查询频率最高的列组合
        try:
            # 检查是否存在查询日志表（如果有的话）
            query_stats = cursor.execute("""
                SELECT COUNT(*) as cnt FROM memories 
                WHERE weight > 0.5 
                GROUP BY created_at, last_accessed
            """).fetchall()
        except:
            query_stats = []
        
        return {
            "existing_indexes": [{"name": idx[0], "definition": idx[1]} for idx in existing_indexes],
            "table_columns": [col[1] for col in table_info],
            "weight_stats": {
                "avg_weight": weight_stats[0] or 0,
                "max_weight": weight_stats[1] or 0,
                "min_weight": weight_stats[2] or 0
            },
            "query_patterns": len(query_stats)
        }
    except Exception as e:
        return {"error": f"无法分析查询模式: {str(e)}"}

def get_optimal_index_recommendations(pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """基于查询模式生成索引建议"""
    recommendations = []
    
    if "error" in pattern_analysis:
        return recommendations
    
    # 如果权重列查询频繁，建议创建权重索引
    if pattern_analysis["weight_stats"]["avg_weight"] > 0.1:
        recommendations.append({
            "index_name": "idx_memories_weight",
            "columns": ["weight"],
            "reason": "高权重查询频率，建议按权重排序优化"
        })
    
    # 如果内容和权重组合查询频繁，建议创建复合索引
    table_columns = pattern_analysis["table_columns"]
    if "content" in table_columns and "weight" in table_columns:
        recommendations.append({
            "index_name": "idx_memories_content_weight",
            "columns": ["content", "weight"],
            "reason": "内容检索与权重过滤组合查询优化"
        })
    
    # 如果嵌入向量和权重组合查询频繁，建议创建复合索引
    if "embedding_vector" in table_columns and "weight" in table_columns:
        recommendations.append({
            "index_name": "idx_memories_embedding_weight",
            "columns": ["embedding_vector", "weight"],
            "reason": "嵌入向量检索与权重过滤组合查询优化"
        })
    
    # 如果按时间排序频繁，建议创建时间索引
    if "created_at" in table_columns:
        recommendations.append({
            "index_name": "idx_memories_created_at",
            "columns": ["created_at"],
            "reason": "按时间排序查询优化"
        })
    
    # 如果按最后访问时间排序频繁，建议创建索引
    if "last_accessed" in table_columns:
        recommendations.append({
            "index_name": "idx_memories_last_accessed",
            "columns": ["last_accessed"],
            "reason": "按最后访问时间排序查询优化"
        })
    
    return recommendations

def validate_index_performance(conn, index_sql: str) -> Dict[str, Any]:
    """验证索引性能影响"""
    try:
        cursor = conn.cursor()
        
        # 测试查询性能前的时间
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM memories WHERE weight > 0.5")
        baseline_time = time.time() - start_time
        
        # 临时创建索引进行测试
        temp_index_name = f"temp_test_idx_{int(time.time())}"
        temp_index_sql = index_sql.replace("CREATE INDEX", f"CREATE INDEX {temp_index_name}")
        
        cursor.execute(temp_index_sql)
        conn.commit()
        
        # 测试查询性能后的时间
        start_time = time.time()
        cursor.execute("SELECT COUNT(*) FROM memories WHERE weight > 0.5")
        optimized_time = time.time() - start_time
        
        # 删除临时索引
        cursor.execute(f"DROP INDEX IF EXISTS {temp_index_name}")
        conn.commit()
        
        return {
            "baseline_time": baseline_time,
            "optimized_time": optimized_time,
            "performance_improvement": baseline_time > optimized_time,
            "improvement_ratio": baseline_time / (optimized_time if optimized_time > 0 else baseline_time)
        }
    except Exception as e:
        return {"error": f"索引性能验证失败: {str(e)}"}

@tool
def adaptive_memory_index_optimizer(input_args: str) -> Dict[str, Any]:
    """
    自适应记忆索引优化工具：基于动态记忆权重验证结果，智能分析和优化SQLite索引
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - action: 操作类型 ("analyze", "recommend", "apply", "full")
            - test_performance: 是否测试索引性能提升 (默认True)
            - target_tables: 目标表列表 (默认["memories"])
    
    Returns:
        Dict[str, Any]: 包含分析结果、建议和优化状态的字典
    """
    try:
        # 解析输入参数
        args = json.loads(input_args) if isinstance(input_args, str) else input_args
        action = args.get("action", "full")
        test_performance = args.get("test_performance", True)
        target_tables = args.get("target_tables", ["memories"])
        
        # 获取数据库连接
        conn = get_memory_db_connection()
        
        result = {
            "action": action,
            "timestamp": time.time(),
            "status": "success"
        }
        
        if action in ["analyze", "full", "recommend"]:
            # 分析当前查询模式
            pattern_analysis = analyze_memory_query_patterns(conn)
            result["pattern_analysis"] = pattern_analysis
            
            if action in ["recommend", "full"]:
                # 生成索引建议
                recommendations = get_optimal_index_recommendations(pattern_analysis)
                result["recommendations"] = recommendations
                
                if test_performance and recommendations:
                    # 测试建议索引的性能影响
                    performance_tests = []
                    for rec in recommendations:
                        columns = rec["columns"]
                        index_sql = f"CREATE INDEX {rec['index_name']} ON memories ({','.join(columns)})"
                        performance_result = validate_index_performance(conn, index_sql)
                        performance_tests.append({
                            "index_name": rec["index_name"],
                            "performance_test": performance_result
                        })
                    result["performance_tests"] = performance_tests
        
        if action == "apply" or (action == "full" and result.get("recommendations")):
            # 应用推荐的索引
            applied_indexes = []
            if "recommendations" in result:
                cursor = conn.cursor()
                for rec in result["recommendations"]:
                    try:
                        index_name = rec["index_name"]
                        columns = rec["columns"]
                        index_sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON memories ({','.join(columns)})"
                        cursor.execute(index_sql)
                        applied_indexes.append({
                            "index_name": index_name,
                            "status": "created",
                            "reason": rec["reason"]
                        })
                    except Exception as e:
                        applied_indexes.append({
                            "index_name": rec["index_name"],
                            "status": "failed",
                            "error": str(e)
                        })
                conn.commit()
            result["applied_indexes"] = applied_indexes
        
        conn.close()
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }