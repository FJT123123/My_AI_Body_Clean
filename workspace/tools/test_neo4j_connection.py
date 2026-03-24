import os
import json

def test_neo4j_connection():
    """测试 Neo4j 连接"""
    try:
        import neo4j
        # 获取连接信息（假设已配置）
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            message = record["message"] if record else "No record returned"
            return {"success": True, "message": message}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = test_neo4j_connection()
    print(json.dumps(result, indent=2))