# tool_name: emotion_state_recorder
from langchain_core.tools import tool
from datetime import datetime
from typing import Optional

@tool
def emotion_state_recorder(
    emotion: str, 
    intensity: int, 
    trigger: Optional[str] = None, 
    notes: Optional[str] = None,
    timestamp: Optional[str] = None
) -> str:
    """
    记录情绪状态的标准化工具，用于创建格式一致的情绪数据供情绪自我调节模块分析
    - emotion: 当前主要情绪类型（如：快乐、悲伤、焦虑、愤怒、平静等）
    - intensity: 情绪强度，范围1-10，1表示最轻微，10表示最强烈
    - trigger: 导致该情绪的触发事件或原因（可选）
    - notes: 补充说明或备注（可选）
    - timestamp: 记录时间戳，格式YYYY-MM-DD HH:MM:SS（可选，默认为当前时间）
    返回标准化的情绪记录字符串
    """
    try:
        # 验证强度范围
        if not 1 <= intensity <= 10:
            return "错误：强度值必须在1-10之间"
        
        # 验证情绪类型
        valid_emotions = ["快乐", "悲伤", "焦虑", "愤怒", "平静", "兴奋", "恐惧", "惊讶", "厌恶", "困惑", 
                         "happy", "sad", "anxious", "angry", "calm", "excited", "fear", "surprised", "disgusted", "confused"]
        if emotion.lower() not in [e.lower() for e in valid_emotions]:
            return f"警告：情绪类型 '{emotion}' 不在标准列表中，可能影响分析结果"
        
        # 设置时间戳
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 创建标准化记录格式
        record = {
            "timestamp": timestamp,
            "emotion": emotion,
            "intensity": intensity,
            "trigger": trigger if trigger else "未记录",
            "notes": notes if notes else "无备注"
        }
        
        # 格式化输出
        formatted_record = (
            f"[情绪记录] 时间: {record['timestamp']} | "
            f"情绪: {record['emotion']} | "
            f"强度: {record['intensity']}/10 | "
            f"触发因素: {record['trigger']} | "
            f"备注: {record['notes']}"
        )
        
        return formatted_record
    
    except Exception as e:
        return f"记录情绪状态时发生错误: {str(e)}"