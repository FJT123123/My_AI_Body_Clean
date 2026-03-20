# daemon_name: btc_price_monitor
# pyright: reportUndefinedVariable=false
from typing import Any


if "memory" not in globals():
    class _MissingMemory:
        def store(self, event_type: str, content: str, importance: float = 0.5) -> None:
            raise RuntimeError("memory is injected at daemon runtime")

    memory: Any = _MissingMemory()


if "send_message_to_user" not in globals():
    def send_message_to_user(*, message: str, subject: str = "") -> None:
        raise RuntimeError("send_message_to_user is injected at daemon runtime")


if "load_capability_module" not in globals():
    def load_capability_module(module_name: str) -> Any:
        raise RuntimeError("load_capability_module is injected at daemon runtime")


def _daemon_run(stop_event):
    capability = load_capability_module("btc_price_monitor_capability")
    price_history = []
    
    while not stop_event.is_set():
        try:
            result = capability.run_btc_monitor_cycle(price_history, threshold_percent=3.0)
            if result.get("ok"):
                price_history = result.get("history", price_history)
                notify = result.get("notify")
                if notify:
                    send_message_to_user(message=notify.get("message", ""), subject=notify.get("subject", ""))
                event = result.get("event")
                if event:
                    _event_bus.put(event)
                memory_payload = result.get("memory")
                if memory_payload:
                    memory.store(
                        memory_payload.get("event_type", "btc_price_alert"),
                        memory_payload.get("content", ""),
                        importance=memory_payload.get("importance", 0.8),
                    )
                stop_event.wait(result.get("wait_seconds", 60))
            else:
                memory_payload = result.get("memory")
                if memory_payload:
                    memory.store(
                        memory_payload.get("event_type", "btc_api_error"),
                        memory_payload.get("content", result.get("error", "BTC 监控失败")),
                        importance=memory_payload.get("importance", 0.3),
                    )
                stop_event.wait(result.get("wait_seconds", 30))
                
        except Exception as _e:
            error_msg = f"BTC监控错误: {str(_e)}"
            memory.store('btc_monitor_error', error_msg, importance=0.7)
            # 出错时等待30秒后重试
            stop_event.wait(30)