# 强制重新加载所有工具的补丁

def force_tool_reload():
    """强制重新加载所有工具"""
    import importlib
    import sys
    import os
    
    # 重新加载工具模块
    workspace_dir = os.path.join(os.path.dirname(__file__), '..')
    tools_dir = os.path.join(workspace_dir, 'tools')
    
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    
    # 重新导入所有工具模块
    for filename in os.listdir(tools_dir):
        if filename.startswith('tool_') and filename.endswith('.py'):
            module_name = filename[:-3]  # 去掉 .py 扩展名
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
            except Exception as e:
                print(f"Failed to reload {module_name}: {e}")
    
    return {"status": "success", "message": "All tools reloaded successfully"}