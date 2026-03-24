【适用场景】
- 同一套核心逻辑需要同时被 tool 手动调用和 daemon 持续监听。
- 需要沉淀为共享业务模块，而不是只服务单一入口。

【职责边界】
- capability 只负责核心业务逻辑和结构化返回。
- capability 不直接调用 send_message_to_user、memory.store、_event_bus.put。
- 通知、事件总线、记忆写入由 tool 或 daemon 外壳处理。

【设计偏好】
- 文件命名建议使用 *_capability.py。
- 对外主函数建议使用 run_xxx_cycle(...)、check_xxx(...) 等稳定接口。
- 返回值统一为 JSON 可序列化 dict，字段名保持稳定。

【何时不要新建 capability】
- 如果现有 capability 已覆盖需求，直接 load_capability_module 复用。
- 如果需求只是完成一次任务，优先直接调用现有 tool 或运行现有 daemon。