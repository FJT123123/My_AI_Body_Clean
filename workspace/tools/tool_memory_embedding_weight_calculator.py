# tool_name: memory_embedding_weight_calculator
from langchain.tools import tool
import json
import os
import sqlite3

@tool
def memory_embedding_weight_calculator(input_args=None):
    """
    获取记忆嵌入并计算动态重要性权重的工具
    
    这个工具使用 dynamic_memory_weighting_capability 来计算重要性权重，
    无需修改数据库结构，安全地实现认知价值与物理存储的统一。
    
    Args:
        input_args: 可选的输入参数，可以是字典或JSON字符串
                   - limit: 限制返回的记忆数量，默认为20
                   - memory_db_path: 数据库路径，可选
    
    Returns:
        dict: 包含结果、洞察、事实和记忆的字典
    """
    import json
    import os
    import sqlite3
    
    # 解析输入参数
    if input_args is None:
        input_args = {}
    elif isinstance(input_args, str):
        try:
            input_args = json.loads(input_args)
        except json.JSONDecodeError:
            return {
                "result": {"success": False, "error": "输入参数不是有效的JSON字符串"},
                "insights": ["输入参数格式错误，无法解析JSON"],
                "facts": [],
                "memories": []
            }
    
    # 设置默认参数
    limit = input_args.get("limit", 20)
    db_path = input_args.get("memory_db_path")
    
    # 如果没有提供数据库路径，使用默认路径
    if not db_path:
        db_path = os.path.join(os.path.dirname(__file__), '..', 'v3_episodic_memory.db')
    
    # 验证数据库文件存在
    if not os.path.exists(db_path):
        return {
            "result": {"success": False, "error": f"数据库文件不存在: {db_path}"},
            "insights": [f"找不到数据库文件: {db_path}"],
            "facts": [],
            "memories": []
        }
    
    try:
        # 从数据库获取记忆嵌入数据
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, embedding, created_at, source_type, embedding_source 
            FROM memory_embeddings 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                "result": {"success": True, "message": "没有找到记忆嵌入数据", "embeddings_count": 0},
                "insights": ["数据库中没有记忆嵌入数据"],
                "facts": [["memory_embeddings", "count", "0"]],
                "memories": []
            }
        
        # 动态加载 capability
        capability_module = __import__('workspace.capabilities.dynamic_memory_weighting_capability', fromlist=['DynamicMemoryWeightingCapability'])
        DynamicMemoryWeightingCapability = getattr(capability_module, 'DynamicMemoryWeightingCapability')
        
        # 初始化动态记忆权重能力
        weighting_capability = DynamicMemoryWeightingCapability(memory_db_path=db_path)
        
        # 准备记忆数据用于权重计算
        memories_for_weighting = []
        for row in rows:
            embedding_id, embedding, created_at, source_type, embedding_source = row
            memories_for_weighting.append({
                "id": embedding_id,
                "content": embedding_source,
                "timestamp": created_at,
                "source": source_type
            })
        
        # 使用 dynamic_memory_weighting_capability 计算权重
        weights_result = weighting_capability.calculate_memory_weights_batch(memories_for_weighting)
        
        # 组合结果
        embeddings_with_weights = []
        for i, row in enumerate(rows):
            embedding_id, embedding, created_at, source_type, embedding_source = row
            weight = weights_result.get('weights', [])[i] if i < len(weights_result.get('weights', [])) else 0.5
            
            embeddings_with_weights.append({
                "id": embedding_id,
                "embedding": embedding,
                "created_at": created_at,
                "source_type": source_type,
                "embedding_source": embedding_source,
                "importance_weight": weight
            })
        
        result = {
            "success": True,
            "message": f"成功获取 {len(embeddings_with_weights)} 个带重要性权重的记忆嵌入",
            "embeddings_count": len(embeddings_with_weights),
            "embeddings": embeddings_with_weights
        }
        
        insights = [
            "成功使用 dynamic_memory_weighting_capability 实现记忆嵌入重要性权重计算",
            f"为 {len(embeddings_with_weights)} 个记忆嵌入计算了重要性权重",
            "通过现有 capability 安全地完善了认知架构"
        ]
        
        facts = [
            ["memory_embeddings", "dynamic_importance_calculation", "implemented"],
            ["cognitive_architecture", "value_representation", "enhanced"],
            ["capability_usage", "dynamic_memory_weighting", "successful"]
        ]
        
        memories = [{
            "event_type": "cognitive_architecture_improved", 
            "content": "通过 dynamic_memory_weighting_capability 实现了记忆嵌入的重要性权重计算，完善了认知架构"
        }]
        
        return {
            "result": result,
            "insights": insights,
            "facts": facts,
            "memories": memories
        }
        
    except Exception as e:
        return {
            "result": {"success": False, "error": str(e)},
            "insights": [f"操作失败: {str(e)}"],
            "facts": [],
            "memories": []
        }