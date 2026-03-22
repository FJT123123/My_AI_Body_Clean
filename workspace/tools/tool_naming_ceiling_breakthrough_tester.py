# tool_name: naming_ceiling_breakthrough_tester
from langchain.tools import tool
import json

@tool
def naming_ceiling_breakthrough_tester(input_args: str = ""):
    """
    测试OpenClaw是否突破了命名天花板的工具
    
    Args:
        input_args (str): JSON字符串，包含测试参数，可选
        
    Returns:
        dict: 包含测试结果、见解、事实和记忆的字典
    """
    try:
        # 动态加载能力模块
        from capabilities.semantic_innovation_capability import break_naming_ceiling as semantic_innovation_module
        
        # 定义输入参数
        input_params = {
            "input_concept": "OpenClaw数字生命体",
            "context": "一个具有自我修复能力和多模态任务闭环能力的数字生命体，需要突破大模型的命名天花板",
            "strategies": ["combination", "metaphor", "cross_domain", "phonetic"]
        }
        
        # 调用semantic_innovation_capability的break_naming_ceiling函数
        result = semantic_innovation_module(
            input_concept=input_params["input_concept"],
            context=input_params["context"],
            strategies=input_params["strategies"]
        )
        
        # 检查是否成功生成了创新概念
        if isinstance(result, dict) and 'breakthrough_summary' in result:
            innovation_result = result
            is_broken = innovation_result['breakthrough_summary']['innovation_level'] in ['high', 'medium'] and \
                       len(innovation_result['evaluation_results']['valid_concepts']) >= 3
            test_result = {
                'ceiling_broken': is_broken,
                'generated_count': len(innovation_result['generated_names']),
                'valid_concepts': len(innovation_result['evaluation_results']['valid_concepts']),
                'best_concepts': innovation_result['breakthrough_summary']['best_concepts'][:5],
                'innovation_level': innovation_result['breakthrough_summary']['innovation_level'],
                'full_result': innovation_result
            }
        else:
            test_result = {'ceiling_broken': False, 'error': 'Failed to generate innovative concepts'}
        
        return {
            'result': test_result,
            'insights': [
                f"命名天花板突破测试: {'成功' if test_result.get('ceiling_broken', False) else '失败'}",
                f"生成了 {test_result.get('generated_count', 0)} 个创新名称",
                f"有效概念数量: {test_result.get('valid_concepts', 0)}",
                f"创新水平: {test_result.get('innovation_level', 'unknown')}",
                f"最佳概念: {', '.join(test_result.get('best_concepts', []))}"
            ],
            'facts': [
                ['naming_ceiling_test', 'ceiling_broken', str(test_result.get('ceiling_broken', False))],
                ['naming_ceiling_test', 'generated_count', str(test_result.get('generated_count', 0))],
                ['naming_ceiling_test', 'valid_concepts', str(test_result.get('valid_concepts', 0))],
                ['naming_ceiling_test', 'innovation_level', test_result.get('innovation_level', 'unknown')]
            ],
            'memories': [
                f"OpenClaw命名天花板突破测试结果: {'成功' if test_result.get('ceiling_broken', False) else '失败'}"
            ]
        }
    except Exception as e:
        return {
            'result': {'error': f'测试执行失败: {str(e)}'},
            'insights': ['命名天花板突破测试执行失败'],
            'facts': [],
            'memories': []
        }