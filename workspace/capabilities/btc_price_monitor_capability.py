from datetime import datetime, timedelta

import requests


BTC_PRICE_API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"


def _parse_iso_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _trim_history(price_history: list, current_time: datetime, window_minutes: int = 60) -> list:
    cutoff = current_time - timedelta(minutes=window_minutes)
    trimmed = []
    for item in price_history:
        try:
            timestamp = _parse_iso_time(item["timestamp"])
            if timestamp >= cutoff:
                trimmed.append({
                    "price": float(item["price"]),
                    "timestamp": timestamp.isoformat(),
                })
        except Exception:
            continue
    return trimmed


def fetch_current_btc_price(timeout: int = 10) -> dict:
    try:
        response = requests.get(BTC_PRICE_API, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return {
            "ok": True,
            "price": float(data["bitcoin"]["usd"]),
            "provider": "coingecko",
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"BTC 价格获取失败: {type(exc).__name__}: {exc}",
        }


def analyze_price_window(price_history: list, threshold_percent: float = 3.0, min_window_minutes: int = 55) -> dict:
    if len(price_history) < 2:
        return {
            "enough_history": False,
            "triggered": False,
            "summary": "历史数据不足，暂不判断波动",
        }

    current = price_history[-1]
    oldest = price_history[0]
    current_time = _parse_iso_time(current["timestamp"])
    oldest_time = _parse_iso_time(oldest["timestamp"])
    age_minutes = (current_time - oldest_time).total_seconds() / 60
    if age_minutes < min_window_minutes:
        return {
            "enough_history": False,
            "triggered": False,
            "summary": f"历史窗口仅 {age_minutes:.1f} 分钟，尚未达到 {min_window_minutes} 分钟",
        }

    current_price = float(current["price"])
    baseline_price = float(oldest["price"])
    change_percent = ((current_price - baseline_price) / baseline_price) * 100
    direction = "上涨" if change_percent > 0 else "下跌"
    triggered = abs(change_percent) >= threshold_percent
    summary = (
        f"BTC 在 {age_minutes:.1f} 分钟内{direction}{abs(change_percent):.2f}%"
        if triggered else
        f"BTC 在窗口内波动 {change_percent:.2f}%，未达到阈值"
    )
    return {
        "enough_history": True,
        "triggered": triggered,
        "direction": direction,
        "change_percent": round(change_percent, 4),
        "current_price": current_price,
        "baseline_price": baseline_price,
        "age_minutes": round(age_minutes, 2),
        "summary": summary,
    }


def run_btc_monitor_cycle(price_history: list, threshold_percent: float = 3.0, window_minutes: int = 60, min_window_minutes: int = 55) -> dict:
    fetch = fetch_current_btc_price()
    if not fetch["ok"]:
        return {
            "ok": False,
            "history": price_history,
            "wait_seconds": 30,
            "error": fetch["error"],
            "memory": {
                "event_type": "btc_api_error",
                "content": fetch["error"],
                "importance": 0.3,
            },
        }

    current_time = datetime.now()
    updated_history = list(price_history or [])
    updated_history.append({
        "price": fetch["price"],
        "timestamp": current_time.isoformat(),
    })
    updated_history = _trim_history(updated_history, current_time, window_minutes=window_minutes)
    analysis = analyze_price_window(updated_history, threshold_percent=threshold_percent, min_window_minutes=min_window_minutes)

    result = {
        "ok": True,
        "current_price": fetch["price"],
        "provider": fetch["provider"],
        "timestamp": current_time.isoformat(),
        "history": updated_history,
        "analysis": analysis,
        "wait_seconds": 60,
    }
    if analysis.get("triggered"):
        direction = analysis["direction"]
        change_percent = abs(analysis["change_percent"])
        message = (
            f"BTC价格在1小时内{direction}{change_percent:.2f}%\n"
            f"当前价格: ${analysis['current_price']:,.2f}\n"
            f"1小时前价格: ${analysis['baseline_price']:,.2f}"
        )
        result.update({
            "notify": {
                "subject": f"⚠️ BTC价格波动警报: {direction}{change_percent:.2f}%",
                "message": message,
            },
            "event": {
                "type": "BTC_PRICE_ALERT",
                "content": message,
                "priority": 9,
            },
            "memory": {
                "event_type": "btc_price_alert",
                "content": message,
                "importance": 0.8,
            },
        })
    return result