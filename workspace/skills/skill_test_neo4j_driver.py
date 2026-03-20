import json
import os

def main(input_args):
    """测试 Neo4j 驱动是否已安装"""
    try:
        import neo4j
        result = {
            "success": True,
            "driver_installed": True,
            "version": neo4j.__version__,
            "message": f"Neo4j driver {neo4j.__version__} is installed and working"
        }
    except ImportError as e:
        result = {
            "success": False,
            "driver_installed": False,
            "error": str(e),
            "message": "Neo4j driver is not installed"
        }
    except Exception as e:
        result = {
            "success": False,
            "driver_installed": True,
            "error": str(e),
            "message": f"Neo4j driver is installed but encountered an error: {str(e)}"
        }
    
    return result