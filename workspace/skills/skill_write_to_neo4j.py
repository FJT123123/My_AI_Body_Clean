import os
import json

def main(input_args):
    """
    直接写入数据到 Neo4j 数据库
    
    Args:
        input_args: 包含 'input' 键的字典，其值为 JSON 字符串或字典
        
    Returns:
        dict: 包含操作结果的字典
    """
    try:
        # 从 input_args 中提取实际输入
        actual_input = input_args.get('input', '') if isinstance(input_args, dict) else input_args
        
        # 解析实际输入
        if actual_input:
            if isinstance(actual_input, str):
                # 如果是字符串，尝试解析为 JSON
                if actual_input.strip():
                    params = json.loads(actual_input)
                else:
                    params = {}
            else:
                # 如果已经是字典，直接使用
                params = actual_input
            query = params.get("query")
            parameters = params.get("parameters", {})
        else:
            # 默认示例
            query = "CREATE (p:TestNode {name: 'Default Test', created: timestamp()}) RETURN p"
            parameters = {}
        
        if not query or (isinstance(query, str) and not query.strip()):
            return {
                "success": False,
                "error": "Query is empty",
                "message": "Query cannot be empty"
            }
        
        # 使用 Neo4j 驱动直接连接
        import neo4j
        
        # 获取连接信息
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            result = session.run(query, parameters)
            # 获取所有结果行
            records = []
            for record in result:
                record_dict = {}
                for key in record.keys():
                    record_dict[key] = record[key]
                records.append(record_dict)
            summary = result.consume()
            
            return {
                "success": True,
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created,
                "properties_set": summary.counters.properties_set,
                "records": records,
                "message": f"Successfully executed query"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to write to Neo4j: {str(e)}"
        }