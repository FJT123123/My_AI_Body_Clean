import os
import json

def main(input_args):
    """
    执行Neo4j查询并返回结果
    
    Args:
        input_args: 查询语句字符串或包含query和parameters的字典
        
    Returns:
        包含查询结果的字典
    """
    try:
        # 处理输入参数 - input_args 可能是字典，包含 'input' 键
        actual_input = input_args
        if isinstance(input_args, dict) and 'input' in input_args:
            actual_input = input_args['input']
        
        # 处理实际输入
        if isinstance(actual_input, str) and actual_input.strip():
            # 如果是字符串，直接作为查询语句
            query = actual_input.strip()
            parameters = {}
        elif isinstance(actual_input, dict):
            # 如果是字典，提取query和parameters
            query = actual_input.get("query", "")
            parameters = actual_input.get("parameters", {})
        else:
            # 尝试解析为JSON
            try:
                if isinstance(actual_input, str):
                    parsed = json.loads(actual_input)
                    query = parsed.get("query", "")
                    parameters = parsed.get("parameters", {})
                else:
                    query = str(actual_input) if actual_input else ""
                    parameters = {}
            except (json.JSONDecodeError, TypeError):
                query = str(actual_input) if actual_input else ""
                parameters = {}
        
        if not query:
            return {
                "success": False,
                "error": "Missing query parameter",
                "message": "Query parameter is required"
            }
        
        # 导入neo4j驱动
        import neo4j
        
        # 获取连接信息
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        # 创建驱动并执行查询
        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            result = session.run(query, parameters)
            records = []
            
            # 收集所有记录
            for record in result:
                record_dict = {}
                for key in record.keys():
                    record_dict[key] = record[key]
                records.append(record_dict)
            
            summary = result.consume()
            
            return {
                "success": True,
                "records": records,
                "record_count": len(records),
                "summary": {
                    "nodes_created": summary.counters.nodes_created,
                    "relationships_created": summary.counters.relationships_created,
                    "properties_set": summary.counters.properties_set
                },
                "message": f"Successfully executed query and returned {len(records)} records"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to execute query: {str(e)}"
        }