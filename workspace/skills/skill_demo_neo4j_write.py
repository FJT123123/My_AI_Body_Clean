def main(input_args):
    """演示如何使用 Neo4j 写入工具"""
    try:
        # neo4j_write 应该作为全局函数可用
        global neo4j_write
        
        # 创建示例节点
        person_query = """
        CREATE (p:Person {
            id: 'john_doe',
            name: 'John Doe',
            age: 30,
            email: 'john.doe@example.com'
        })
        RETURN p
        """
        person_result = neo4j_write(person_query)
        
        company_query = """
        CREATE (c:Company {
            id: 'acme_corp',
            name: 'ACME Corporation',
            industry: 'Technology'
        })
        RETURN c
        """
        company_result = neo4j_write(company_query)
        
        # 创建关系
        relationship_query = """
        MATCH (p:Person {id: 'john_doe'})
        MATCH (c:Company {id: 'acme_corp'})
        CREATE (p)-[r:WORKS_AT {
            since: '2020-01-01',
            position: 'Software Engineer'
        }]->(c)
        RETURN r
        """
        relationship_result = neo4j_write(relationship_query)
        
        return {
            "success": True,
            "person_creation": person_result,
            "company_creation": company_result,
            "relationship_creation": relationship_result,
            "message": "Successfully demonstrated Neo4j write operations"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to demonstrate Neo4j write operations: {str(e)}"
        }