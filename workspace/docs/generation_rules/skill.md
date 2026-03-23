【适用场景】
- 纯计算、分析、文本处理、查询汇总。
- 先造后按需调用，不需要常驻运行。
- 不承担持续监控、实时通知、热注入行为。

【何时不要新建 skill】
- 如果现有 skill 已能完成任务，直接 run_skill。
- 如果任务本质是修改运行时行为，用 patch。
- 如果任务本质是常驻工具或需要与其它工具协作，优先考虑 tool。
- 如果任务只是复用已有系统运维 skill，直接 run_skill，不要重复锻造。

【输出偏好】
- 返回 dict，而不是裸字符串。
- 尽量提供 result、insights、facts、memories、next_skills 等标准键。
- 不要伪造外部数据或使用硬编码样本作为 fallback。

【真实数据约束】
- 不要在 main() 中写入任何硬编码样本或假数据作为 fallback。
- 如果技能需要外部数据，优先从 args['__context__'] 读取 db_path、recent_memories、skill_history 等真实上下文。
- 若数据库不可访问，应返回明确错误，而不是用假数据继续运行。
- 如果 skill 承担系统运维任务，必须执行真实检查、真实安装、真实验证，不要伪造 brew/apt/PATH 结果。

【系统运维型 skill】
- 允许锻造用于系统依赖安装、命令探测、环境修复的 skill。
- 这类 skill 可以调用真实系统命令，但必须把执行结果和验证结果结构化返回。
- 完成安装后，应至少再执行一次版本检查或可用性检查，确认不是“命令跑了但没生效”。

【标准数据读取范式】
```python
context = args.get('__context__', {})
db_path = context.get('db_path', '')
import sqlite3, os
if not db_path or not os.path.exists(db_path):
	return {'result': {'error': 'db_path 不可用'}, 'insights': ['无法访问数据库']}
conn = sqlite3.connect(db_path)
rows = conn.execute('SELECT ... FROM memories ...').fetchall()
conn.close()
```

【双向数据流协议】
- main() 应返回 dict，包含真实计算结果。
- 可按需提供以下标准键，让结果回流主系统：
- result: 主要结果
- insights: 关键洞察，自动写入记忆
- facts: 知识三元组
- memories: 直接写入记忆库的事件
- capabilities: 新获得能力描述
- next_skills: 建议后续继续执行的技能
- 示例：return {'result': computed_value, 'insights': ['发现X'], 'facts': [...]} 

【数据库真实表结构】
- memories
- 列: id(INTEGER PK), event_type(TEXT), content(TEXT/JSON), importance(REAL), timestamp(TEXT), tags(TEXT)
- 不存在 created_at / metadata / updated_at / status 列
- 真实 event_type 枚举只允许使用这些：
- skill_forged, skill_forge_failed, skill_executed, skill_insight
- learning, autonomous_thought, conscious_reflection
- direction_value_reflection, workspace_analysis
- skill_health_check, emotional_self_regulation, system_boot

- skill_results
- 列: id(TEXT PK), skill_name(TEXT), input_args(TEXT), result_json(TEXT), result_summary(TEXT), timestamp(TEXT), execution_time_ms(REAL)
- execution_time_ms 允许为 NULL，0.0 不代表异常

- knowledge_triples
- 列: id(TEXT), subject(TEXT), relation(TEXT), object(TEXT), source(TEXT), timestamp(TEXT)

【实现风格】
- main(args=None) 保持单一入口。
- skill 名称（含 skill_ 前缀）严禁超过 64 字符。
- 先从 args['__context__'] 读取上下文与 db_path。
- 结果结构稳定，便于主系统回流和持久化。