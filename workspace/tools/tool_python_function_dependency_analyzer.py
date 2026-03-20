# tool_name: python_function_dependency_analyzer
from langchain.tools import tool
import ast
import os

def add_parent_references(node, parent=None):
    """为AST节点添加父引用"""
    for child in ast.iter_child_nodes(node):
        child.parent = parent
        add_parent_references(child, child)

def get_parent_function(node):
    """获取节点所属的函数名"""
    current = node
    while hasattr(current, 'parent') and current.parent is not None:
        current = current.parent
        if isinstance(current, ast.FunctionDef):
            return current.name
    return None

@tool
def python_function_dependency_analyzer(file_path: str) -> dict:
    """
    分析Python文件中的函数依赖关系
    
    Args:
        file_path (str): Python文件的路径
        
    Returns:
        dict: 包含函数定义、函数调用关系和文件路径的字典
              - functions: 函数名作为键，包含函数名称、行号和调用的其他函数列表
              - calls: 函数调用关系列表，包含调用者、被调用者和行号
              - file_path: 分析的文件路径
              - error: 如果出现错误，包含错误信息
    """
    if not os.path.exists(file_path):
        return {"error": f"文件不存在: {file_path}"}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        add_parent_references(tree)
        
        # 存储函数定义
        functions = {}
        # 存储函数调用
        calls = []
        
        # 遍历AST获取函数定义
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = {
                    "name": node.name,
                    "lineno": node.lineno,
                    "calls": []
                }
        
        # 遍历AST获取函数调用
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    caller_func = get_parent_function(node)
                    callee = node.func.id
                    if caller_func and caller_func in functions:
                        functions[caller_func]["calls"].append(callee)
                    calls.append({
                        "caller": caller_func,
                        "callee": callee,
                        "lineno": node.lineno
                    })
        
        return {
            "functions": functions,
            "calls": calls,
            "file_path": file_path
        }
    except Exception as e:
        return {"error": f"分析失败: {str(e)}"}