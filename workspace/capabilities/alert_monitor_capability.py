import os
from datetime import datetime


def _resolve_alert_path(workspace_dir: str, relative_path: str) -> str:
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(workspace_dir, relative_path)


def read_alert_source(workspace_dir: str, relative_path: str = "alert.txt") -> dict:
    alert_path = _resolve_alert_path(workspace_dir, relative_path)
    if not os.path.exists(alert_path):
        return {
            "exists": False,
            "path": alert_path,
            "content": "",
        }

    with open(alert_path, "r", encoding="utf-8") as handle:
        content = handle.read().strip()
    return {
        "exists": True,
        "path": alert_path,
        "content": content,
    }


def evaluate_alert_signal(content: str, last_seen: str = "", danger_keyword: str = "DANGER") -> dict:
    text = (content or "").strip()
    ts = datetime.now().strftime("%H:%M:%S")
    triggered = bool(text and danger_keyword in text and text != last_seen)

    result = {
        "triggered": triggered,
        "last_seen_next": text if triggered else last_seen,
        "summary": "未检测到新的危险信号",
    }
    if not triggered:
        return result

    message = f"[{ts}] alert.txt 检测到危险信号: {text[:200]}"
    result.update({
        "summary": f"检测到新的危险信号: {text[:80]}",
        "subject": "🚨 DANGER 报警",
        "message": message,
        "event": {
            "type": "DANGER_ALERT",
            "content": f"[{ts}] alert.txt 内容: {text[:200]}",
            "priority": 10,
        },
        "memory": {
            "event_type": "alert_detected",
            "content": f"DANGER detected: {text}",
            "importance": 0.9,
        },
    })
    return result


def check_alert_file(workspace_dir: str, last_seen: str = "", relative_path: str = "alert.txt", danger_keyword: str = "DANGER") -> dict:
    source = read_alert_source(workspace_dir, relative_path=relative_path)
    if not source["exists"]:
        return {
            "triggered": False,
            "reset_state": True,
            "last_seen_next": "",
            "path": source["path"],
            "summary": "告警文件不存在，状态已重置",
            "wait_seconds": 10,
        }

    analysis = evaluate_alert_signal(source["content"], last_seen=last_seen, danger_keyword=danger_keyword)
    analysis.update({
        "path": source["path"],
        "content": source["content"],
        "reset_state": False,
        "wait_seconds": 10,
    })
    return analysis