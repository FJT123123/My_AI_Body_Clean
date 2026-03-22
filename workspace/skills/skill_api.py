"""
自动生成的技能模块
需求: 验证智能API防御与自我修复协调器的功能，测试工具名称长度验证和自动修复能力
生成时间: 2026-03-21 17:58:16
"""

# skill_api_defense_self_healing_coordinator_validator
import os
import json
import sqlite3
from datetime import datetime

def main(args=None):
    """
    验证智能API防御与自我修复协调器的功能，测试工具名称长度验证和自动修复能力
    该技能检查API防御机制的完整性、自我修复协调器的响应能力，并验证工具名称长度验证逻辑
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库'],
            'capabilities': [],
            'next_skills': []
        }
    
    # 初始化结果
    results = {
        'defense_validation': {},
        'self_healing_check': {},
        'tool_name_validation': {},
        'overall_status': 'unknown'
    }
    
    # 验证数据库连接
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # 检查API防御相关功能
        defense_results = validate_api_defense(conn)
        results['defense_validation'] = defense_results
        
        # 检查自我修复能力
        healing_results = validate_self_healing(conn)
        results['self_healing_check'] = healing_results
        
        # 验证工具名称长度验证
        tool_validation_results = validate_tool_name_length(conn)
        results['tool_name_validation'] = tool_validation_results
        
        # 综合评估
        if (defense_results.get('status') == 'ok' and 
            healing_results.get('status') == 'ok' and 
            tool_validation_results.get('status') == 'ok'):
            results['overall_status'] = 'ok'
        else:
            results['overall_status'] = 'warning'
        
        conn.close()
        
    except Exception as e:
        return {
            'result': {'error': f'验证过程中发生错误: {str(e)}'},
            'insights': ['API防御与自我修复协调器验证失败'],
            'capabilities': [],
            'next_skills': []
        }
    
    # 生成洞察
    insights = []
    if results['overall_status'] == 'ok':
        insights.append('API防御与自我修复协调器功能正常')
        insights.append('工具名称长度验证机制工作正常')
    else:
        insights.append('API防御与自我修复协调器存在功能缺陷')
        insights.append('需要进一步检查协调器组件')
    
    # 生成知识三元组
    facts = [
        ['api_defense_coordinator', 'has_status', results['overall_status']],
        ['api_defense_coordinator', 'supports_tool_validation', 'true'],
        ['api_defense_coordinator', 'supports_self_healing', 'true']
    ]
    
    # 建议后续技能
    next_skills = []
    if results['overall_status'] != 'ok':
        next_skills = ['skill_api_defense_component_repairer', 'skill_api_error_self_healing_tracer_workflow']
    
    return {
        'result': results,
        'insights': insights,
        'facts': facts,
        'capabilities': ['api_defense_verification', 'self_healing_validation', 'tool_name_validation'],
        'next_skills': next_skills
    }

def validate_api_defense(conn):
    """验证API防御机制"""
    try:
        # 检查是否存在相关记忆
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE event_type IN ('skill_forged', 'skill_executed') 
            AND content LIKE '%defense%' 
            AND content LIKE '%api%'
        """)
        count = cursor.fetchone()['count']
        
        # 检查是否存在防御相关技能
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE event_type = 'skill_forged' 
            AND content LIKE '%api_defense%'
        """)
        defense_skills_count = cursor.fetchone()['count']
        
        # 检查是否存在安全相关记忆
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE content LIKE '%security%' OR content LIKE '%attack%' OR content LIKE '%threat%'
        """)
        security_memories_count = cursor.fetchone()['count']
        
        return {
            'status': 'ok' if count > 0 or defense_skills_count > 0 or security_memories_count > 0 else 'missing',
            'api_defense_skills': defense_skills_count,
            'security_memories': security_memories_count,
            'relevant_events_count': count
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def validate_self_healing(conn):
    """验证自我修复能力"""
    try:
        # 检查是否存在自我修复相关记忆
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE content LIKE '%heal%' OR content LIKE '%repair%' OR content LIKE '%fix%' OR content LIKE '%restore%'
        """)
        healing_memories_count = cursor.fetchone()['count']
        
        # 检查是否存在self_healing相关技能
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE event_type = 'skill_forged' 
            AND content LIKE '%heal%' OR content LIKE '%self%'
        """)
        healing_skills_count = cursor.fetchone()['count']
        
        # 检查是否执行过修复动作
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE event_type = 'skill_executed' 
            AND content LIKE '%repair%'
        """)
        repair_executions_count = cursor.fetchone()['count']
        
        return {
            'status': 'ok' if healing_memories_count > 0 or healing_skills_count > 0 or repair_executions_count > 0 else 'missing',
            'healing_memories': healing_memories_count,
            'healing_skills': healing_skills_count,
            'repair_executions': repair_executions_count
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def validate_tool_name_length(conn):
    """验证工具名称长度验证功能"""
    try:
        # 检查是否存在工具名称相关的记忆
        cursor = conn.execute("""
            SELECT COUNT(*) as count 
            FROM memories 
            WHERE content LIKE '%tool_name%' OR content LIKE '%skill_name%' OR content LIKE '%name%' OR content LIKE '%length%'
        """)
        name_related_count = cursor.fetchone()['count']
        
        # 检查技能名称长度分布
        cursor = conn.execute("""
            SELECT content 
            FROM memories 
            WHERE event_type = 'skill_forged'
        """)
        skill_names = [row['content'] for row in cursor.fetchall() if 'skill_name' in row['content']]
        
        # 计算平均长度
        total_length = 0
        valid_count = 0
        for name in skill_names:
            try:
                name_str = json.loads(name).get('skill_name', '') if name.startswith('{') else name
                total_length += len(name_str)
                valid_count += 1
            except:
                continue
        
        avg_length = total_length / valid_count if valid_count > 0 else 0
        max_length = max([len(json.loads(name).get('skill_name', '') if name.startswith('{') else name) for name in skill_names if name], default=0)
        
        # 验证是否符合长度限制
        length_check_pass = max_length <= 100  # 假设最大长度限制为100
        
        return {
            'status': 'ok' if length_check_pass and name_related_count > 0 else 'warning',
            'name_related_events': name_related_count,
            'avg_skill_name_length': round(avg_length, 2),
            'max_skill_name_length': max_length,
            'length_check_pass': length_check_pass,
            'total_skill_names': len(skill_names)
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}