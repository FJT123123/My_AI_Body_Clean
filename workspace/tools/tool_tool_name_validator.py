# tool_name: tool_name_validator

from typing import Dict, List, Any
from langchain.tools import tool
import re

@tool
def tool_name_validator(tool_name: str) -> Dict[str, Any]:
    """
    Validate tool name length and format according to API constraints.
    
    Args:
        tool_name (str): The tool name to validate
        
    Returns:
        dict: Validation result with the following keys:
            - is_valid (bool): Whether the tool name is valid
            - original_name (str): Original tool name
            - safe_name (str): Safe tool name after validation/truncation
            - issues (list): List of issues found
            - recommendations (list): Recommendations for fixing issues
    """
    # Check length constraint (max 64 characters)
    max_length = 64
    is_valid = len(tool_name) <= max_length
    
    # Generate safe name
    safe_name = tool_name
    if not is_valid:
        # Truncate to max_length
        safe_name = tool_name[:max_length]
    
    # Check character constraints (only letters, numbers, underscores)
    if re.search(r'[^a-zA-Z0-9_]', safe_name):
        # Replace invalid characters with underscores
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', safe_name)
    
    # Ensure it doesn't start with a number
    if safe_name and safe_name[0].isdigit():
        safe_name = '_' + safe_name
    
    # Ensure it starts with a letter or underscore
    if not safe_name or (safe_name[0] != '_' and not safe_name[0].isalpha()):
        safe_name = 'tool_' + safe_name
    
    # Final truncation if needed after prefix addition
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    
    # Prepare results
    issues = []
    recommendations = []
    
    if len(tool_name) > max_length:
        issues.append(f"Tool name exceeds {max_length} character limit. Length is {len(tool_name)}.")
        recommendations.append(f"Use truncated name: {safe_name}")
    
    if re.search(r'[^a-zA-Z0-9_]', tool_name):
        issues.append("Tool name contains invalid characters. Only letters, numbers, and underscores are allowed.")
        recommendations.append("Use only alphanumeric characters and underscores in tool names")
    
    if tool_name and tool_name[0].isdigit():
        issues.append("Tool name cannot start with a number.")
        recommendations.append("Start tool names with a letter or underscore")
    
    recommendations.append("Best practice: Keep tool names under 30 characters for future extensibility")
    
    return {
        "is_valid": is_valid and len(issues) == 0,
        "original_name": tool_name,
        "safe_name": safe_name,
        "issues": issues,
        "recommendations": recommendations
    }