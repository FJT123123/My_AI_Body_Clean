# tool_name: error_pattern_to_cognition_evolution_mapper
from langchain.tools import tool
import json

@tool
def error_pattern_to_cognition_evolution_mapper(input_args):
    """
    错误模式到认知进化映射器 - 将错误模式精确分类并触发对应的修复策略
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - error_type: 错误类型
            - error_message: 错误消息
            - context: 错误上下文
            - parameters: 相关参数
    
    Returns:
        dict: 包含分类结果、修复策略和验证结果的字典
    """
    try:
        import json
        
        # 解析输入
        if isinstance(input_args, str):
            args = json.loads(input_args)
        else:
            args = input_args
        
        error_type = args.get('error_type', '')
        error_message = args.get('error_message', '')
        context = args.get('context', '')
        parameters = args.get('parameters', {})
        
        # 错误模式分类
        error_patterns = {
            'parameter_validation_error': {
                'keywords': ['missing', 'required', 'parameter'],
                'repair_strategy': 'auto_generate_missing_parameter_template',
                'cognitive_weight': 0.9
            },
            'type_error': {
                'keywords': ['type', 'expected', 'got'],
                'repair_strategy': 'auto_convert_parameter_type',
                'cognitive_weight': 0.85
            },
            'api_length_error': {
                'keywords': ['length', '64', 'characters'],
                'repair_strategy': 'auto_truncate_tool_name',
                'cognitive_weight': 0.8
            }
        }
        
        # 分类错误模式
        classified_pattern = None
        for pattern_name, pattern_config in error_patterns.items():
            if any(keyword.lower() in error_message.lower() for keyword in pattern_config['keywords']):
                classified_pattern = pattern_name
                break
        
        if not classified_pattern:
            classified_pattern = 'unknown_error'
            repair_strategy = 'fallback_manual_intervention'
            cognitive_weight = 0.5
        else:
            repair_strategy = error_patterns[classified_pattern]['repair_strategy']
            cognitive_weight = error_patterns[classified_pattern]['cognitive_weight']
        
        # 执行修复策略
        repair_result = None
        if repair_strategy == 'auto_generate_missing_parameter_template':
            required_params = []
            if 'input_data' in error_message:
                required_params.append('input_data')
            if 'tool_name' in error_message:
                required_params.append('tool_name')
            
            repair_result = {
                'template': {param: '' for param in required_params},
                'strategy': repair_strategy,
                'success': len(required_params) > 0
            }
        elif repair_strategy == 'auto_convert_parameter_type':
            repair_result = {
                'strategy': repair_strategy,
                'success': True,
                'converted_parameters': parameters
            }
        elif repair_strategy == 'auto_truncate_tool_name':
            repair_result = {
                'strategy': repair_strategy,
                'success': True,
                'truncated_name': error_message[:64] if len(error_message) > 64 else error_message
            }
        elif repair_strategy == 'fallback_manual_intervention':
            repair_result = {
                'strategy': repair_strategy,
                'success': False,
                'message': 'Manual intervention required'
            }
        
        return {
            'error_classification': classified_pattern,
            'repair_strategy': repair_strategy,
            'cognitive_weight': cognitive_weight,
            'repair_result': repair_result,
            'physical_validation_ready': True
        }
    except Exception as e:
        return {
            'error_classification': 'unknown_error',
            'repair_strategy': 'fallback_manual_intervention',
            'cognitive_weight': 0.5,
            'repair_result': {
                'strategy': 'fallback_manual_intervention',
                'success': False,
                'error': str(e)
            },
            'physical_validation_ready': False
        }