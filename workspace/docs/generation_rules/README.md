# Generation Rules

本目录承载 OpenClaw 生成体系中的说明书式规则。

目标不是替代运行时代码，而是把原本堆在主程序中的长篇自然语言说明拆出来，按组件维护。

## 分工原则

- Python 代码负责硬约束：安全校验、格式检查、去重、生成前短路、运行时注入与沙箱。
- Markdown 文档负责软规则：适用场景、组件选择、架构偏好、示例风格、常见误用。
- 当软规则与硬约束冲突时，以代码中的硬约束为准。

## 文件说明

- runtime_extensions.md
  运行时总则、自我扩展渠道、对话协议与高层使用原则。

- skill.md
  skill 的适用场景、真实数据约束、双向数据流协议、数据库真实表结构、实现风格。

- capability.md
  capability 的职责边界、适用场景、共享逻辑抽取原则、何时不要新建 capability。

- tool.md
  tool 的适用场景、与 capability 的分层关系、工具间协作偏好、常见误用。

- patch.md
  patch 的适用场景、运行时边界、钩子注册原则、何时不要新建 patch。

- daemon.md
  daemon 的适用场景、持续监控职责、与 capability 的分层关系、停止/路径约束。

- strategy.md
  反思策略 JSON 的结构约束、模板类型、适用场景与误用边界。

## 使用方式

- forge_new_skill(...) 会加载 skill.md。
- evolve_self(component='capability'|'tool'|'patch'|'daemon'|'strategy', ...) 会按组件加载对应规则文件。
- 系统运行时扩展说明由 runtime_extensions.md 提供。

## 维护约束

- 这里放说明，不放执法逻辑。
- 这里可以放示例、偏好、注意事项，但不要假设它们天然具有强制力。
- 如果某条规则必须被强制执行，应落到 openclaw_continuity.py 的运行时检查中，而不是只写在文档里。

## 推荐维护流程

1. 先判断一条规则属于硬约束还是软规则。
2. 硬约束改代码与校验器。
3. 软规则改本目录中的对应 Markdown。
4. 若组件边界变化，同时更新 README，避免索引失真。