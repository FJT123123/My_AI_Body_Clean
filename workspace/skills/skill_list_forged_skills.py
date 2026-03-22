"""
自动生成的技能模块
需求: 列出所有已锻造的技能模块，提供正确的模块路径和名称映射，用于API防御验证工具的依赖解析
生成时间: 2026-03-21 22:22:44
"""

# skill_name: list_forged_skills
import os
import json
import sqlite3

def main(args=None):
    """
    列出所有已锻造的技能模块，提供正确的模块路径和名称映射，用于API防御验证工具的依赖解析
    """
    args = args or {}
    context = args.get('__context__', {})
    db_path = context.get('db_path', '')
    
    # 检查数据库路径是否有效
    if not db_path or not os.path.exists(db_path):
        return {
            'result': {'error': 'db_path 不可用'},
            'insights': ['无法访问数据库'],
            'next_skills': []
        }
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        
        # 查询所有已锻造的技能
        skill_query = """
        SELECT id, skill_name, input_args, result_json, timestamp
        FROM skill_results
        WHERE skill_name LIKE 'skill_%'
        ORDER BY timestamp DESC
        """
        
        # 同时查询记忆表中的技能锻造记录
        memory_query = """
        SELECT content, timestamp, tags
        FROM memories
        WHERE event_type IN ('skill_forged', 'skill_forge_failed', 'skill_executed')
        ORDER BY timestamp DESC
        """
        
        # 执行查询
        skill_rows = conn.execute(skill_query).fetchall()
        memory_rows = conn.execute(memory_query).fetchall()
        
        # 处理技能结果表中的数据
        skills_from_results = []
        for row in skill_rows:
            try:
                skill_info = {
                    'id': row[0],
                    'skill_name': row[1],
                    'module_path': f"skills/{row[1]}.py" if row[1] else "",
                    'last_used': row[4],
                    'status': 'available'
                }
                skills_from_results.append(skill_info)
            except Exception:
                continue
        
        # 处理记忆表中的技能锻造记录
        skills_from_memories = []
        for row in memory_rows:
            try:
                content = json.loads(row[0]) if isinstance(row[0], str) and row[0].startswith('{') else row[0]
                if isinstance(content, dict):
                    skill_name = content.get('skill_name', content.get('name', ''))
                else:
                    skill_name = ''
                
                if skill_name and skill_name.startswith('skill_'):
                    skill_info = {
                        'skill_name': skill_name,
                        'module_path': f"skills/{skill_name}.py",
                        'timestamp': row[1],
                        'event_type': row[2] if row[2] else 'unknown'
                    }
                    skills_from_memories.append(skill_info)
            except Exception:
                continue
        
        # 去重并合并所有技能
        all_skills = {}
        
        # 先添加技能结果表中的技能
        for skill in skills_from_results:
            skill_name = skill['skill_name']
            if skill_name not in all_skills:
                all_skills[skill_name] = skill
            else:
                # 如果已有记录，更新时间戳
                if skill.get('last_used') and skill['last_used'] > all_skills[skill_name].get('last_used', ''):
                    all_skills[skill_name].update(skill)
        
        # 再添加记忆表中的技能
        for skill in skills_from_memories:
            skill_name = skill['skill_name']
            if skill_name not in all_skills:
                all_skills[skill_name] = skill
            else:
                # 合并信息
                all_skills[skill_name].update({
                    'event_type': skill.get('event_type', all_skills[skill_name].get('event_type')),
                    'timestamp': skill.get('timestamp', all_skills[skill_name].get('timestamp'))
                })
        
        # 构建最终技能列表
        final_skills = list(all_skills.values())
        
        # 检查实际文件是否存在
        for skill in final_skills:
            module_path = skill.get('module_path', '')
            if module_path:
                skill['file_exists'] = os.path.exists(module_path)
                skill['status'] = 'available' if skill['file_exists'] else 'missing'
        
        # 按技能名称排序
        final_skills.sort(key=lambda x: x['skill_name'])
        
        # 统计信息
        total_skills = len(final_skills)
        available_skills = len([s for s in final_skills if s.get('status') == 'available'])
        missing_skills = len([s for s in final_skills if s.get('status') == 'missing'])
        
        conn.close()
        
        return {
            'result': {
                'skills': final_skills,
                'statistics': {
                    'total_count': total_skills,
                    'available_count': available_skills,
                    'missing_count': missing_skills
                }
            },
            'insights': [
                f'共发现 {total_skills} 个技能模块，其中 {available_skills} 个可用，{missing_skills} 个缺失',
                '技能列表可用于API防御验证工具的依赖解析'
            ],
            'facts': [
                ['skill_registry', 'contains', f'{total_skills} skills'],
                ['skill_registry', 'has_available', f'{available_skills} skills'],
                ['skill_registry', 'has_missing', f'{missing_skills} skills']
            ],
            'next_skills': ['skill_api_defense_validation'] if available_skills > 0 else ['skill_forge_missing_modules']
        }
        
    except Exception as e:
        return {
            'result': {'error': f'查询技能列表失败: {str(e)}'},
            'insights': ['数据库查询失败，无法获取技能列表'],
            'next_skills': []
        }