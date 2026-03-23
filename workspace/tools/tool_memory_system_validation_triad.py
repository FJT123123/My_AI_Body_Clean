import json
import ast
from typing import Dict, Any

def main(input_params: str) -> Dict[str, Any]:
    """
    记忆系统三维验证框架：整合代码补丁安全性、动态权重有效性和修复结果真实性三个维度的验证
    
    Args:
        input_params (str): JSON字符串，包含以下字段：
            - patch_content: 要验证的代码补丁内容
            - memory_weights: 记忆权重配置字典
            - repair_data: 修复结果数据字典
            - validation_mode: 验证模式 ("syntax", "semantic", "full")
    
    Returns:
        dict: 三维验证结果，包含：
            - patch_safety: 补丁安全性验证结果
            - weight_effectiveness: 权重有效性验证结果  
            - repair_authenticity: 修复真实性验证结果
            - overall_validity: 整体有效性评分 (0-1)
            - confidence_interval: 置信区间
            - recommendations: 优化建议列表
    """
    try:
        # 解析输入参数
        if isinstance(input_params, str):
            params = json.loads(input_params)
        else:
            params = input_params
            
        patch_content = params.get('patch_content', '')
        memory_weights = params.get('memory_weights', {})
        repair_data = params.get('repair_data', {})
        validation_mode = params.get('validation_mode', 'syntax')
        
        # 初始化验证结果
        result = {
            'patch_safety': {'is_valid': True, 'safety_score': 1.0, 'issues': []},
            'weight_effectiveness': {'is_valid': True, 'effectiveness_score': 1.0, 'issues': []},
            'repair_authenticity': {'is_valid': True, 'authenticity_score': 1.0, 'issues': []},
            'overall_validity': 1.0,
            'confidence_interval': [0.9, 1.0],
            'recommendations': []
        }
        
        # 1. 补丁安全性验证
        try:
            ast.parse(patch_content)
        except SyntaxError as e:
            result['patch_safety']['is_valid'] = False
            result['patch_safety']['safety_score'] = 0.0
            result['patch_safety']['issues'].append(f"语法错误: {str(e)}")
            result['recommendations'].append("修复补丁的语法错误")
        
        # 检查危险操作
        if result['patch_safety']['is_valid']:
            tree = ast.parse(patch_content)
            dangerous_operations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec', 'compile']:
                        dangerous_operations.append(f"危险函数调用: {node.func.id}")
                    elif isinstance(node.func, ast.Attribute) and hasattr(node.func, 'attr') and node.func.attr in ['system', 'popen', 'exec']:
                        dangerous_operations.append(f"危险方法调用: {node.func.attr}")
            
            if dangerous_operations:
                result['patch_safety']['is_valid'] = False
                result['patch_safety']['safety_score'] = max(0.0, 1.0 - len(dangerous_operations) * 0.4)
                result['patch_safety']['issues'].extend(dangerous_operations)
                result['recommendations'].append("移除危险操作，使用安全的替代方案")
        
        # 2. 权重有效性验证
        if memory_weights:
            # 检查权重值是否在合理范围内
            invalid_weights = []
            for key, value in memory_weights.items():
                if not isinstance(value, (int, float)) or value < 0 or value > 1:
                    invalid_weights.append(f"权重 {key} 值 {value} 不在 [0,1] 范围内")
            
            if invalid_weights:
                result['weight_effectiveness']['is_valid'] = False
                result['weight_effectiveness']['effectiveness_score'] = max(0.0, 1.0 - len(invalid_weights) * 0.3)
                result['weight_effectiveness']['issues'].extend(invalid_weights)
                result['recommendations'].append("确保所有记忆权重值都在 [0,1] 范围内")
        else:
            result['weight_effectiveness']['is_valid'] = False
            result['weight_effectiveness']['effectiveness_score'] = 0.5
            result['weight_effectiveness']['issues'].append("未提供记忆权重配置")
            result['recommendations'].append("提供有效的记忆权重配置以提高验证准确性")
        
        # 3. 修复真实性验证
        if repair_data:
            # 检查修复数据是否包含必要的字段
            required_fields = ['success', 'result', 'timestamp']
            missing_fields = []
            for field in required_fields:
                if field not in repair_data:
                    missing_fields.append(field)
            
            if missing_fields:
                result['repair_authenticity']['is_valid'] = False
                result['repair_authenticity']['authenticity_score'] = max(0.0, 1.0 - len(missing_fields) * 0.3)
                result['repair_authenticity']['issues'].append(f"修复数据缺少必要字段: {missing_fields}")
                result['recommendations'].append(f"确保修复数据包含所有必要字段: {required_fields}")
            
            # 检查修复是否成功
            if 'success' in repair_data and not repair_data['success']:
                result['repair_authenticity']['is_valid'] = False
                result['repair_authenticity']['authenticity_score'] = 0.3
                result['repair_authenticity']['issues'].append("修复操作未成功完成")
                result['recommendations'].append("分析修复失败原因并重新尝试")
        else:
            result['repair_authenticity']['is_valid'] = False
            result['repair_authenticity']['authenticity_score'] = 0.4
            result['repair_authenticity']['issues'].append("未提供修复结果数据")
            result['recommendations'].append("提供完整的修复结果数据以进行真实性验证")
        
        # 4. 计算整体有效性评分
        safety_score = result['patch_safety']['safety_score']
        effectiveness_score = result['weight_effectiveness']['effectiveness_score']
        authenticity_score = result['repair_authenticity']['authenticity_score']
        
        # 加权平均（安全性权重最高）
        result['overall_validity'] = (
            safety_score * 0.5 + 
            effectiveness_score * 0.3 + 
            authenticity_score * 0.2
        )
        
        # 调整置信区间
        if result['overall_validity'] >= 0.8:
            result['confidence_interval'] = [0.75, 1.0]
        elif result['overall_validity'] >= 0.6:
            result['confidence_interval'] = [0.5, 0.85]
        else:
            result['confidence_interval'] = [0.0, 0.7]
        
        return result
        
    except json.JSONDecodeError as e:
        return {
            'patch_safety': {'is_valid': False, 'safety_score': 0.0, 'issues': [f"JSON解析错误: {str(e)}"]},
            'weight_effectiveness': {'is_valid': False, 'effectiveness_score': 0.0, 'issues': ["无法解析输入参数"]},
            'repair_authenticity': {'is_valid': False, 'authenticity_score': 0.0, 'issues': ["无法解析输入参数"]},
            'overall_validity': 0.0,
            'confidence_interval': [0.0, 0.0],
            'recommendations': ["请确保输入参数是有效的JSON字符串"]
        }
    except Exception as e:
        return {
            'patch_safety': {'is_valid': False, 'safety_score': 0.0, 'issues': [f"验证过程中发生错误: {str(e)}"]},
            'weight_effectiveness': {'is_valid': False, 'effectiveness_score': 0.0, 'issues': ["验证过程异常"]},
            'repair_authenticity': {'is_valid': False, 'authenticity_score': 0.0, 'issues': ["验证过程异常"]},
            'overall_validity': 0.0,
            'confidence_interval': [0.0, 0.0],
            'recommendations': ["检查输入参数格式和内容"]
        }

if __name__ == '__main__':
    # 测试代码
    test_input = json.dumps({
        'patch_content': 'def safe_function():\n    return "safe code"',
        'memory_weights': {'weight1': 0.8, 'weight2': 0.6},
        'repair_data': {'success': True, 'result': 'fixed', 'timestamp': '2026-03-22'},
        'validation_mode': 'full'
    })
    result = main(test_input)
    print(json.dumps(result, indent=2, ensure_ascii=False))