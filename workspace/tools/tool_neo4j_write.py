# tool_name: neo4j_write
from langchain.tools import tool
import os
import sys

# AGI Rebirth: 增加本地依赖库路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(os.path.dirname(_current_dir)) # tools -> workspace -> root
_lib_path = os.path.join(_root_dir, "lib")
if os.path.exists(_lib_path) and _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

def check_neo4j_driver():
    """检查 Neo4j Python 驱动是否已安装"""
    try:
        import neo4j
        return {"installed": True, "version": neo4j.__version__}
    except ImportError:
        return {"installed": False, "error": "Neo4j driver not installed"}

def write_to_neo4j(query, parameters=None):
    """向 Neo4j 数据库写入数据的通用函数"""
    try:
        import neo4j
        # 获取连接信息（假设已配置）
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        
        driver = neo4j.GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run(query, parameters or {})
            return {"success": True, "result_summary": str(result.consume())}
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def neo4j_write(query: str, parameters: dict = None) -> dict:
    """
    向 Neo4j 数据库写入数据的工具
    
    Args:
        query (str): Cypher 查询语句
        parameters (dict, optional): 查询参数字典
    
    Returns:
        dict: 包含操作结果的字典，包含 success、result_summary 或 error 字段
    
    Raises:
        ImportError: 当 Neo4j 驱动未安装时
    """
    try:
        # 检查驱动是否已安装
        driver_check = check_neo4j_driver()
        if not driver_check["installed"]:
            return {"success": False, "error": "Neo4j driver not installed", "driver_check": driver_check}
        
        # 执行写入操作
        result = write_to_neo4j(query, parameters)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}