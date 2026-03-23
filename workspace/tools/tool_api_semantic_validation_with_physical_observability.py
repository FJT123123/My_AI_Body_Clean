# tool_name: api_semantic_validation_with_physical_observability

from langchain.tools import tool
import json

@tool
def api_semantic_validation_with_physical_observability(input_args):
    """
    API语义验证与物理可观测性集成工具
    
    将API参数语义验证与物理可观测性深度结合，
    确保在参数生成阶段就能拦截400错误，并提供物理性能指标。
    
    Args:
        input_args (str): JSON字符串，包含以下字段：
            - parameters: 要验证的参数字典
            - parameter_contract: 参数契约定义（可选）
            - type_contract: 类型契约定义（可选）
            - validation_mode: 验证模式 ("strict", "lenient", "repair")
            
    Returns:
        dict: 包含验证结果和物理观测数据的完整报告
    """
    try:
        if isinstance(input_args, str):
            config = json.loads(input_args)
        else:
            config = input_args
            
        parameters = config.get('parameters', {})
        parameter_contract = config.get('parameter_contract', {})
        type_contract = config.get('type_contract', {})
        validation_mode = config.get('validation_mode', 'strict')
        
        # 使用运行时注入加载能力模块
        capability_module = __import__('workspace.capabilities.api_semantic_validation_with_physical_observability_capability', fromlist=['api_semantic_validation_with_physical_observability_capability'])
        
        result = capability_module.api_semantic_validation_with_physical_observability_capability(
            parameters=parameters,
            parameter_contract=parameter_contract,
            type_contract=type_contract,
            validation_mode=validation_mode
        )
        
        return result
        
    except Exception as e:
        return {
            'is_valid': False,
            'errors': [f"验证过程异常: {str(e)}"],
            'warnings': [],
            'validated_parameters': {},
            'physical_observability': {},
            'preventive_interception': {
                'would_prevent_400_error': True,
                'intercepted_issues': [f"验证过程异常: {str(e)}"],
                'suggested_fixes': []
            }
        }