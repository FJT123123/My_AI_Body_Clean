"""
自动生成的技能模块
需求: 监控 workspace/alert.txt 文件中的危险信号。读取文件内容，检查是否包含 "DANGER" 关键字，如果发现则返回危险信号详情。
生成时间: 2026-03-12 10:24:49
"""

# skill_name: workspace_alert_monitor
import os

def main(args=None):
    """
    监控 workspace/alert.txt 文件中的危险信号。
    读取文件内容，检查是否包含 "DANGER" 关键字，如果发现则返回危险信号详情。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', '.')
    
    alert_file_path = os.path.join(workspace_path, 'alert.txt')
    
    if not os.path.exists(alert_file_path):
        return {
            'result': {'status': 'file_not_found', 'message': f'文件不存在: {alert_file_path}'},
            'insights': [f'未找到警报文件: {alert_file_path}']
        }
    
    try:
        with open(alert_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'result': {'status': 'read_error', 'message': f'读取文件失败: {str(e)}'},
            'insights': [f'读取警报文件失败: {str(e)}']
        }
    
    if 'DANGER' in content.upper():
        # 发现危险信号
        danger_signals = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'DANGER' in line.upper():
                danger_signals.append({
                    'line_number': i + 1,
                    'content': line.strip(),
                    'severity': 'high'
                })
        
        result = {
            'status': 'danger_detected',
            'danger_signals': danger_signals,
            'total_danger_count': len(danger_signals),
            'file_path': alert_file_path
        }
        
        insights = [f'在文件 {alert_file_path} 中发现 {len(danger_signals)} 个危险信号']
        return {
            'result': result,
            'insights': insights,
            'memories': [{
                'event_type': 'skill_insight',
                'content': f'发现危险信号: {len(danger_signals)} 个危险信号来自 {alert_file_path}',
                'importance': 0.9
            }],
            'next_skills': ['emergency_response_handler'] if len(danger_signals) > 0 else []
        }
    else:
        # 未发现危险信号
        return {
            'result': {
                'status': 'no_danger',
                'message': '未发现危险信号',
                'file_path': alert_file_path
            },
            'insights': ['警报文件中未检测到危险信号']
        }