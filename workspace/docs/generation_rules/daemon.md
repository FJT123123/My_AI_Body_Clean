【适用场景】
- 持续监控、定时检查、后台轮询。
- 命中条件时进行通知、事件投递、记忆写入。

【优先架构】
- 如果核心判断逻辑可能被 tool 手动调用，优先先抽成 capability。
- daemon 只负责循环、调度、通知、_event_bus、memory。

【实现偏好】
- 第一行使用 # daemon_name: 名称。
- 入口函数固定为 _daemon_run(stop_event)。
- 停止控制必须使用 stop_event.wait(N)，不要用 time.sleep()。
- 文件路径统一用 os.path.join(WORKSPACE_DIR, ...)。

【何时不要新建 daemon】
- 如果现有 daemon 已覆盖同一监控目标，优先复用或修改现有 daemon。
- 如果只是手动执行一次检查，优先调用现有 tool，而不是造 daemon。