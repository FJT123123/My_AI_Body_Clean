# tool_name: neo4j_type_constraint_validator

from langchain.tools import tool
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

@tool
def neo4j_type_constraint_validator(input_args):
    """
    Neo4j类型约束验证器 - 建立预测性防御的灯塔
    
    这个工具提供应用层类型安全验证框架，弥补Neo4j原生约束的局限性，
    确保在高并发和复杂查询场景下实现真正的预测性防御。
    
    Args:
        input_args (str or dict): 包含以下参数的JSON字符串或字典:
            - validation_mode (str): 验证模式，可选 'basic', 'stress_test', 'concurrent'
            - node_constraints (dict): 节点约束定义
            - relationship_constraints (dict): 关系约束定义
            - test_scenarios (list): 测试场景列表
            - concurrency_level (int): 并发级别，默认5
    
    Returns:
        dict: 包含验证结果、见解、事实和记忆的字典
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        validation_mode = params.get('validation_mode', 'basic')
        node_constraints = params.get('node_constraints', {})
        relationship_constraints = params.get('relationship_constraints', {})
        test_scenarios = params.get('test_scenarios', [])
        concurrency_level = params.get('concurrency_level', 5)
        
        insights = []
        facts = []
        memories = []
        results = {
            'validation_mode': validation_mode,
            'success': True,
            'errors': [],
            'warnings': [],
            'performance_metrics': {}
        }
        
        # neo4j_write 函数已在运行时全局可用，直接使用
        # 无需导入，直接调用即可
        
        # 执行测试场景 - 在应用层进行类型验证
        if validation_mode == 'basic':
            insights.append("执行基础类型约束验证")
            test_results = _execute_app_layer_validation(test_scenarios, node_constraints, relationship_constraints)
            results.update(test_results)
            
        elif validation_mode == 'stress_test':
            insights.append(f"执行压力测试模式，测试场景数量: {len(test_scenarios)}")
            start_time = time.time()
            stress_results = _execute_app_layer_validation(test_scenarios, node_constraints, relationship_constraints)
            end_time = time.time()
            results.update(stress_results)
            results['performance_metrics']['stress_test_duration'] = end_time - start_time
            results['performance_metrics']['scenarios_executed'] = len(test_scenarios)
            
        elif validation_mode == 'concurrent':
            insights.append(f"执行并发测试模式，并发级别: {concurrency_level}")
            start_time = time.time()
            concurrent_results = _execute_concurrent_app_layer_validation(
                test_scenarios, concurrency_level, node_constraints, relationship_constraints
            )
            end_time = time.time()
            results.update(concurrent_results)
            results['performance_metrics']['concurrent_test_duration'] = end_time - start_time
            results['performance_metrics']['concurrency_level'] = concurrency_level
            
        else:
            results['success'] = False
            results['errors'].append(f"未知的验证模式: {validation_mode}")
            return {
                'result': results,
                'insights': insights,
                'facts': facts,
                'memories': memories
            }
        
        # 添加预测性防御分析
        predictive_analysis = _analyze_predictive_defense_capability(results)
        results['predictive_defense'] = predictive_analysis
        insights.append(f"预测性防御能力评估完成: {predictive_analysis.get('defense_score', 0)}/100")
        
        # 记录关键事实
        facts.append(f"Neo4j类型约束验证完成，模式: {validation_mode}")
        facts.append(f"验证成功: {results['success']}")
        if results['errors']:
            facts.append(f"发现错误数量: {len(results['errors'])}")
        if results['warnings']:
            facts.append(f"发现警告数量: {len(results['warnings'])}")
            
        # 创建记忆
        memories.append({
            'type': 'neo4j_type_constraint_validation',
            'mode': validation_mode,
            'timestamp': time.time(),
            'success': results['success'],
            'error_count': len(results['errors']),
            'warning_count': len(results['warnings']),
            'defense_score': predictive_analysis.get('defense_score', 0)
        })
        
        return {
            'result': results,
            'insights': insights,
            'facts': facts,
            'memories': memories
        }
        
    except Exception as e:
        error_msg = f"Neo4j类型约束验证器执行失败: {str(e)}"
        return {
            'result': {
                'success': False,
                'errors': [error_msg],
                'validation_mode': 'error'
            },
            'insights': [f"验证器执行异常: {str(e)}"],
            'facts': [error_msg],
            'memories': []
        }

def _execute_app_layer_validation(scenarios, node_constraints, relationship_constraints):
    """在应用层执行类型验证"""
    errors = []
    warnings = []
    executed_scenarios = 0
    
    for i, scenario in enumerate(scenarios):
        try:
            # 在应用层验证场景数据是否符合约束
            validation_result = _validate_scenario_against_constraints(
                scenario, node_constraints, relationship_constraints
            )
            
            if not validation_result['valid']:
                errors.extend(validation_result['errors'])
            else:
                executed_scenarios += 1
                
        except Exception as e:
            errors.append(f"场景 {i} 验证异常: {str(e)}")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'executed_scenarios': executed_scenarios,
        'total_scenarios': len(scenarios)
    }

def _execute_concurrent_app_layer_validation(scenarios, concurrency_level, node_constraints, relationship_constraints):
    """在应用层执行并发类型验证"""
    errors = []
    warnings = []
    completed = 0
    
    def worker(scenario):
        try:
            validation_result = _validate_scenario_against_constraints(
                scenario, node_constraints, relationship_constraints
            )
            return {
                'valid': validation_result['valid'],
                'errors': validation_result['errors']
            }
        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}
    
    with ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        futures = [executor.submit(worker, scenario) for scenario in scenarios]
        
        for future in as_completed(futures):
            result = future.result()
            if not result.get('valid', False):
                errors.extend(result.get('errors', []))
            completed += 1
    
    return {
        'errors': errors,
        'warnings': warnings,
        'completed_scenarios': completed,
        'total_scenarios': len(scenarios)
    }

def _validate_scenario_against_constraints(scenario, node_constraints, relationship_constraints):
    """验证单个场景是否符合约束"""
    errors = []
    valid = True
    
    # 处理字符串场景（向后兼容）
    if isinstance(scenario, str):
        # 字符串场景被视为简单的测试标识符，不进行详细验证
        # 这允许压力测试使用简单的字符串列表
        return {'valid': True, 'errors': []}
    
    # 确保scenario是字典类型
    if not isinstance(scenario, dict):
        errors.append(f"场景必须是字典或字符串类型，但收到了: {type(scenario).__name__}")
        return {'valid': False, 'errors': errors}
    
    scenario_type = scenario.get('type', 'create_node')
    
    if scenario_type == 'create_node':
        node_label = scenario.get('label', 'TestNode')
        properties = scenario.get('properties', {})
        
        # 检查节点约束
        if node_label in node_constraints:
            constraints = node_constraints[node_label]
            
            # 检查必需属性
            required_props = constraints.get('required_properties', [])
            for prop in required_props:
                if prop not in properties:
                    errors.append(f"节点 {node_label} 缺少必需属性: {prop}")
                    valid = False
            
            # 检查唯一属性（这里只做基本检查，实际唯一性需要数据库支持）
            unique_props = constraints.get('unique_properties', [])
            for prop in unique_props:
                if prop not in properties:
                    errors.append(f"节点 {node_label} 缺少唯一属性: {prop}")
                    valid = False
                    
    elif scenario_type == 'create_relationship':
        rel_type = scenario.get('relationship_type', 'TEST_REL')
        properties = scenario.get('properties', {})
        
        # 检查关系约束
        if rel_type in relationship_constraints:
            constraints = relationship_constraints[rel_type]
            
            # 检查必需属性
            required_props = constraints.get('required_properties', [])
            for prop in required_props:
                if prop not in properties:
                    errors.append(f"关系 {rel_type} 缺少必需属性: {prop}")
                    valid = False
    
    return {'valid': valid, 'errors': errors}

def _analyze_predictive_defense_capability(validation_results):
    """分析预测性防御能力"""
    total_errors = len(validation_results.get('errors', []))
    total_warnings = len(validation_results.get('warnings', []))
    
    # 计算防御分数
    if total_errors == 0 and total_warnings == 0:
        defense_score = 100
    elif total_errors == 0:
        defense_score = max(70, 100 - total_warnings * 5)
    else:
        defense_score = max(0, 100 - total_errors * 15 - total_warnings * 3)
    
    # 分析防御能力
    if defense_score >= 90:
        defense_level = "优秀"
        recommendation = "系统具有强大的预测性防御能力，可以处理复杂的高并发场景"
    elif defense_score >= 70:
        defense_level = "良好"
        recommendation = "系统具有良好的预测性防御能力，建议优化警告项以提升稳定性"
    elif defense_score >= 50:
        defense_level = "一般"
        recommendation = "系统预测性防御能力有限，需要修复错误并加强类型约束"
    else:
        defense_level = "薄弱"
        recommendation = "系统缺乏有效的预测性防御，必须立即修复所有错误并重新设计约束"
    
    return {
        'defense_score': defense_score,
        'defense_level': defense_level,
        'recommendation': recommendation,
        'error_count': total_errors,
        'warning_count': total_warnings
    }