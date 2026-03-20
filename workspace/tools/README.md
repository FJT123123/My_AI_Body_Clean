# 动态工具目录

这里存放 OpenClaw 自主生成并加载的工具模块。

这个目录文档只负责说明 `workspace/tools/` 是什么、当前真实加载机制是什么。
更细的组件选择规则、架构偏好和生成约束，统一见：

- `workspace/docs/generation_rules/README.md`
- `workspace/docs/generation_rules/tool.md`
- `workspace/docs/generation_rules/capability.md`
- `workspace/docs/generation_rules/daemon.md`

## 🔧 工具 vs 技能

**技能（Skills）**
- 存放位置：`workspace/skills/`
- 特征：纯计算模块，无副作用
- 生成方式：`forge_new_skill(...)`
- 调用方式：`run_skill(...)`
- 用途：数据处理、分析计算等

**工具（Tools）**
- 存放位置：`workspace/tools/`  ← 这里
- 特征：可与外部系统交互，可承担副作用或工具协作
- 生成方式：`evolve_self('tool', ...)`
- 调用方式：Agent 直接调用（与内置工具平级）
- 用途：系统监控、API调用、文件批处理等

## 🧩 Capability 分层

当某个能力既需要被 Tool 手动调用，又需要被 Daemon 持续监听时，不要在两边各写一份业务逻辑。

- 共享核心实现：`workspace/capabilities/`
- Tool：负责手动触发、参数入口、结果返回
- Daemon：负责循环调度、事件投递、通知、记忆写入

推荐模式：

```python
# tool_xxx.py
capability = load_capability_module("xxx_capability")
result = capability.run_xxx(...)
return result

# daemon_xxx.py
capability = load_capability_module("xxx_capability")
while not stop_event.is_set():
   result = capability.run_xxx(...)
   # 这里处理通知 / 事件 / memory
```

这样 Tool 和 Daemon 只是不同入口，共享的是同一个能力中心。

当前架构下，如果一个需求已经可由现有 tool 直接完成，运行时会在生成前短路，优先引导直接复用已有 tool，而不是继续新建重复组件。

## 📝 工具模板

```python
# tool_example.py
from langchain_core.tools import tool

@tool
def my_custom_tool(input_text: str) -> str:
    """
    工具功能的详细描述（LLM 会读取这段 docstring 决定何时调用）
    - input_text: 参数说明
    """
    # 实现逻辑
    result = f"处理结果: {input_text}"
    return result
```

## 🔄 加载机制

`openclaw_continuity.py` 启动时会自动扫描此目录，
导入所有 `tool_*.py` 文件中的 `@tool` 装饰器函数，并把它们并入当前 Agent 的工具集。

工具运行时可直接复用系统注入对象，例如：

- `invoke_tool(...)`
- `run_skill(...)`
- `query_skill_results(...)`
- `remember_this(...)`
- `send_message_to_user(...)`
- `load_capability_module(...)`

输出示例：
```
🔌 [动态工具] 已加载: monitor_system_resources
🔌 [动态工具] 已加载: batch_web_scraper
✨ [元编程] 已加载 2 个自定义工具
```

## 🧬 生成流程

当前真实流程是：

1. 调用 `evolve_self('tool', ...)`
2. 运行时先做生成前短路判断，确认是否其实应直接复用已有 tool
3. 若确需新建，则进入代码生成
4. 保存前执行安全校验、自检、重复薄包装拦截
5. 通过后直接写入 `workspace/tools/` 并尝试热加载

## ⚠️ 安全须知

- 工具代码仍受运行时安全校验约束。
- 禁止使用 subprocess、socket、os.system 等危险操作。
- 禁止伪造 mock/fake 结果。
- 禁止把持续监听循环误写进 tool；这类能力应做成 daemon。
- 共享逻辑优先抽到 capability，而不是在多个 tool/daemon 中复制。

## 💡 示例用途

- 系统资源监控（CPU、内存、磁盘）
- 批量网页抓取与分析
- 定时任务调度
- 文件批处理（压缩、格式转换）
- 数据库查询封装
- API 集成（天气、新闻、股票等）

这是 OpenClaw 的运行时工具层：面向直接调用、结果返回和跨工具协作。
