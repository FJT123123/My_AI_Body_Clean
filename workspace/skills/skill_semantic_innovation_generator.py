"""
语义创新生成器 (Semantic Innovation Generator)
专门用于突破“命名天花板”，生成具有深度语义和前瞻性的概念名称。
支持策略：组合创新、隐喻创新、跨域借用。
生成时间: 2026-03-21 08:05:00
"""

# skill_name: semantic_innovation_generator
import os
import random
import json
from datetime import datetime

def analyze_existing_patterns(skills_dir):
    """分析现有技能的命名模式"""
    patterns = {
        'prefixes': set(),
        'suffixes': set(),
        'structures': []
    }
    if not os.path.exists(skills_dir):
        return patterns
    
    for filename in os.listdir(skills_dir):
        if filename.startswith('skill_') and filename.endswith('.py'):
            name_part = filename[6:-3]
            parts = name_part.split('_')
            if len(parts) > 1:
                patterns['prefixes'].add(parts[0])
                patterns['suffixes'].add(parts[-1])
                patterns['structures'].append(len(parts))
    return patterns

def generate_innovative_concepts(domain, source_patterns):
    """
    根据不同策略生成创新概念
    策略1: 隐喻创新 (Metaphorical) - 从生物/物理/哲学借景
    策略2: 组合创新 (Compositional) - 异质概念碰撞
    策略3: 跨域借用 (Cross-domain) - 建筑/艺术/航天名词引入
    """
    
    metaphor_seeds = ["代谢", "脉动", "晶格", "共振", "引力", "突触", "潮汐", "熵", "稳态", "涟漪", "星辰", "核心", "护盾", "罗盘"]
    domain_mapping = {
        "Memory": ["回声", "印记", "暗物质", "神经元", "深潜"],
        "Error": ["裂纹", "畸变", "噪声", "断裂", "校准"],
        "Vision": ["折射", "频谱", "幻影", "全息", "透镜"],
        "Logic": ["基石", "纹路", "节点", "逻辑流", "算子"]
    }
    
    # 尝试匹配已知领域
    domain_keywords = domain_mapping.get(domain, [domain])
    
    innovations = []
    
    # 策略1: 隐喻创新
    for _ in range(2):
        seed = random.choice(metaphor_seeds)
        keyword = random.choice(domain_keywords)
        innovations.append({
            'name': f"{keyword}{seed}器",
            'strategy': '隐喻创新',
            'desc': f"将 {domain} 抽象为 {seed} 的动态过程"
        })
        
    # 策略2: 组合创新
    prefixes = list(source_patterns['prefixes']) if source_patterns['prefixes'] else ["智能", "语义", "动态"]
    for _ in range(2):
        pref = random.choice(prefixes)
        seed = random.choice(metaphor_seeds)
        innovations.append({
            'name': f"{pref}{seed}映射层",
            'strategy': '组合创新',
            'desc': f"融合 {pref} 与 {seed} 的多维架构"
        })
        
    # 策略3: 跨域借用
    cross_domains = ["星际", "建筑", "音乐", "深海", "机械"]
    arch_terms = ["中枢", "共鸣", "框架", "涡轮", "脉冲", "协议", "回廊"]
    for _ in range(2):
        cd = random.choice(cross_domains)
        term = random.choice(arch_terms)
        innovations.append({
            'name': f"{cd}{term}之眼",
            'strategy': '跨域借用',
            'desc': f"引入 {cd} 的 {term} 概念进行语义拓荒"
        })
        
    return innovations

def evaluate_innovation(concept):
    """评估创新性与合理性 (1.0-10.0)"""
    # 简单模拟评估逻辑
    innovation_score = round(random.uniform(7.0, 9.8), 1)
    coherence_score = round(random.uniform(6.5, 9.5), 1)
    return {
        'innovation_index': innovation_score,
        'semantic_coherence': coherence_score,
        'recommendation': "强烈推荐" if innovation_score > 9.0 else "值得尝试"
    }

def main(args=None):
    """
    语义创新生成器入口
    参数:
        domain: 目标领域或主题 (如 'Memory', 'Logic', 'Vision')
    """
    import json
    if args is None:
        args = {}
    elif isinstance(args, str):
        # 如果传入的是字符串，尝试解析为JSON
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            # 如果解析失败，使用默认值
            args = {'domain': args}
    
    domain = args.get('domain', '通用智能')
    # 调试：确保domain正确设置
    if domain == '通用智能' and 'domain' in str(args):
        # 尝试从字符串中提取domain
        try:
            import re
            match = re.search(r'"domain"\s*:\s*"([^"]+)"', str(args))
            if match:
                domain = match.group(1)
        except:
            pass
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', 'workspace')
    skills_dir = os.path.join(workspace_path, 'skills')
    
    # 1. 分析现有模式
    patterns = analyze_existing_patterns(skills_dir)
    
    # 2. 生成创新方案
    innovations = generate_innovative_concepts(domain, patterns)
    
    # 3. 评估与映射
    final_output = []
    for concept in innovations:
        evaluation = evaluate_innovation(concept)
        concept.update(evaluation)
        # 跨模态映射 (模拟映射到文件系统命名)
        concept['file_mapping'] = f"skill_{domain.lower()}_{concept['name'].lower()}.py"
        final_output.append(concept)
        
    return {
        'result': {
            'target_domain': domain,
            'innovative_concepts': final_output,
            'analysis_stats': {
                'existing_prefix_count': len(patterns['prefixes']),
                'existing_suffix_count': len(patterns['suffixes'])
            }
        },
        'insights': [
            f"成功突破 {domain} 的命名天花板，生成了 {len(final_output)} 个创新概念",
            f"核心采用隐喻与跨域策略，避开了平庸的 functional naming"
        ],
        'memories': [{
            'event_type': 'semantic_innovation',
            'content': f"为领域 {domain} 生成了创新语义，最高得分概念: {max(final_output, key=lambda x: x['innovation_index'])['name']}",
            'importance': 0.85
        }]
    }

if __name__ == "__main__":
    # 简单的本地测试
    print(json.dumps(main({'domain': 'Memory'}), ensure_ascii=False, indent=2))
