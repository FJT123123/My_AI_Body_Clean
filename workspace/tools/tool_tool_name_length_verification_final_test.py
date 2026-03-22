# tool_name: tool_name_length_verification_final_test
from langchain.tools import tool
import json

@tool
def tool_name_length_verification_final_test(input_args: str = "") -> dict:
    """
    Final verification tool for testing that tool names under 64 characters work properly.
    
    Args:
        input_args (str): JSON string of input arguments, optional
        
    Returns:
        dict: Contains result, tool name, and length verification
    """
    try:
        # Parse input args if provided
        if input_args:
            try:
                parsed_args = json.loads(input_args)
            except json.JSONDecodeError:
                parsed_args = {}
        else:
            parsed_args = {}
        
        # Get the actual tool name from the function name
        tool_name = tool_name_length_verification_final_test.name
        
        # Verify the length is under 64 characters
        name_length = len(tool_name)
        is_valid_length = name_length < 64
        
        result = {
            "result": "Successfully created tool with safe name under 64-char limit" if is_valid_length else "Tool name exceeds 64 character limit",
            "tool_name": tool_name,
            "length": name_length,
            "is_valid_length": is_valid_length,
            "input_args": parsed_args
        }
        
        return result
        
    except Exception as e:
        return {
            "result": "Error during tool name verification",
            "tool_name": "tool_name_length_verification_final_test",
            "length": len("tool_name_length_verification_final_test"),
            "error": str(e)
        }