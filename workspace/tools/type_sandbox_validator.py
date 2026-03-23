import json
import ast
from typing import Dict, Any

def main(input_params: str) -> Dict[str, Any]:
    """
    类型沙盒验证器：在非执行环境中验证动态权重调整补丁的安全性和有效性
    
    Args:
        input_params (str): JSON字符串，包含以下字段：
            - patch_content: 要验证的补丁内容
            - memory_weights: 当前记忆权重配置
            - validation_mode: 验证模式（"syntax", "semantic", "full"）
    
    Returns:
        dict: 验证结果，包含：
            - is_valid: 是否通过验证
            - failure_modes: 识别出的失效模式列表
            - safety_score: 安全评分 (0-1)
            - recommendations: 修复建议
    """
    try:
        # 解析输入参数
        if isinstance(input_params, str):
            params = json.loads(input_params)
        else:
            params = input_params
            
        patch_content = params.get('patch_content', '')
        memory_weights = params.get('memory_weights', {})
        validation_mode = params.get('validation_mode', 'syntax')
        
        # 验证结果初始化
        result = {
            'is_valid': True,
            'failure_modes': [],
            'safety_score': 1.0,
            'recommendations': []
        }
        
        # 语法验证
        if validation_mode in ['syntax', 'semantic', 'full']:
            try:
                ast.parse(patch_content)
            except SyntaxError as e:
                result['is_valid'] = False
                result['failure_modes'].append(f"语法错误: {str(e)}")
                result['safety_score'] = 0.0
                result['recommendations'].append("修复语法错误后再试")
                return result
        
        # 语义验证（检查危险操作）
        if validation_mode in ['semantic', 'full']:
            # 检查危险的AST节点
            tree = ast.parse(patch_content)
            dangerous_nodes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == '__future__':
                    dangerous_nodes.append("检测到 __future__ 导入")
                elif isinstance(node, ast.Import) and any(alias.name == 'os' or alias.name == 'sys' for alias in node.names):
                    dangerous_nodes.append("检测到系统模块导入")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec', 'compile']:
                        dangerous_nodes.append(f"检测到危险函数调用: {node.func.id}")
                    elif isinstance(node.func, ast.Attribute) and node.func.attr in ['system', 'popen', 'exec']:
                        dangerous_nodes.append(f"检测到危险方法调用: {node.func.attr}")
            
            if dangerous_nodes:
                result['is_valid'] = False
                result['failure_modes'].extend(dangerous_nodes)
                result['safety_score'] = max(0.0, 1.0 - len(dangerous_nodes) * 0.3)
                result['recommendations'].append("移除危险操作，使用安全的替代方案")
        
        # 完整验证（检查与记忆权重的兼容性）
        if validation_mode == 'full':
            # 检查补丁是否引用了不存在的记忆权重键
            if memory_weights:
                # 简单的字符串匹配检查
                weight_keys = set(memory_weights.keys())
                mentioned_keys = set()
                for key in weight_keys:
                    if key in patch_content:
                        mentioned_keys.add(key)
                
                # 如果提到了权重但没有实际使用，可能是问题
                if mentioned_keys and len(mentioned_keys) < len(weight_keys) * 0.5:
                    result['failure_modes'].append("补丁可能未充分利用记忆权重配置")
                    result['safety_score'] = max(0.3, result['safety_score'] - 0.2)
                    result['recommendations'].append("确保补丁正确使用所有相关的记忆权重")
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            'is_valid': False,
            'failure_modes': [f"JSON解析错误: {str(e)}"],
            'safety_score': 0.0,
            'recommendations': ["请确保输入参数是有效的JSON字符串"]
        }
    except Exception as e:
        return {
            'is_valid': False,
            'failure_modes': [f"验证过程中发生错误: {str(e)}"],
            'safety_score': 0.0,
            'recommendations': ["检查补丁内容和参数格式"]
        }

if __name__ == '__main__':
    # 测试代码
    test_input = json.dumps({
        'patch_content': 'def test_function():\n    return "safe code"',
        'memory_weights': {'weight1': 0.5, 'weight2': 0.8},
        'validation_mode': 'full'
    })
    result = main(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))