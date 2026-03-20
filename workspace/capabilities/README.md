# Capability Center

`workspace/capabilities/` 是共享能力中心：
- capability: 纯业务逻辑（可调用外部 API），不直接做通知/记忆副作用。
- tool: 手动触发入口，负责参数解析与返回结构。
- daemon: 持续监听入口，负责循环、通知、事件总线、memory 写入。

生成入口：
- 直接生成 capability：`evolve_self('capability', ...)`
- 手写 capability 代码时，第一行建议使用 `# capability_name: xxx_capability`

## 目录约定

- 文件命名：`*_capability.py`
- 对外主函数建议：`run_<domain>_cycle(...)` 或 `check_<domain>_...(...)`
- 返回值统一为 `dict`

## 返回值契约（建议）

成功/失败统一字段：
- `ok: bool` 或 `triggered: bool`
- `summary: str`（可选）
- `wait_seconds: int`（供 daemon 调度）

当需要通知：
- `notify: { subject: str, message: str }`

当需要事件总线：
- `event: { type: str, content: str, priority: int }`

当需要记忆：
- `memory: { event_type: str, content: str, importance: float }`

## 责任边界

- capability 不调用 `send_message_to_user`。
- capability 不直接写 `memory.store(...)`。
- capability 不直接 `_event_bus.put(...)`。
- 这些副作用由 daemon/tool 外壳执行。

## 示例

- `alert_monitor_capability.py`
- `btc_price_monitor_capability.py`

这两个文件已经作为 capability-centered 样板在运行。
