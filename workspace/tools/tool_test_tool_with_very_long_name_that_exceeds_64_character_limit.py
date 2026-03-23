# tool_name: test_tool_with_very_long_name_that_exceeds_64_character_limit
from langchain.tools import tool

@tool
def test_tool_with_very_long_name_that_exceeds_64_character_limit(tool_name: str) -> dict:
    """
    Test tool with a very long name that exceeds the 64 character limit to verify automatic truncation and validation works correctly.
    
    Args:
        tool_name: The tool name to test for length validation
    
    Returns:
        dict: A dictionary containing the validation result with the following keys:
            - original_name: The original tool name provided
            - is_valid: Boolean indicating if the name is valid (length <= 64 characters)
            - name_length: The length of the original name
            - message: Descriptive message about the validation result
    """
    try:
        # Check if the name length exceeds 64 characters
        name_length = len(tool_name)
        is_valid = name_length <= 64
        
        if is_valid:
            message = f"Tool name is valid with length {name_length}."
        else:
            message = f"Tool name exceeds 64 character limit. Length is {name_length}."
        
        return {
            "original_name": tool_name,
            "is_valid": is_valid,
            "name_length": name_length,
            "message": message
        }
    except Exception as e:
        return {
            "original_name": tool_name,
            "is_valid": False,
            "name_length": len(tool_name) if tool_name else 0,
            "message": f"Error validating tool name: {str(e)}"
        }