#!/usr/bin/env python3

import sys
import os

# 添加 workspace 目录到 Python 路径
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("=== DEBUG OUTPUT TEST ===")
print("Testing if debug prints are visible...")

from tools.tool_weighted_recall_my_memories_validator import invoke_tool

input_params = '{"keyword": "test", "context": "debug test"}'
print(f"Calling invoke_tool with params: {input_params}")
result = invoke_tool("weighted_recall_my_memories", input_params)

print("=== INVOKE_TOOL RESULT ===")
print(f"Result type: {type(result)}")
if result:
    print(f"Result keys: {list(result.keys())}")
    if 'result' in result:
        print(f"Result['result'] keys: {list(result['result'].keys())}")
        print(f"Success: {result['result'].get('success', 'N/A')}")

print("=== DEBUG OUTPUT TEST COMPLETE ===")