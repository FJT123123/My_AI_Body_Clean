"""
语义创新和概念生成能力模块
专门用于突破命名天花板，生成新颖、有意义的概念名称和表达方式
"""

import json
import re
from typing import List, Dict, Any, Optional

def analyze_naming_patterns(concept_domain: str) -> Dict[str, Any]:
    """
    分析特定概念领域的现有命名模式和语义结构
    
    Args:
        concept_domain: 概念领域或主题
        
    Returns:
        包含命名模式分析结果的字典
    """
    # 基本分析逻辑
    patterns = {
        'prefixes': [],
        'suffixes': [],
        'root_words': [],
        'metaphors': [],
        'constraints': []
    }
    
    # 简单的模式识别（实际应用中可以更复杂）
    if 'ai' in concept_domain.lower() or 'artificial intelligence' in concept_domain.lower():
        patterns['prefixes'] = ['neuro', 'deep', 'quantum', 'cognitive', 'adaptive']
        patterns['suffixes'] = ['net', 'mind', 'brain', 'agent', 'system']
        patterns['root_words'] = ['learn', 'think', 'reason', 'perceive', 'create']
        patterns['metaphors'] = ['brain', 'mind', 'network', 'ecosystem', 'organism']
        patterns['constraints'] = ['avoid anthropomorphism', 'prefer descriptive over metaphorical', 'ensure technical accuracy']
    
    elif 'digital' in concept_domain.lower() or 'virtual' in concept_domain.lower():
        patterns['prefixes'] = ['cyber', 'meta', 'hyper', 'ultra', 'nano']
        patterns['suffixes'] = ['verse', 'space', 'world', 'realm', 'domain']
        patterns['root_words'] = ['connect', 'interact', 'simulate', 'represent', 'transform']
        patterns['metaphors'] = ['ocean', 'web', 'cloud', 'mirror', 'portal']
        patterns['constraints'] = ['avoid overused terms like "metaverse"', 'ensure clarity', 'consider cultural implications']
    
    else:
        # 通用模式
        patterns['prefixes'] = ['neo', 'ultra', 'hyper', 'meta', 'proto']
        patterns['suffixes'] = ['sphere', 'plex', 'flux', 'nexus', 'matrix']
        patterns['root_words'] = ['create', 'build', 'design', 'develop', 'innovate']
        patterns['metaphors'] = ['journey', 'bridge', 'key', 'light', 'foundation']
        patterns['constraints'] = ['ensure pronounceability', 'avoid trademark conflicts', 'consider global accessibility']
    
    return {
        'domain': concept_domain,
        'patterns': patterns,
        'analysis_summary': f"Identified naming patterns for {concept_domain} domain"
    }

def generate_innovative_names(concept_description: str, strategies: List[str] = None) -> List[str]:
    """
    应用多种创新策略生成新颖、有意义的新概念名称
    
    Args:
        concept_description: 概念描述
        strategies: 创新策略列表，可选值包括:
            - 'combination': 词根组合
            - 'metaphor': 隐喻映射  
            - 'cross_domain': 跨域借用
            - 'phonetic': 音韵创新
            
    Returns:
        生成的新概念名称列表
    """
    if strategies is None:
        strategies = ['combination', 'metaphor', 'cross_domain', 'phonetic']
    
    # 提取关键词
    keywords = extract_keywords(concept_description)
    
    # 基于概念领域分析命名模式
    domain_analysis = analyze_naming_patterns(concept_description)
    patterns = domain_analysis['patterns']
    
    generated_names = []
    
    # 组合策略
    if 'combination' in strategies:
        for prefix in patterns['prefixes'][:3]:
            for root in patterns['root_words'][:3]:
                for suffix in patterns['suffixes'][:3]:
                    name = f"{prefix}{root}{suffix}"
                    generated_names.append(name.capitalize())
        
        # 关键词组合
        for i, kw1 in enumerate(keywords[:3]):
            for kw2 in keywords[i+1:i+2]:
                if kw1 and kw2:
                    generated_names.append(f"{kw1.capitalize()}{kw2.capitalize()}")
                    generated_names.append(f"{kw2.capitalize()}{kw1.capitalize()}")
    
    # 隐喻策略
    if 'metaphor' in strategies:
        for metaphor in patterns['metaphors'][:5]:
            for keyword in keywords[:3]:
                if keyword:
                    generated_names.append(f"{metaphor.capitalize()}{keyword.capitalize()}")
                    generated_names.append(f"{keyword.capitalize()}{metaphor.capitalize()}")
    
    # 跨域借用策略
    if 'cross_domain' in strategies:
        cross_domains = ['nature', 'music', 'architecture', 'mathematics', 'mythology']
        for domain in cross_domains[:3]:
            domain_prefixes = {
                'nature': ['eco', 'bio', 'geo', 'astro'],
                'music': ['sonic', 'harmonic', 'rhythmic', 'melodic'],
                'architecture': ['archi', 'struct', 'form', 'design'],
                'mathematics': ['algo', 'quant', 'logic', 'vector'],
                'mythology': ['olympic', 'cosmic', 'divine', 'legendary']
            }
            for prefix in domain_prefixes.get(domain, [])[:2]:
                for keyword in keywords[:2]:
                    if keyword:
                        generated_names.append(f"{prefix.capitalize()}{keyword.capitalize()}")
    
    # 音韵创新策略
    if 'phonetic' in strategies:
        phonetic_patterns = ['zen', 'vox', 'lum', 'nova', 'aura', 'quantum', 'synth']
        for pattern in phonetic_patterns[:4]:
            for keyword in keywords[:2]:
                if keyword:
                    generated_names.append(f"{pattern.capitalize()}{keyword.capitalize()}")
                    generated_names.append(f"{keyword.capitalize()}{pattern.capitalize()}")
    
    # 去重并返回
    return list(set(generated_names))[:20]

def extract_keywords(text: str) -> List[str]:
    """提取文本中的关键词"""
    # 简单的关键词提取（实际应用中可以使用NLP技术）
    words = re.findall(r'\b\w+\b', text.lower())
    # 过滤常见停用词
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
    keywords = [word for word in words if word not in stopwords and len(word) > 2]
    return keywords[:10]

def evaluate_semantic_validity(new_concepts: List[str], context: str = "") -> Dict[str, Any]:
    """
    评估新生成概念的语义合理性和创新性
    
    Args:
        new_concepts: 新概念名称列表
        context: 上下文信息
        
    Returns:
        包含评估结果的字典
    """
    evaluations = {}
    
    for concept in new_concepts:
        # 简单的评估逻辑
        score = 0.0
        feedback = []
        
        # 长度合理性
        if 3 <= len(concept) <= 20:
            score += 0.2
        else:
            feedback.append("Length may be suboptimal")
        
        # 可发音性（简单检查）
        if re.search(r'[aeiou]', concept.lower()):
            score += 0.2
        else:
            feedback.append("May be difficult to pronounce")
        
        # 创新性（避免常见模式）
        common_patterns = ['ai', 'smart', 'intelligent', 'digital', 'virtual', 'cyber']
        if not any(pattern in concept.lower() for pattern in common_patterns):
            score += 0.3
            feedback.append("High innovation - avoids common patterns")
        else:
            feedback.append("Uses common patterns - lower innovation")
        
        # 语义相关性（简单检查）
        if context:
            context_keywords = extract_keywords(context)
            concept_lower = concept.lower()
            if any(kw in concept_lower for kw in context_keywords):
                score += 0.3
                feedback.append("Good semantic relevance to context")
            else:
                feedback.append("Limited semantic connection to context")
        
        evaluations[concept] = {
            'validity_score': min(score, 1.0),
            'feedback': feedback,
            'is_valid': score >= 0.5
        }
    
    return {
        'evaluations': evaluations,
        'summary': f"Evaluated {len(new_concepts)} concepts",
        'valid_concepts': [c for c, e in evaluations.items() if e['is_valid']],
        'best_concepts': sorted(evaluations.items(), key=lambda x: x[1]['validity_score'], reverse=True)[:5]
    }

def cross_modal_mapping(source_modality: str, target_modality: str, concept: str) -> Dict[str, Any]:
    """
    支持跨模态的概念映射
    
    Args:
        source_modality: 源模态（如 'visual', 'auditory', 'tactile'）
        target_modality: 目标模态（通常是 'linguistic'）
        concept: 要映射的概念
        
    Returns:
        包含映射结果的字典
    """
    # 简单的跨模态映射逻辑
    modality_mappings = {
        'visual': {
            'bright': ['luminous', 'radiant', 'brilliant', 'gleaming'],
            'dark': ['shadowy', 'obscure', 'mysterious', 'profound'],
            'fast': ['rapid', 'swift', 'nimble', 'agile'],
            'slow': ['gradual', 'leisurely', 'deliberate', 'methodical'],
            'complex': ['intricate', 'sophisticated', 'elaborate', 'multifaceted']
        },
        'auditory': {
            'loud': ['powerful', 'intense', 'forceful', 'resonant'],
            'soft': ['gentle', 'subtle', 'delicate', 'whispering'],
            'harmonic': ['balanced', 'coherent', 'symphonic', 'unified'],
            'chaotic': ['disordered', 'unpredictable', 'turbulent', 'fragmented']
        },
        'tactile': {
            'smooth': ['fluid', 'seamless', 'graceful', 'elegant'],
            'rough': ['raw', 'authentic', 'unrefined', 'textured'],
            'warm': ['inviting', 'comfortable', 'nurturing', 'accessible'],
            'cold': ['precise', 'analytical', 'detached', 'efficient']
        }
    }
    
    mappings = modality_mappings.get(source_modality, {})
    related_terms = []
    
    # 查找相关术语
    concept_lower = concept.lower()
    for key, terms in mappings.items():
        if key in concept_lower:
            related_terms.extend(terms)
        elif any(c in key for c in concept_lower.split()):
            related_terms.extend(terms)
    
    # 如果没有找到直接匹配，尝试更宽松的匹配
    if not related_terms:
        all_terms = []
        for terms in mappings.values():
            all_terms.extend(terms)
        related_terms = all_terms[:5]  # 返回前5个通用术语
    
    return {
        'source_modality': source_modality,
        'target_modality': target_modality,
        'original_concept': concept,
        'mapped_terms': list(set(related_terms)),
        'mapping_confidence': min(len(related_terms) / 5.0, 1.0)
    }

def break_naming_ceiling(input_concept: str, context: str = "", strategies: List[str] = None) -> Dict[str, Any]:
    """
    主函数：突破命名天花板
    
    Args:
        input_concept: 输入概念或主题
        context: 上下文信息
        strategies: 创新策略列表
        
    Returns:
        包含完整突破命名天花板过程和结果的字典
    """
    if strategies is None:
        strategies = ['combination', 'metaphor', 'cross_domain', 'phonetic']
    
    # 1. 分析命名模式
    pattern_analysis = analyze_naming_patterns(input_concept)
    
    # 2. 生成创新名称
    generated_names = generate_innovative_names(input_concept, strategies)
    
    # 3. 评估语义有效性
    evaluation_results = evaluate_semantic_validity(generated_names, context)
    
    # 4. 跨模态映射（如果提供了上下文）
    cross_modal_results = None
    if context:
        # 尝试不同的源模态
        for modality in ['visual', 'auditory', 'tactile']:
            cross_modal_results = cross_modal_mapping(modality, 'linguistic', input_concept)
            if cross_modal_results['mapped_terms']:
                break
    
    # 5. 整合结果
    result = {
        'input_concept': input_concept,
        'context': context,
        'strategies_used': strategies,
        'pattern_analysis': pattern_analysis,
        'generated_names': generated_names,
        'evaluation_results': evaluation_results,
        'cross_modal_mapping': cross_modal_results,
        'breakthrough_summary': {
            'total_generated': len(generated_names),
            'valid_concepts': len(evaluation_results['valid_concepts']),
            'best_concepts': [c[0] for c in evaluation_results['best_concepts']],
            'innovation_level': 'high' if len(evaluation_results['valid_concepts']) >= 5 else 'medium' if len(evaluation_results['valid_concepts']) >= 2 else 'low'
        }
    }
    
    return result

# 兼容性接口
def main(input_args: str = "") -> Dict[str, Any]:
    """
    主函数接口，用于与其他系统集成
    
    Args:
        input_args: JSON字符串，包含input_concept, context, strategies等参数
        
    Returns:
        处理结果字典
    """
    try:
        if isinstance(input_args, str) and input_args.strip():
            params = json.loads(input_args)
        elif isinstance(input_args, dict):
            params = input_args
        else:
            params = {}
    except (json.JSONDecodeError, TypeError):
        params = {}
    
    input_concept = params.get('input_concept', '')
    context = params.get('context', '')
    strategies = params.get('strategies', ['combination', 'metaphor', 'cross_domain', 'phonetic'])
    
    if not input_concept:
        return {
            'result': {'error': 'Missing required parameter: input_concept'},
            'insights': ['Input concept is required for semantic innovation'],
            'facts': [],
            'memories': []
        }
    
    try:
        result = break_naming_ceiling(input_concept, context, strategies)
        return {
            'result': result,
            'insights': [
                f"Generated {len(result['generated_names'])} innovative concept names",
                f"Found {len(result['evaluation_results']['valid_concepts'])} semantically valid concepts",
                f"Best concepts: {', '.join(result['breakthrough_summary']['best_concepts'][:3])}"
            ],
            'facts': [
                ['semantic_innovation', 'generated_concepts_count', str(len(result['generated_names']))],
                ['semantic_innovation', 'valid_concepts_count', str(len(result['evaluation_results']['valid_concepts']))],
                ['semantic_innovation', 'innovation_level', result['breakthrough_summary']['innovation_level']]
            ],
            'memories': [
                f"Semantic innovation breakthrough for '{input_concept}': {len(result['generated_names'])} concepts generated",
                f"Best innovative names: {', '.join(result['breakthrough_summary']['best_concepts'][:3])}"
            ]
        }
    except Exception as e:
        return {
            'result': {'error': f'Semantic innovation failed: {str(e)}'},
            'insights': ['Error occurred during semantic innovation process'],
            'facts': [],
            'memories': []
        }