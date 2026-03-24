# 重新定义_get_tool_importance函数以确保修改生效
def _get_tool_importance(tool_name: str) -> float:
    """获取工具的重要性权重 - 增强认知权重免疫系统"""
    critical_tools = {
        'run_skill': 1.5,
        'write_workspace_file': 1.8,
        'read_workspace_file': 1.2,
        'forge_new_skill': 2.0,
        'cognitive_weighting_framework': 1.6,
        'tool_output_stream_diagnostic': 1.7,
        'interaction_weighting_capability_defense_layer': 1.9,
        'cross_tool_validator': 1.8,  # 增强跨工具验证器的重要性
        'output_redirection_debug_info_escape_prevention': 1.9,  # 增强输出重定向防护的重要性
        'end_to_end_debug_info_integrity_validator': 2.0  # 增强端到端验证器的重要性
    }
    
    return critical_tools.get(tool_name, 1.0)