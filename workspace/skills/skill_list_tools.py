import os
import json

def main(input_args=""):
    """List all tools in the workspace/tools directory"""
    tools_dir = '/Users/zhufeng/My_AI_Body/workspace/tools'
    if os.path.exists(tools_dir) and os.path.isdir(tools_dir):
        files = [f for f in os.listdir(tools_dir) if f.endswith('.py') and f != '__init__.py']
        return {"tools": files, "count": len(files)}
    else:
        return {"tools": [], "count": 0, "error": "Tools directory not found"}