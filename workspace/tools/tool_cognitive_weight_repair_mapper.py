# tool_name: cognitive_weight_repair_mapper
from typing import Dict, Any
from langchain.tools import tool
import json
import numpy as np

@tool
def cognitive_weight_repair_mapper(input_params: str) -> Dict[str, Any]:
    """
    构建认知权重与物理修复成功率的映射关系验证框架
    
    Args:
        input_params (str): JSON字符串，包含以下字段：
            - cognitive_weights: 认知权重配置字典
            - repair_scenarios: 修复场景列表
            - validation_metrics: 验证指标配置
            - historical_data: 历史修复数据（可选）
    
    Returns:
        dict: 映射验证结果，包含：
            - mapping_validity: 映射有效性评分 (0-1)
            - success_rate_prediction: 预测修复成功率
            - confidence_interval: 置信区间
            - validation_results: 详细验证结果
            - recommendations: 优化建议
    """
    try:
        # 解析输入参数
        if isinstance(input_params, str):
            params = json.loads(input_params)
        else:
            params = input_params
        
        cognitive_weights = params.get('cognitive_weights', {})
        repair_scenarios = params.get('repair_scenarios', [])
        validation_metrics = params.get('validation_metrics', {})
        historical_data = params.get('historical_data', [])
        
        # 验证输入参数
        if not cognitive_weights:
            return {
                'error': '缺少 cognitive_weights 参数',
                'mapping_validity': 0.0,
                'success_rate_prediction': 0.0
            }
        
        if not repair_scenarios:
            return {
                'error': '缺少 repair_scenarios 参数',
                'mapping_validity': 0.0,
                'success_rate_prediction': 0.0
            }
        
        # 核心映射算法
        def calculate_weighted_success_probability(weights: Dict[str, float], scenario: Dict[str, Any]) -> float:
            """基于认知权重计算修复成功率"""
            success_score = 0.0
            total_weight = 0.0
            
            # 场景特征提取
            scenario_features = scenario.get('features', {})
            scenario_complexity = scenario.get('complexity', 1.0)
            scenario_type = scenario.get('type', 'unknown')
            
            # 权重映射逻辑
            for feature, weight in weights.items():
                if feature in scenario_features:
                    feature_value = scenario_features[feature]
                    # 应用非线性映射函数
                    if isinstance(feature_value, (int, float)):
                        normalized_value = min(1.0, max(0.0, feature_value))
                        success_score += weight * normalized_value
                    elif isinstance(feature_value, bool):
                        success_score += weight * (1.0 if feature_value else 0.0)
                    total_weight += abs(weight)
            
            # 复杂度调整
            complexity_penalty = min(0.5, 0.1 * (scenario_complexity - 1.0))
            adjusted_score = max(0.0, success_score / max(total_weight, 1e-6) - complexity_penalty)
            
            return min(1.0, max(0.0, adjusted_score))
        
        # 执行映射验证
        validation_results = []
        total_scenarios = len(repair_scenarios)
        successful_predictions = 0
        
        for scenario in repair_scenarios:
            predicted_success = calculate_weighted_success_probability(cognitive_weights, scenario)
            actual_success = scenario.get('actual_success', None)
            
            result = {
                'scenario_id': scenario.get('id', 'unknown'),
                'scenario_type': scenario.get('type', 'unknown'),
                'predicted_success_rate': predicted_success,
                'actual_success': actual_success,
                'prediction_accuracy': None
            }
            
            if actual_success is not None:
                # 计算预测准确性
                prediction_error = abs(predicted_success - (1.0 if actual_success else 0.0))
                result['prediction_accuracy'] = 1.0 - prediction_error
                if prediction_error <= 0.2:  # 20%误差容忍
                    successful_predictions += 1
            
            validation_results.append(result)
        
        # 计算整体指标
        mapping_validity = successful_predictions / max(total_scenarios, 1)
        
        # 基于历史数据的增强预测
        if historical_data:
            # 简单的回归分析
            historical_success_rates = [item.get('success_rate', 0.0) for item in historical_data]
            avg_historical_success = np.mean(historical_success_rates) if historical_success_rates else 0.5
            # 结合当前预测和历史数据
            final_success_prediction = 0.7 * np.mean([r['predicted_success_rate'] for r in validation_results]) + 0.3 * avg_historical_success
        else:
            final_success_prediction = np.mean([r['predicted_success_rate'] for r in validation_results]) if validation_results else 0.5
        
        # 生成优化建议
        recommendations = []
        if mapping_validity < 0.6:
            recommendations.append("认知权重配置需要调整，当前映射有效性较低")
        if final_success_prediction < 0.7:
            recommendations.append("建议增加对高复杂度场景的权重调整")
        if len(repair_scenarios) < 5:
            recommendations.append("需要更多样化的修复场景来提高映射准确性")
        
        return {
            'mapping_validity': float(mapping_validity),
            'success_rate_prediction': float(final_success_prediction),
            'confidence_interval': [float(max(0.0, final_success_prediction - 0.1)), float(min(1.0, final_success_prediction + 0.1))],
            'validation_results': validation_results,
            'recommendations': recommendations,
            'total_scenarios_tested': total_scenarios,
            'successful_predictions': successful_predictions
        }
    
    except Exception as e:
        return {
            'error': f"处理过程中发生错误: {str(e)}",
            'mapping_validity': 0.0,
            'success_rate_prediction': 0.0
        }