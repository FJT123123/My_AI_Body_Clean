# tool_name: dynamic_memory_weighting_validator

from typing import Dict, Any, List, Optional
from langchain.tools import tool
import time
import json

@tool
def dynamic_memory_weighting_validator(input_args: str) -> Dict[str, Any]:
    """
    动态记忆权重验证工具 - 验证dynamic_memory_weighting_capability模块的功能完整性
    
    Args:
        input_args (str): JSON字符串，包含以下参数:
            - test_scope (str): 测试范围，可选 'all', 'time_decay', 'semantic_similarity', 'memory_clustering', 'batch_weighting', 'full_cycle'
            - verbose (bool): 是否显示详细输出
    
    Returns:
        Dict[str, Any]: 包含所有测试结果的字典
    """
    try:
        args = json.loads(input_args) if isinstance(input_args, str) else input_args
        test_scope = args.get('test_scope', 'all')
        verbose = args.get('verbose', False)
        
        # 动态加载capability模块
        import importlib
        import sys
        import os
        
        # 确保 workspace 目录在 Python 路径中
        workspace_dir = os.path.join(os.path.dirname(__file__), '..')
        if workspace_dir not in sys.path:
            sys.path.insert(0, workspace_dir)
            
        dynamic_memory_weighting_capability = importlib.import_module('capabilities.dynamic_memory_weighting_capability')
        
        results = {
            'tool': 'dynamic_memory_weighting_validator',
            'timestamp': time.time(),
            'test_scope': test_scope,
            'verbose': verbose,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_results': {}
        }
        
        # 根据测试范围决定运行哪些测试
        test_functions = []
        if test_scope in ['all', 'time_decay']:
            test_functions.append(('test_time_decay_weight', test_time_decay_weight))
        if test_scope in ['all', 'semantic_similarity']:
            test_functions.append(('test_semantic_similarity', test_semantic_similarity))
        if test_scope in ['all', 'memory_clustering']:
            test_functions.append(('test_memory_clustering', test_memory_clustering))
        if test_scope in ['all', 'batch_weighting']:
            test_functions.append(('test_batch_weighting', test_batch_weighting))
        if test_scope in ['all', 'full_cycle']:
            test_functions.append(('test_full_cycle', test_full_cycle))
        
        for test_name, test_func in test_functions:
            try:
                test_result = test_func(dynamic_memory_weighting_capability, verbose)
                results['test_results'][test_name] = test_result
                results['tests_run'] += 1
                if test_result.get('passed', False):
                    results['tests_passed'] += 1
                else:
                    results['tests_failed'] += 1
            except Exception as e:
                results['test_results'][test_name] = {
                    'passed': False,
                    'error': str(e),
                    'details': f'Test {test_name} failed with exception'
                }
                results['tests_run'] += 1
                results['tests_failed'] += 1
        
        return results
    except Exception as e:
        return {
            'error': str(e),
            'tool': 'dynamic_memory_weighting_validator',
            'status': 'failed'
        }

def test_time_decay_weight(capability_module, verbose=False):
    """验证时间衰减权重计算的正确性"""
    try:
        # 测试当前时间与过去时间的权重计算
        current_time = time.time()
        past_time = current_time - 3600  # 1小时前
        
        # 计算时间衰减权重
        weight1 = capability_module.calculate_time_decay_weight(past_time, current_time, decay_rate=0.1)
        weight2 = capability_module.calculate_time_decay_weight(past_time, current_time, decay_rate=0.5)
        
        # 验证权重在合理范围内（0-1之间）
        weight1_valid = 0 <= weight1 <= 1
        weight2_valid = 0 <= weight2 <= 1
        # 验证较高衰减率应该产生较低权重（更快衰减）
        higher_decay_lower_weight = weight2 <= weight1
        
        passed = weight1_valid and weight2_valid and higher_decay_lower_weight
        
        if verbose:
            result = {
                'passed': passed,
                'details': {
                    'weight1': weight1,
                    'weight2': weight2,
                    'weight1_valid': weight1_valid,
                    'weight2_valid': weight2_valid,
                    'higher_decay_lower_weight': higher_decay_lower_weight
                }
            }
        else:
            result = {'passed': passed}
        
        return result
    except Exception as e:
        return {
            'passed': False,
            'error': str(e)
        }

def test_semantic_similarity(capability_module, verbose=False):
    """验证语义相似度计算的准确性"""
    try:
        # 测试相似的文本
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "A quick brown fox jumps over a lazy dog"
        text3 = "Completely different unrelated text"
        
        similarity_high = capability_module.calculate_semantic_similarity(text1, text2)
        similarity_low = capability_module.calculate_semantic_similarity(text1, text3)
        
        # 验证相似度在合理范围内（0-1之间）
        similarity_high_valid = 0 <= similarity_high <= 1
        similarity_low_valid = 0 <= similarity_low <= 1
        # 验证相似文本的相似度应该高于不相似文本
        similarity_order_correct = similarity_high > similarity_low
        
        passed = similarity_high_valid and similarity_low_valid and similarity_order_correct
        
        if verbose:
            result = {
                'passed': passed,
                'details': {
                    'text1': text1,
                    'text2': text2,
                    'text3': text3,
                    'similarity_high': similarity_high,
                    'similarity_low': similarity_low,
                    'similarity_high_valid': similarity_high_valid,
                    'similarity_low_valid': similarity_low_valid,
                    'similarity_order_correct': similarity_order_correct
                }
            }
        else:
            result = {'passed': passed}
        
        return result
    except Exception as e:
        return {
            'passed': False,
            'error': str(e)
        }

def test_memory_clustering(capability_module, verbose=False):
    """验证记忆聚类功能的有效性"""
    try:
        # 创建测试记忆数据
        test_memories = [
            {'id': '1', 'content': 'Learning about neural networks', 'timestamp': time.time() - 1000},
            {'id': '2', 'content': 'Neural network architectures', 'timestamp': time.time() - 900},
            {'id': '3', 'content': 'Cooking pasta recipe', 'timestamp': time.time() - 800},
            {'id': '4', 'content': 'Types of pasta', 'timestamp': time.time() - 700},
            {'id': '5', 'content': 'Machine learning concepts', 'timestamp': time.time() - 600}
        ]
        
        # 执行聚类
        clusters = capability_module.cluster_similar_memories(test_memories, threshold=0.5)
        
        # 验证返回结果的基本结构
        is_list = isinstance(clusters, list)
        all_clusters_are_lists = all(isinstance(cluster, list) for cluster in clusters)
        cluster_content_preserved = all(
            all('id' in memory and 'content' in memory for memory in cluster)
            for cluster in clusters
        )
        
        passed = is_list and all_clusters_are_lists and cluster_content_preserved
        
        if verbose:
            result = {
                'passed': passed,
                'details': {
                    'input_memories': test_memories,
                    'clusters': clusters,
                    'num_clusters': len(clusters),
                    'is_list': is_list,
                    'all_clusters_are_lists': all_clusters_are_lists,
                    'cluster_content_preserved': cluster_content_preserved
                }
            }
        else:
            result = {'passed': passed}
        
        return result
    except Exception as e:
        return {
            'passed': False,
            'error': str(e)
        }

def test_batch_weighting(capability_module, verbose=False):
    """验证批量权重计算的性能和正确性"""
    try:
        # 创建测试记忆数据
        test_memories = [
            {'id': '1', 'content': 'Important memory about algorithms', 'timestamp': time.time() - 300},
            {'id': '2', 'content': 'Less important memory', 'timestamp': time.time() - 600},
            {'id': '3', 'content': 'Another algorithm concept', 'timestamp': time.time() - 100},
            {'id': '4', 'content': 'Random note', 'timestamp': time.time() - 1200}
        ]
        
        context = "Learning about algorithms and data structures"
        
        # 计算批量权重
        weighted_results = capability_module.calculate_memory_weights_batch(
            test_memories, context, current_time=time.time(), time_decay_rate=0.1
        )
        
        # 验证结果结构
        is_list = isinstance(weighted_results, list)
        correct_length = len(weighted_results) == len(test_memories)
        all_have_weights = all('weight' in item for item in weighted_results)
        all_weights_valid = all(0 <= item['weight'] <= 1 for item in weighted_results)
        
        passed = is_list and correct_length and all_have_weights and all_weights_valid
        
        if verbose:
            result = {
                'passed': passed,
                'details': {
                    'input_memories': test_memories,
                    'context': context,
                    'weighted_results': weighted_results,
                    'is_list': is_list,
                    'correct_length': correct_length,
                    'all_have_weights': all_have_weights,
                    'all_weights_valid': all_weights_valid
                }
            }
        else:
            result = {'passed': passed}
        
        return result
    except Exception as e:
        return {
            'passed': False,
            'error': str(e)
        }

def test_full_cycle(capability_module, verbose=False):
    """验证完整记忆权重计算周期的端到端功能"""
    try:
        # 创建测试记忆数据
        test_memories = [
            {'id': '1', 'content': 'Machine learning research', 'timestamp': time.time() - 100},
            {'id': '2', 'content': 'Deep learning techniques', 'timestamp': time.time() - 200},
            {'id': '3', 'content': 'Cooking recipe', 'timestamp': time.time() - 1000},
            {'id': '4', 'content': 'Neural network architecture', 'timestamp': time.time() - 150},
            {'id': '5', 'content': 'Different pasta types', 'timestamp': time.time() - 900}
        ]
        
        context = "Researching machine learning approaches"
        
        # 运行完整记忆权重计算周期
        result = capability_module.run_dynamic_memory_weighting_cycle(
            test_memories, 
            context
        )
        
        # 验证结果结构
        has_weighted_memories = 'weighted_memories' in result
        has_clusters = 'memory_clusters' in result
        has_continuity_score = 'continuity_score' in result
        
        if has_weighted_memories:
            weighted_memories_valid = isinstance(result['weighted_memories'], list)
            all_weighted_have_weights = all('weight' in mem for mem in result['weighted_memories'])
        else:
            weighted_memories_valid = False
            all_weighted_have_weights = False
        
        if has_clusters:
            clusters_valid = isinstance(result['memory_clusters'], list)
        else:
            clusters_valid = False
        
        passed = has_weighted_memories and has_clusters and has_continuity_score and \
                weighted_memories_valid and all_weighted_have_weights and clusters_valid
        
        if verbose:
            result_details = {
                'passed': passed,
                'details': {
                    'input_memories': test_memories,
                    'context': context,
                    'result': result,
                    'has_weighted_memories': has_weighted_memories,
                    'has_clusters': has_clusters,
                    'has_continuity_score': has_continuity_score,
                    'weighted_memories_valid': weighted_memories_valid,
                    'all_weighted_have_weights': all_weighted_have_weights,
                    'clusters_valid': clusters_valid
                }
            }
        else:
            result_details = {'passed': passed}
        
        return result_details
    except Exception as e:
        return {
            'passed': False,
            'error': str(e)
        }