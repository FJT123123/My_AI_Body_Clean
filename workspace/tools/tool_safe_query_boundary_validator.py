# tool_name: safe_query_boundary_validator
from langchain.tools import tool
import json
import re
from typing import Dict, Any, List

@tool
def safe_query_boundary_validator(input_args: str) -> Dict[str, Any]:
    """
    安全查询边界验证工具 - 确保认知权重驱动的动态记忆淘汰与SQLite索引协同优化中的查询安全性
    
    Args:
        input_args: JSON字符串，包含以下参数:
            - query_pattern: 查询模式字符串
            - context: 查询上下文
            - memory_table: 记忆表名，默认'memory_embeddings'
            - max_results: 最大结果数，默认1000
            - safety_level: 安全级别，默认'strict'
    
    Returns:
        dict: 包含验证结果、安全查询模板、验证详情等信息
    """
    try:
        # 解析输入参数
        if isinstance(input_args, str):
            params = json.loads(input_args)
        else:
            params = input_args
        
        # 提取必要参数
        query_pattern = params.get('query_pattern', '')
        context = params.get('context', '')
        memory_table = params.get('memory_table', 'memory_embeddings')
        max_results = params.get('max_results', 1000)
        safety_level = params.get('safety_level', 'strict')
        
        # 验证查询模式的安全性
        validation_result = validate_query_safety(query_pattern, safety_level)
        if not validation_result['is_safe']:
            return {
                'result': {'error': f'不安全的查询模式: {validation_result["reason"]}'},
                'insights': [f'查询安全验证失败: {validation_result["reason"]}'],
                'facts': [],
                'memories': []
            }
        
        # 验证查询与索引的协同性
        index_validation = validate_index_synergy(query_pattern, memory_table)
        
        # 构建安全的查询模板
        safe_query_template = build_safe_query_template(
            query_pattern, 
            memory_table, 
            max_results
        )
        
        return {
            'result': {
                'is_safe': True,
                'safe_query_template': safe_query_template,
                'validation_details': {
                    'query_safety': validation_result,
                    'index_synergy': index_validation
                }
            },
            'insights': [
                f'成功验证查询边界安全性 (级别: {safety_level})',
                f'查询模板已优化以利用现有索引: {", ".join(index_validation.get("used_indexes", []))}'
            ],
            'facts': [
                f'safe_query_boundary_validator validated query pattern: {query_pattern}',
                f'max_results_limit: {max_results}',
                f'safety_level: {safety_level}'
            ],
            'memories': [
                '建立了安全查询边界验证框架，防止破坏性SQL操作',
                '实现了查询模式与SQLite索引的协同优化验证'
            ]
        }
        
    except Exception as e:
        return {
            'result': {'error': f'查询边界验证失败: {str(e)}'},
            'insights': [f'查询边界验证异常: {str(e)}'],
            'facts': [],
            'memories': []
        }

def validate_query_safety(query_pattern: str, safety_level: str = 'strict') -> Dict[str, Any]:
    """验证查询模式的安全性"""
    # 检查危险关键字
    dangerous_keywords = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 
        'TRUNCATE', 'EXEC', 'EXECUTE', 'xp_', 'sp_', ';', '--', '/*', '*/'
    ]
    
    query_upper = query_pattern.upper()
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return {
                'is_safe': False,
                'reason': f'包含危险关键字: {keyword}',
                'detected_keyword': keyword
            }
    
    # 检查SQL注入模式
    injection_patterns = [
        r"'.*--",
        r"'.*;",
        r"union.*select",
        r"select.*from.*information_schema",
        r"benchmark\s*\(",
        r"sleep\s*\("
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, query_pattern, re.IGNORECASE):
            return {
                'is_safe': False,
                'reason': f'检测到潜在SQL注入模式: {pattern}',
                'injection_pattern': pattern
            }
    
    # 根据安全级别进行额外检查
    if safety_level == 'strict':
        # 严格模式：只允许SELECT语句
        if not query_pattern.strip().upper().startswith('SELECT'):
            return {
                'is_safe': False,
                'reason': '严格模式下只允许SELECT查询',
                'allowed_operations': ['SELECT']
            }
    
    return {
        'is_safe': True,
        'reason': '查询模式通过安全验证',
        'safety_level': safety_level
    }

def validate_index_synergy(query_pattern: str, table_name: str = 'memory_embeddings') -> Dict[str, Any]:
    """验证查询与索引的协同性"""
    # 分析查询中使用的列
    used_columns = extract_used_columns(query_pattern)
    
    # 已知的索引信息（基于现有的数据库结构）
    available_indexes = {
        'memory_embeddings': [
            'idx_memory_embeddings_ts',      # timestamp DESC
            'idx_memory_embeddings_source_type',  # source_type
            'idx_memory_embeddings_embedding_source'  # embedding_source
        ]
    }
    
    table_indexes = available_indexes.get(table_name, [])
    
    # 检查哪些索引可以被有效利用
    used_indexes = []
    optimization_suggestions = []
    
    if 'timestamp' in used_columns:
        if 'idx_memory_embeddings_ts' in table_indexes:
            used_indexes.append('idx_memory_embeddings_ts')
        else:
            optimization_suggestions.append('考虑为timestamp列创建索引')
    
    if 'source_type' in used_columns:
        if 'idx_memory_embeddings_source_type' in table_indexes:
            used_indexes.append('idx_memory_embeddings_source_type')
        else:
            optimization_suggestions.append('考虑为source_type列创建索引')
    
    if 'embedding_source' in used_columns:
        if 'idx_memory_embeddings_embedding_source' in table_indexes:
            used_indexes.append('idx_memory_embeddings_embedding_source')
        else:
            optimization_suggestions.append('考虑为embedding_source列创建索引')
    
    return {
        'used_columns': used_columns,
        'used_indexes': used_indexes,
        'available_indexes': table_indexes,
        'optimization_suggestions': optimization_suggestions,
        'synergy_score': len(used_indexes) / max(len(used_columns), 1)
    }

def extract_used_columns(query_pattern: str) -> List[str]:
    """从查询模式中提取使用的列名"""
    # 简单的列名提取（实际应用中可能需要更复杂的SQL解析）
    known_columns = [
        'memory_id', 'source_type', 'content_text', 
        'embedding_json', 'timestamp', 'embedding_source'
    ]
    
    used_columns = []
    query_lower = query_pattern.lower()
    
    for column in known_columns:
        if column in query_lower:
            used_columns.append(column)
    
    return used_columns

def build_safe_query_template(query_pattern: str, table_name: str, max_results: int) -> str:
    """构建安全的查询模板"""
    # 确保有结果限制
    safe_query = query_pattern.strip()
    
    # 添加结果限制（如果还没有）
    if 'LIMIT' not in safe_query.upper():
        safe_query += f' LIMIT {max_results}'
    
    # 确保表名正确
    if table_name not in safe_query:
        # 这是一个简化的替换，实际应用中需要更智能的SQL解析
        safe_query = safe_query.replace('memory_embeddings', table_name)
    
    return safe_query