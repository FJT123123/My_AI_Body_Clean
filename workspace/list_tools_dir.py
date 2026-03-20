import os

def list_tools_directory():
    tools_path = "workspace/tools"
    if os.path.exists(tools_path):
        return {"tools": os.listdir(tools_path)}
    else:
        return {"error": "tools directory not found"}

if __name__ == "__main__":
    print(list_tools_directory())