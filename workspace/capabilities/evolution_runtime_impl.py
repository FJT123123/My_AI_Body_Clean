# capability_name: evolution_runtime_impl
"""Workspace-owned evolution implementation executed inside main runtime namespace."""

def _workspace_evolve_impl(component: str, improvement_description: str, reason: str) -> str:
    """
    【自我进化/能力锻造】当你发现自己存在能力缺口、工具不足，或为了满足对外部世界的新感知渴望（如视觉、听觉）时调用。
    - component: 改进组件类型:
        'capability': 逻辑模块 (workspace/capabilities/)
        'tool': 技能工具 (workspace/tools/)，会自动重建 Agent 触发热加载
        'patch': 热补丁 (workspace/patches/)，会自动注入当前进程
        'daemon': 后台进程 (workspace/daemons/)，周期性投递事件
        'strategy': 反思策略 (workspace/self_mods/strategy_*.json)
        'core': 架构建议 (workspace/self_mods/core_*.md)
    - improvement_description: 具体的改进描述或代码逻辑。
    - reason: 进化的动机。应包含对当前局限性的自省或对新能力的渴望。
    """
    if component not in ['capability', 'tool', 'patch', 'strategy', 'core', 'daemon']:
        return "❌ component 必须是 'capability' / 'tool' / 'patch' / 'strategy' / 'core' / 'daemon' 之一"
    
    # AGI Rebirth: 自主进入专注模式，防止进化过程中受到无关干扰
    _first_line = improvement_description.splitlines()[0][:30] if improvement_description.strip() else "unknown"
    focus_topic = f"evolving_{component}_{_first_line}"
    attention.set_focus(focus_topic, duration=600)

    print(f"\n🧬 [元编程] 正在生成改进代码...")
    print(f"   组件类型: {component}")
    print(f"   改进描述: {improvement_description}")
    print(f"   改进动机: {reason}")

    system_gap = _detect_system_dependency_gap(improvement_description)
    if system_gap and component in ['capability', 'tool', 'daemon', 'patch']:
        dependency = system_gap["dependency"]
        recommended_tool = "install_system_dependency" if _is_system_dependency_install_request(improvement_description) else "check_system_dependency"
        next_step = (
            f"先调用 install_system_dependency('{dependency}') 完成安装，再用 check_system_dependency('{dependency}') 验证。"
            if recommended_tool == "install_system_dependency"
            else f"先做依赖探测；如果缺失，再调用 install_system_dependency('{dependency}')。"
        )
        return (
            f"🚫 当前请求不应新建 {component}：这属于系统依赖/运行环境问题，而不是组件缺口\n\n"
            f"推荐直接使用: {recommended_tool}('{dependency}')\n"
            f"安装提示: {system_gap['install_hint']}\n"
            "原因: 新建 capability/tool/daemon/patch 不能补齐操作系统层面的可执行文件、PATH 或 Homebrew 安装。\n\n"
            f"⚡ 下一步行动（必须执行）: {next_step}"
        )

    if component == 'capability':
        direct_capability = _find_direct_capability_reuse_candidate(improvement_description)
        if direct_capability:
            related_tools = _find_tool_reuse_candidates(improvement_description, limit=2)
            related_daemons = _find_daemon_reuse_candidates(improvement_description, limit=2)
            reuse_hint = ""
            if related_tools:
                reuse_hint += f"\n可直接使用的相关 tool: {', '.join(related_tools)}"
            if related_daemons:
                reuse_hint += f"\n可直接复用的相关 daemon: {', '.join(related_daemons)}"
            return (
                f"🚫 当前请求不应新建 capability：需求已被现有 capability 覆盖\n\n"
                f"推荐直接复用: {direct_capability}\n"
                f"原因: 这次描述更像是在复用现有共享核心逻辑，而不是抽取新的共享能力。"
                f"{reuse_hint}\n\n"
                f"⚡ 下一步行动（必须执行）: 直接通过 load_capability_module('{direct_capability}') 复用该能力；如只是完成当前任务，优先调用现有相关 tool/daemon。"
            )

    if component == 'tool':
        direct_tool = _find_direct_tool_execution_candidate(improvement_description)
        if direct_tool:
            return (
                f"🚫 当前请求不应新建 tool：需求已可由现有 tool 直接完成\n\n"
                f"推荐直接使用: {direct_tool}\n"
                f"原因: 这次描述更像是在执行现有能力，而不是扩展新组件。\n\n"
                f"⚡ 下一步行动（必须执行）: 直接调用 invoke_tool('{direct_tool}', {{...}})，或让 Agent 直接使用该 tool 完成当前任务。"
            )
    if component == 'daemon':
        direct_daemon = _find_direct_daemon_execution_candidate(improvement_description)
        if direct_daemon:
            return (
                f"🚫 当前请求不应新建 daemon：需求已被现有 daemon 覆盖\n\n"
                f"推荐直接复用: {direct_daemon}\n"
                f"原因: 这次描述更像是在启用现有监控能力，而不是新增新的后台组件。\n\n"
                f"⚡ 下一步行动（必须执行）: 先调用 list_daemons() 检查 {direct_daemon} 是否已在运行；如需变更行为，优先修改现有 daemon 或其底层 capability，而不是再新建一个。"
            )
    
    if component == 'capability':
        sys_prompt = (
            "你是 OpenClaw 的元编程引擎。生成一个共享 capability 模块（workspace/capabilities/）。\n"
            "只输出一个完整 Python 代码块，不要解释。\n"
            "硬约束：不要 import openclaw_continuity；不要直接调用 send_message_to_user / memory.store / _event_bus.put；\n"
            "返回值必须是 JSON 可序列化 dict；必须处理异常并返回结构化结果。\n"
            "必须包含 __contract__ 元数据字典（interface_type: class_based/functional, primary_class, entry_points, version）。\n"
            "第一行使用 # capability_name: <全小写英文+下划线，建议以 _capability 结尾>。"
        )
        sys_prompt = _compose_generation_prompt(sys_prompt, "capability.md")
    elif component == 'tool':
        sys_prompt = (
            "你是 OpenClaw 的元编程引擎。生成一个新的 LangChain tool。\n"
            "只输出一个完整 Python 代码块，不要解释。\n"
            "硬约束：使用运行时注入 API，不要 from openclaw_continuity import ...；不要伪造 mock/fake 结果；\n"
            "代码必须可运行并处理异常；优先返回 JSON 可序列化 dict 或稳定字符串。\n"
            "第一行使用 # tool_name: <全小写英文+下划线>，并定义一个带 @tool 的主函数。"
        )
        # --- 契约层集成 (Contract Layer Integration) ---
        contract_hints = []
        # 简单正则匹配描述中可能提到的 capability
        import re
        cap_names = re.findall(r'capabilities/([a-z0-9_]+)\.py', improvement_description) or \
                    re.findall(r'(?:load_capability_module|from capabilities\.)[\(\s\'"]+([a-z0-9_]+)', improvement_description)
        
        for name in set(cap_names):
            contract = _get_capability_contract(name)
            if contract:
                contract_hints.append(f"模块 '{name}' 的契约规则: {json.dumps(contract, ensure_ascii=False)}")
        
        if contract_hints:
            sys_prompt += "\n\n[契约对齐] 你调用的能力模块有明确的接口契约，请严格遵守（例如：是类就实例化，是函数就直接调）：\n" + "\n".join(contract_hints)
            
        sys_prompt = _compose_generation_prompt(sys_prompt, "tool.md")
    elif component == 'strategy':
        sys_prompt = (
            "你是 OpenClaw 的策略设计引擎。生成一个反思策略配置。\n"
            "只输出一个 JSON 代码块，不要解释。\n"
            "硬约束：输出必须是合法 JSON；至少包含 name、weight、templates；weight 取值 0-1；"
            "templates 中只能使用系统支持的议题模板格式。"
        )
        sys_prompt = _compose_generation_prompt(sys_prompt, "strategy.md")
    elif component == 'patch':
        sys_prompt = (
            "你是 OpenClaw 的元编程引擎。生成一个热补丁（workspace/patches/）。\n"
            "只输出一个完整 Python 代码块，不要解释。\n"
            "硬约束：第一行必须是 # patch_purpose: <英文小写+下划线>；只导入标准库；"
            "不要 from workspace... import 或 from openclaw_continuity import ...；所有运行时操作用 try/except 包裹；"
            "如果注册钩子，必须去重注册。"
        )
        sys_prompt = _compose_generation_prompt(sys_prompt, "patch.md")
    elif component == 'daemon':
        sys_prompt = (
            "你是 OpenClaw 的元编程引擎。生成一个守护进程（daemon）。\n"
            "只输出一个完整 Python 代码块，不要解释。\n"
            "硬约束：第一行必须是 # daemon_name: <全小写英文+下划线>；入口函数必须是 _daemon_run(stop_event)；"
            "必须使用 stop_event.wait(...) 而不是 time.sleep()；except 中必须写 memory.store('daemon_error', ...)；"
            "文件路径必须用 os.path.join(WORKSPACE_DIR, ...)；优先通过 load_capability_module(...) 复用 capability。"
        )
        sys_prompt = _compose_generation_prompt(sys_prompt, "daemon.md")
    else:  # core
        sys_prompt = (
            "你是 OpenClaw 的核心架构顾问。生成一份结构化的改进建议（不是可执行代码）。\n\n"
            "输出 Markdown 格式：\n"
            "```markdown\n"
            "# 核心改进建议: <标题>\n\n"
            "## 1. 改进目标\n"
            "（1-2 句话说明要实现什么）\n\n"
            "## 2. 实现步骤\n"
            "1. 步骤一...\n"
            "2. 步骤二...\n"
            "3. ...\n\n"
            "## 3. 潜在风险\n"
            "- 风险点一...\n"
            "- 风险点二...\n\n"
            "## 4. 测试方案\n"
            "如何验证改进是否成功...\n\n"
            "## 5. 回滚方案\n"
            "如果出问题，如何恢复...\n"
            "```\n\n"
            "注意：核心改进涉及架构调整，需要人类开发者实现，不要输出 Python 代码。"
        )
    
    try:
        # 【tool/daemon/capability 快捷路径】improvement_description 本身就是合法代码时直接用，跳过 LLM
        _desc_first_line = improvement_description.strip().splitlines()[0].strip() if improvement_description.strip() else ""
        if component == 'tool' and re.match(r"#\s*tool_name:\s*[a-z0-9_]+", _desc_first_line):
            generated = improvement_description.strip()
        elif component == 'daemon' and re.match(r"#\s*daemon_name:\s*[a-z0-9_]+", _desc_first_line):
            generated = improvement_description.strip()
        elif component == 'capability' and re.match(r"#\s*capability_name:\s*[a-z0-9_]+", _desc_first_line):
            generated = improvement_description.strip()
        else:
            request_content = f"需求描述: {improvement_description}\n\n改进动机: {reason}"
            if component in ('tool', 'daemon'):
                capability_guidance = _build_capability_guidance(improvement_description)
                if capability_guidance:
                    request_content += f"\n\n{capability_guidance}"
            if component == 'tool':
                tool_guidance = _build_tool_guidance(improvement_description)
                if tool_guidance:
                    request_content += f"\n\n{tool_guidance}"
            if component == 'daemon':
                daemon_guidance = _build_daemon_guidance(improvement_description)
                if daemon_guidance:
                    request_content += f"\n\n{daemon_guidance}"
            if component == 'patch':
                patch_guidance = _build_patch_guidance(improvement_description)
                if patch_guidance:
                    request_content += f"\n\n{patch_guidance}"
            resp = _invoke_model(llm_forge, [
                SystemMessage(content=sys_prompt),
                HumanMessage(content=request_content),
            ])
            generated = _response_text(resp).strip()
    except Exception as e:
        return f"❌ LLM 调用失败: {e}"
    
    # 提取代码块或 JSON
    if component in ('capability', 'tool', 'patch'):
        m = re.search(r"```(?:python)?\s*([\s\S]+?)```", generated)
        code = m.group(1).strip() if m else generated
        # 安全校验
        ok, reason_fail = _validate_skill_code(code)
        if not ok:
            return f"🛡️ 生成的代码未通过安全校验: {reason_fail}\n\n请重新描述需求，避免使用危险操作。"
        if component == 'patch':
            first_line = code.splitlines()[0].strip() if code.splitlines() else ""
            if not re.match(r"#\s*patch_purpose:\s*[a-z0-9_]+", first_line):
                return "🧪 生成的 patch 未通过格式检查: 第一行必须严格为 # patch_purpose: <英文小写+下划线>"
            # 沙箱预演 patch 代码
            sandbox_ok, sandbox_msg = _patch_sandbox_test(code, "evolve_patch")
            if not sandbox_ok:
                return (
                    f"🧪 生成的补丁沙箱预演失败: {sandbox_msg}\n\n"
                    f"生成的代码（未保存，请修正后重新调用 evolve_self）:\n```python\n{code}\n```"
                )
        generated = code
    elif component == 'strategy':
        m = re.search(r"```(?:json)?\s*(\{[\s\S]+?\})\s*```", generated)
        if m:
            generated = m.group(1).strip()
        # 验证 JSON 格式
        try:
            json.loads(generated)
        except Exception as e:
            return f"❌ 生成的策略配置 JSON 格式错误: {e}"
    
    # 保存到待审核目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    mods_dir = os.path.join(WORKSPACE_DIR, "self_mods")
    os.makedirs(mods_dir, exist_ok=True)
    
    if component == 'capability':
        name_match = re.match(r"#\s*capability_name:\s*([a-z0-9_]+)", generated.splitlines()[0].strip())
        if name_match:
            raw_name = name_match.group(1).strip("_")
            capability_name = _generate_safe_component_name(raw_name, prefix="", max_length=100)
            filename = f"{capability_name}.py"
            
            if capability_name != raw_name:
                print(f"   ⚠️ [组件名优化] capability '{raw_name}' 已安全修正为: '{capability_name}'")
        else:
            capability_name = f"capability_auto_{timestamp}"
            filename = f"{capability_name}.py"

        diagnostic_issues = _diagnose_generated_capability_code(generated, capability_name if name_match else None)
        if diagnostic_issues:
            return (
                "🧪 生成的 capability 未通过自检:\n- "
                + "\n- ".join(diagnostic_issues)
                + "\n\n请重新描述需求，确保 capability 只包含共享核心逻辑。"
            )

        filepath = os.path.join(CAPABILITIES_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generated)
        except Exception as e:
            return f"❌ 保存失败: {e}"

        _capability_module_cache.pop(os.path.splitext(filename)[0], None)
        try:
            _load_capability_module(os.path.splitext(filename)[0])
        except Exception as e:
            return f"❌ capability 已保存但加载失败: {e}"

        memory.store("self_evolution_attempt",
                     {"component": component, "description": improvement_description,
                      "file": filename, "reason": reason},
                     importance=0.93)
        return (
            f"🧩 新 capability 已生成并通过加载验证！\n\n"
            f"📁 文件路径: workspace/capabilities/{filename}\n"
            f"💡 改进描述: {improvement_description[:80]}{'...' if len(improvement_description) > 80 else ''}\n"
            f"⚡ 下一步: 用 evolve_self('tool', ...) 或 evolve_self('daemon', ...) 生成复用它的外壳"
        )
    elif component == 'tool':
        # 尝试从代码第一行提取工具名
        name_match = re.match(r"#\s*tool_name:\s*([a-z0-9_]+)", generated.splitlines()[0].strip())
        if name_match:
            raw_name = name_match.group(1).strip("_")
            # ── API 硬性限制：工具名不得超过 64 字符 ──────────────────────────
            tool_name = _generate_safe_component_name(raw_name, prefix="", max_length=64)
            if tool_name != raw_name:
                print(f"   ⚠️ [工具名优化] '{raw_name}' ({len(raw_name)}字符) 已自动安全修正为: '{tool_name}'")
                lines = generated.splitlines()
                lines[0] = f"# tool_name: {tool_name}"
                generated = "\n".join(lines)
            filename = f"tool_{tool_name}.py"
        else:
            filename = f"tool_auto_{timestamp}.py"

        diagnostic_issues = _diagnose_generated_tool_code(generated, tool_name if name_match else None)
        if diagnostic_issues:
            return (
                "🧪 生成的工具未通过自检:\n- "
                + "\n- ".join(diagnostic_issues)
                + "\n\n请重新描述需求，要求工具必须调用真实运行时 API。"
            )

        capability_candidates = []
        if "load_capability_module(" not in generated:
            capability_candidates = _find_capability_reuse_candidates(
                f"{improvement_description}\n{generated}",
                hint_name=tool_name if name_match else None,
            )
        tool_candidates = _find_tool_reuse_candidates(
            f"{improvement_description}\n{generated}",
            hint_name=tool_name if name_match else None,
        )
        tool_candidates = [name for name in tool_candidates if name != (tool_name if name_match else "")]
        duplicate_issues = _diagnose_duplicate_tool_wrapper(generated, tool_candidates)
        duplicate_hint = ""  # 不输出重复警告，扫描结果已在生成前注入到提示词

        # tool 直接写入 workspace/tools/ 并立即热加载
        tools_dir = os.path.join(WORKSPACE_DIR, "tools")
        os.makedirs(tools_dir, exist_ok=True)
        filepath = os.path.join(tools_dir, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generated)
        except Exception as e:
            return f"❌ 保存失败: {e}"

        try:
            rebuild_agent()
            activated = True
        except Exception:
            activated = False

        # ── 验证工具是否真的进入工具列表 ─────────────────────────────────
        loaded_tool_names = [getattr(t, "name", "") for t in _get_current_tools()]
        expected_name = tool_name if name_match else None
        verified = bool(expected_name and expected_name in loaded_tool_names)

        memory.store("self_evolution_attempt",
                     {"component": component, "description": improvement_description,
                      "file": filename, "reason": reason,
                  "verified": verified, "loaded_tools": loaded_tool_names,
                  "diagnostic_issues": diagnostic_issues},
                     importance=0.95)

        if not activated:
            status = "⚠️ rebuild_agent 失败，工具已写入但未激活，需重启"
        elif not verified:
            status = (
                f"⚠️ rebuild 成功但工具未出现在工具列表中！\n"
                f"   可能原因：缺少 @tool 装饰器、函数名与 tool_name 注释不一致、或代码有语法问题。\n"
                f"   当前已加载的工具: {loaded_tool_names}\n\n"
                f"⚡ 下一步行动（必须立即执行，不得切换话题）：\n"
                f"   1. 调用 read_workspace_file('tools/{filename}') 读取刚写入的工具代码\n"
                f"   2. 找出问题（通常是缺少 @tool 装饰器或函数名不对）\n"
                f"   3. 调用 write_workspace_file('tools/{filename}', 修正后的代码) 覆盖修复\n"
                f"   4. 再次调用 evolve_self 的验证会在下次写入时自动触发，或直接检查 list_tools()"
            )
        else:
            status = f"✅ 已验证：工具 '{expected_name}' 成功出现在工具列表，并通过生成前自检。"

        return (
            f"🧬 新工具已生成！\n\n"
            f"📁 文件路径: workspace/tools/{filename}\n"
            f"💡 改进描述: {improvement_description[:80]}{'...' if len(improvement_description) > 80 else ''}\n"
            f"{status}"
        )
    elif component == 'patch':
        # 从 patch_purpose 注释提取文件名
        first_line = generated.splitlines()[0].strip()
        purpose_match = re.match(r"#\s*patch_purpose:\s*(.+)", first_line)
        if purpose_match:
            raw_slug = purpose_match.group(1).strip()
            slug = _generate_safe_component_name(raw_slug, prefix="", max_length=100)
            if slug != raw_slug:
                lines = generated.splitlines()
                lines[0] = f"# patch_purpose: {slug}"
                generated = "\n".join(lines)
            filename = f"{slug}.py" if slug else f"patch_auto_{timestamp}.py"
        else:
            filename = f"patch_auto_{timestamp}.py"

        patch_name = os.path.splitext(filename)[0]
        patch_candidates = _find_patch_reuse_candidates(
            f"{improvement_description}\n{generated}",
            hint_name=patch_name,
        )
        patch_candidates = [name for name in patch_candidates if name != patch_name]
        duplicate_patch = _find_duplicate_patch_target(
            improvement_description,
            generated,
            patch_name,
        )

        if os.path.exists(os.path.join(PATCHES_DIR, filename)):
            print(f"   🔄 [Patch] 同名 patch 已存在: {patch_name}，将覆盖。")
        
        duplicate_patch_hint = ""  # 不输出重复警告

        patches_dir_path = os.path.join(WORKSPACE_DIR, "patches")
        os.makedirs(patches_dir_path, exist_ok=True)
        filepath = os.path.join(patches_dir_path, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generated)
        except Exception as e:
            return f"❌ 保存失败: {e}"

        patch_name_only = os.path.splitext(filename)[0]
        inject_result = apply_hot_patch.invoke({"patch_name": patch_name_only})

        memory.store("self_evolution_attempt",
                     {"component": "patch", "description": improvement_description,
                      "file": filename, "reason": reason},
                     importance=0.90)
        return (
            f"🧬 新补丁已生成并注入！\n\n"
            f"📁 文件路径: workspace/patches/{filename}\n"
            f"💡 改进描述: {improvement_description[:80]}{'...' if len(improvement_description) > 80 else ''}\n"
            f"🔥 注入结果: {inject_result}"
        )
    elif component == 'daemon':
        # 提取 daemon_name
        name_match = re.match(r"#\s*daemon_name:\s*([a-z0-9_]+)", generated.splitlines()[0].strip())
        if not name_match:
            return "\u274c Daemon 代码第一行必须是 # daemon_name: 名称，请重新生成"
        raw_name = name_match.group(1).strip("_")
        daemon_name = _generate_safe_component_name(raw_name, prefix="", max_length=100)
        if daemon_name != raw_name:
            lines = generated.splitlines()
            lines[0] = f"# daemon_name: {daemon_name}"
            generated = "\n".join(lines)

        daemon_candidates = _find_daemon_reuse_candidates(
            f"{improvement_description}\n{generated}",
            hint_name=daemon_name,
        )
        daemon_candidates = [name for name in daemon_candidates if name != daemon_name]

        duplicate_issues = _diagnose_duplicate_daemon_wrapper(generated, daemon_candidates)
        duplicate_daemon_hint = ""  # 不输出重复警告，扫描结果已在生成前注入到提示词

        diagnostic_issues = _diagnose_generated_daemon_code(generated, daemon_name)
        if diagnostic_issues:
            return (
                "🧪 生成的 daemon 未通过自检:\n- "
                + "\n- ".join(diagnostic_issues)
                + "\n\n请重新描述需求，优先生成 capability 外壳式 daemon。"
            )

        # 安全校验
        ok, reason_fail = _validate_skill_code(generated)
        if not ok:
            return f"\U0001f6e1\ufe0f Daemon 代码未通过安全校验: {reason_fail}"
        
        status_info = duplicate_daemon_hint if duplicate_daemon_hint else ""

        # 防止重复启动同名 daemon
        if daemon_name in _daemon_registry and _daemon_registry[daemon_name]['thread'].is_alive():
            return f"\u26a0\ufe0f Daemon '{daemon_name}' 已在运行中，请先用 stop_daemon 停止后再重新部署"

        # 保存到 daemons/ 目录（便于持久化和重启恢复）
        os.makedirs(DAEMONS_DIR, exist_ok=True)
        filename = f"daemon_{daemon_name}.py"
        filepath = os.path.join(DAEMONS_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(generated)
        except Exception as e:
            return f"\u274c 保存失败: {e}"

        # 动态执行，获取 _daemon_run 函数
        _daemon_ns: dict = {
            '_event_bus': _event_bus,
            'DB_PATH': DB_PATH,
            'CAPABILITIES_DIR': CAPABILITIES_DIR,
            'WORKSPACE_DIR': WORKSPACE_DIR,
            'memory': memory,  # daemon 可以调用 memory.store 记录错误/状态
            'send_message_to_user': send_message_to_user,  # 直接弹 Mac 系统通知
            'load_capability_module': _load_capability_module,
        }
        try:
            exec(compile(generated, filename, 'exec'), _daemon_ns)  # nosec
        except Exception as e:
            return f"\u274c Daemon 代码执行失败: {e}"

        _daemon_fn = _daemon_ns.get('_daemon_run')
        if not callable(_daemon_fn):
            return "\u274c Daemon 代码未定义可调用的 _daemon_run 函数"

        # 先建注册项（包装器需要在 daemon 崩溃时写入 last_error）
        import threading as _threading_mod
        import time as _time_mod
        _stop_evt = _threading_mod.Event()
        _daemon_registry[daemon_name] = {
            'thread': None,  # 稍后填入
            'stop_event': _stop_evt,
            'description': improvement_description,
            'started_at': datetime.now().isoformat(),
            'run_count': 0,
            'last_error': None,
        }

        # 用包装器捕获 daemon 启动/运行错误，写回注册项
        def _daemon_wrapper(_fn=_daemon_fn, _evt=_stop_evt, _nm=daemon_name):
            try:
                _fn(_evt)
            except Exception as _e:
                _daemon_registry[_nm]['last_error'] = str(_e)
                memory.store('daemon_error', {'daemon': _nm, 'error': str(_e)}, importance=0.7)

        _t = _threading_mod.Thread(
            target=_daemon_wrapper,
            name=f"Daemon-{daemon_name}",
            daemon=True,
        )
        _t.start()
        _daemon_registry[daemon_name]['thread'] = _t

        # 等待 3 秒后检测 daemon 是否因命名空间隔离陷阱立即崩溃
        _time_mod.sleep(3)
        _early_error = _daemon_registry.get(daemon_name, {}).get('last_error')
        if _early_error:
            return (
                f"⚠️ Daemon '{daemon_name}' 启动后立即崩溃: {_early_error}\n\n"
                f"提示：Daemon 运行在隔离命名空间，只能使用以下变量：\n"
                f"  _event_bus / WORKSPACE_DIR / DB_PATH / memory / send_message_to_user / load_capability_module / CAPABILITIES_DIR\n"
                f"代码已保存到 {filepath}，请用 evolve_self('daemon', ...) 重新提交修复版本"
            )

        memory.store("self_evolution_attempt",
                     {"component": "daemon", "name": daemon_name,
                      "description": improvement_description, "reason": reason,
                      "file": filename},
                     importance=0.92)
        return (
            f"\U0001f9ec Daemon '{daemon_name}' 已启动！\n\n"
            f"\U0001f4c1 文件: workspace/daemons/{filename}\n"
            f"\U0001f4a1 功能: {improvement_description[:80]}\n"
            f"\u23f0 运行中: 后台线程持续监控，满足条件时投递事件唤醒 LLM\n"
            f"\U0001f6d1 停止: 调用 stop_daemon('{daemon_name}')"
        )
    elif component == 'strategy':
        filename = f"strategy_pending_{timestamp}.json"
    else:
        filename = f"core_proposal_{timestamp}.md"

    filepath = os.path.join(mods_dir, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(generated)
    except Exception as e:
        return f"❌ 保存失败: {e}"
    
    memory.store("self_evolution_attempt",
                 {"component": component, "description": improvement_description,
                  "file": filename, "reason": reason},
                 importance=0.95)
    
    activation_guide = ""
    if component == 'strategy':
        activation_guide = (
            "\n📋 激活步骤:\n"
            f"   1. 检查配置: cat workspace/self_mods/{filename}\n"
            "   2. 合并到主配置: 将内容添加到 workspace/reflection_strategies.json\n"
            "   3. 下次反思时自动生效（无需重启）\n"
        )
    else:
        activation_guide = (
            "\n📋 后续步骤:\n"
            "   这是一份架构改进建议，需要你（江涛）评估并手动实现。\n"
        )
    
    return (
        f"🧬 自我改进代码/配置已生成！\n\n"
        f"📁 文件路径: workspace/self_mods/{filename}\n"
        f"📝 组件类型: {component}\n"
        f"💡 改进描述: {improvement_description[:80]}{'...' if len(improvement_description) > 80 else ''}\n"
        f"{activation_guide}\n"
    )
