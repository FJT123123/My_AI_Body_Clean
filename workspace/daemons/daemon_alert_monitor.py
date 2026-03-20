# daemon_name: alert_monitor

def _daemon_run(stop_event):
    """监控 workspace/alert.txt 文件中的危险信号。"""
    capability = load_capability_module("alert_monitor_capability")
    last_seen = ""

    while not stop_event.is_set():
        try:
            result = capability.check_alert_file(WORKSPACE_DIR, last_seen=last_seen)
            if result.get("reset_state"):
                last_seen = ""
            elif result.get("triggered"):
                last_seen = result.get("last_seen_next", last_seen)
                notify = result.get("message")
                subject = result.get("subject", "")
                if notify:
                    send_message_to_user(subject=subject, message=notify)
                event = result.get("event")
                if event:
                    _event_bus.put(event)
                memory_payload = result.get("memory")
                if memory_payload:
                    memory.store(
                        memory_payload.get("event_type", "alert_detected"),
                        memory_payload.get("content", ""),
                        importance=memory_payload.get("importance", 0.9),
                    )
        except Exception as _e:
            memory.store('daemon_error', f"alert_monitor 出错: {_e}", importance=0.7)

        stop_event.wait(10)
