"""
自动生成的技能模块
需求: 创建一个名为skill_alert_monitor的技能，它可以读取workspace目录下的alert.txt文件，检查是否包含'DANGER'关键词。如果发现'DANGER'，就调用send_message_to_user向用户发送最高优先级的报警消息。
生成时间: 2026-03-12 09:48:34
"""

# skill_name: skill_alert_monitor
import os

def main(args=None):
    """
    监控workspace目录下的alert.txt文件，检查是否包含'DANGER'关键词。
    如果发现'DANGER'，就调用send_message_to_user向用户发送最高优先级的报警消息。
    """
    if args is None:
        args = {}
    
    context = args.get('__context__', {})
    workspace_path = context.get('workspace_path', './workspace')
    
    alert_file_path = os.path.join(workspace_path, 'alert.txt')
    
    # 检查文件是否存在
    if not os.path.exists(alert_file_path):
        return {
            'result': {'error': 'alert.txt文件不存在'},
            'insights': [f'监控文件 {alert_file_path} 不存在']
        }
    
    # 读取文件内容
    try:
        with open(alert_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {
            'result': {'error': f'读取文件失败: {str(e)}'},
            'insights': [f'读取 {alert_file_path} 文件时发生错误: {str(e)}']
        }
    
    # 检查是否包含'DANGER'关键词
    if 'DANGER' in content.upper():
        # 准备返回结果，让上层系统调用send_message_to_user
        return {
            'result': {
                'alert_detected': True,
                'message': '检测到危险信号！系统发现DANGER关键词，请立即处理！',
                'priority': 'highest'
            },
            'insights': ['检测到DANGER关键词，需要立即通知用户'],
            'memories': [{
                'event_type': 'skill_insight',
                'content': '在alert.txt中检测到DANGER关键词，触发紧急报警机制',
                'importance': 0.9
            }]
        }
    else:
        return {
            'result': {
                'alert_detected': False,
                'message': '未检测到危险信号',
                'priority': 'normal'
            },
            'insights': ['alert.txt文件中未发现DANGER关键词，系统运行正常']
        }