【适用场景】
- 调整自主反思时的议题生成策略。
- 定义在什么条件下，优先思考、搜索、锻造或让 LLM 自主出题。

【输出结构】
- 输出 JSON，而不是 Python。
- 至少包含：name、weight、templates。
- 可选包含：condition。

【字段约束】
- weight: 0 到 1 之间的浮点数，用于表示策略权重。
- condition: 可选触发条件；常见是 emotion 条件。
- templates: 非空数组，元素为议题模板字符串。

【模板约束】
- [THINK] = 纯思考
- [ACTION:search] = 调用 search_and_learn
- [ACTION:forge] = 调用 forge_new_skill
- [LLM_GENERATE] = 让 LLM 自主生成议题

【何时不要新建 strategy】
- 如果只是完成当前用户任务，不要误用 strategy。
- 如果需求是代码生成、补丁、工具、守护进程或共享能力，应分别使用对应组件。