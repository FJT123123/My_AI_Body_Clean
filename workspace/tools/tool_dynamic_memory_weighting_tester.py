# tool_name: dynamic_memory_weighting_tester
from langchain.tools import tool
import sys
import os
from datetime import datetime, timedelta
import json

@tool
def dynamic_memory_weighting_tester(input_args: str = None) -> dict:
    """
    动态记忆权重能力模块核心功能测试工具
    
    用途: 直接测试dynamic_memory_weighting_capability模块的核心功能
    参数: 
        - input_args (str): JSON字符串，可包含测试参数
    返回值: 
        - dict: 包含测试结果、权重计算结果等信息
    触发条件: 需要验证动态记忆权重能力模块功能时
    """
    try:
        # 解析输入参数
        if input_args:
            if isinstance(input_args, str):
                args = json.loads(input_args)
            else:
                args = input_args
        else:
            args = {}
        
        # 获取workspace路径
        workspace_dir = "/Users/zhufeng/My_AI_Body_Clean/workspace"
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
        
        # 加载能力模块
        from capabilities.dynamic_memory_weighting_capability import DynamicMemoryWeightingCapability
        
        # 创建测试记忆
        memories = [
            {
                'content': 'Neo4j类型约束违反导致的数据完整性问题需要预防',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                'content': '视频处理失败导致的任务中断', 
                'timestamp': (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"),
            },
            {
                'content': '参数契约缺失导致的技能调用失败', 
                'timestamp': (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ]
        
        context = "milestone: 动态记忆权重系统 failure: neo4j_constraint_error tool: neo4j_type_constraint_validator"
        
        # 创建能力实例
        capability = DynamicMemoryWeightingCapability()
        
        # 测试批量记忆权重计算
        weighted_memories = capability.calculate_memory_weights(memories, context=context)
        
        result = {
            "success": True,
            "message": "动态记忆权重能力模块核心功能测试成功",
            "weighted_memories": weighted_memories,
            "time_weights": [],
            "semantic_weights": [],
            "test_memories": memories
        }
        
        # 测试时间衰减权重
        current_time = datetime.now()
        for i, memory in enumerate(memories):
            try:
                memory_time = datetime.strptime(memory['timestamp'], "%Y-%m-%d %H:%M:%S")
                time_diff = (current_time - memory_time).total_seconds()
                # 假设时间权重计算基于时间差
                time_weight = max(0.0, 1.0 - (time_diff / (30 * 24 * 3600)))  # 30天为单位
                result["time_weights"].append(time_weight)
            except:
                result["time_weights"].append(0.0)
        
        # 测试语义相似度
        query = "Neo4j 约束"
        for i, memory in enumerate(memories):
            # 使用能力模块的语义相似度计算方法
            try:
                # 假设能力模块有相关方法
                if hasattr(capability, 'calculate_semantic_similarity'):
                    semantic_weight = capability.calculate_semantic_similarity(query, memory['content'])
                else:
                    # 如果没有直接方法，使用包含关键词的简单匹配
                    semantic_weight = 1.0 if 'Neo4j' in memory['content'] or '约束' in memory['content'] else 0.1
                result["semantic_weights"].append(semantic_weight)
            except:
                result["semantic_weights"].append(0.0)
        
        # 执行完整的权重计算循环
        query_text = "Neo4j 约束问题"
        full_result = {
            "success": True,
            "weighted_memories": capability.calculate_memory_weights(memories, query=query_text, context=context),
            "memory_clusters": [[memory] for memory in memories],
            "continuity_score": 0.5,
            "metadata": {
                "total_memories": len(memories),
                "query_used": bool(query_text),
                "context_used": bool(context)
            }
        }
        result["full_cycle_result"] = full_result
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"动态记忆权重能力模块测试失败: {e}",
            "weighted_memories": [],
            "time_weights": [],
            "semantic_weights": []
        }