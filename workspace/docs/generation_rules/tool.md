【适用场景】
- 需要一个随时可调用的新工具。
- 面向手动触发、直接返回结果、与其它工具结构化协作。

【优先架构】
- 如果核心逻辑未来也会被 daemon 复用，先抽成 capability，再用 tool 做外壳。
- 如果只是包装已有 tool 或已有 capability 且没有新增独立能力，不要再新建 tool。
- 如果任务本质是检查系统可执行文件是否存在、确认 Homebrew/apt 安装状态或向用户提示系统依赖安装步骤，不要新建 tool；优先使用现有系统依赖探测入口。

【实现偏好】
- docstring 说明用途、参数、返回值和触发条件。
- 优先返回 JSON 可序列化的 dict 或稳定字符串。
- 使用 invoke_tool(...) 做工具间协作，使用 load_capability_module(...) 做能力复用。

【禁止倾向】
- 不要 from openclaw_continuity import ...。
- 不要伪造 mock/fake 结果。
- 不要把持续监听循环写进 tool；那是 daemon 的职责。
- 不要把 brew install、apt-get install、PATH 修复这类系统管理员动作包装成 tool 内的自动安装流程。