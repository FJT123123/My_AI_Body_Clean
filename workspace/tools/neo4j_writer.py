import os
import json
from typing import Dict, Any, Optional

class Neo4jWriter:
    """Neo4j 数据库写入工具"""
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        初始化 Neo4j 连接
        
        Args:
            uri: Neo4j 数据库 URI (默认从环境变量 NEO4J_URI 获取)
            user: 用户名 (默认从环境变量 NEO4J_USER 获取)
            password: 密码 (默认从环境变量 NEO4J_PASSWORD 获取)
        """
        self.uri = uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.environ.get("NEO4J_USER", "neo4j")
        self.password = password or os.environ.get("NEO4J_PASSWORD", "password")
        
    def write_data(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        向 Neo4j 数据库写入数据
        
        Args:
            query: Cypher 查询语句
            parameters: 查询参数
            
        Returns:
            包含操作结果的字典
        """
        try:
            import neo4j
            driver = neo4j.GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            
            with driver.session() as session:
                result = session.run(query, parameters or {})
                summary = result.consume()
                
                return {
                    "success": True,
                    "records_affected": summary.counters.nodes_created + summary.counters.relationships_created,
                    "nodes_created": summary.counters.nodes_created,
                    "relationships_created": summary.counters.relationships_created,
                    "properties_set": summary.counters.properties_set,
                    "message": f"Successfully executed query: {query[:50]}..."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to execute query: {str(e)}"
            }
    
    def create_node(self, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建单个节点
        
        Args:
            label: 节点标签
            properties: 节点属性
            
        Returns:
            包含操作结果的字典
        """
        query = f"CREATE (n:`{label}` $properties) RETURN n"
        return self.write_data(query, {"properties": properties})
    
    def create_relationship(self, start_label: str, start_id: str, end_label: str, end_id: str, 
                          rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建关系
        
        Args:
            start_label: 起始节点标签
            start_id: 起始节点ID属性值
            end_label: 结束节点标签
            end_id: 结束节点ID属性值
            rel_type: 关系类型
            properties: 关系属性
            
        Returns:
            包含操作结果的字典
        """
        query = f"""
        MATCH (a:{start_label} {{id: $start_id}})
        MATCH (b:{end_label} {{id: $end_id}})
        CREATE (a)-[r:{rel_type} $properties]->(b)
        RETURN r
        """
        params = {
            "start_id": start_id,
            "end_id": end_id,
            "properties": properties or {}
        }
        return self.write_data(query, params)

# 全局函数，方便直接调用
def write_to_neo4j(query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """向 Neo4j 写入数据的便捷函数"""
    writer = Neo4jWriter()
    return writer.write_data(query, parameters)

def create_neo4j_node(label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    """创建 Neo4j 节点的便捷函数"""
    writer = Neo4jWriter()
    return writer.create_node(label, properties)

def create_neo4j_relationship(start_label: str, start_id: str, end_label: str, end_id: str, 
                             rel_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建 Neo4j 关系的便捷函数"""
    writer = Neo4jWriter()
    return writer.create_relationship(start_label, start_id, end_label, end_id, rel_type, properties)