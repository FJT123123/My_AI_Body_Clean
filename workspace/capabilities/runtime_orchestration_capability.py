# capability_name: runtime_orchestration_capability
"""Runtime orchestration capability.

This module owns runtime-adjustable orchestration logic so the main entry file
can stay thin and stable.
"""

import ast
import os
import re
import threading
import time
from datetime import datetime
from typing import Any, Dict


__contract__ = {
    "purpose": "Own runtime orchestration logic (patch/daemon/evolve) with editable capability code.",
    "public_callables": [
        "apply_hot_patch",
        "list_daemons",
        "stop_daemon",
        "auto_load_patches",
        "auto_restore_daemons",
        "normalize_patch_name",
        "should_auto_load_patch",
        "extend_patch_exec_namespace",
        "after_apply_hot_patch",
        "should_auto_restore_daemon",
        "daemon_boot_probe_seconds",
        "extend_daemon_exec_namespace",
        "after_restore_daemon",
        "evolve",
    ],
}


def _require_dict(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError(f"{name} 必须是 dict")
    return value


def _ctx_sections(ctx: Any):
    ctx = _require_dict(ctx, "ctx")
    paths = _require_dict(ctx.get("paths"), "ctx.paths")
    state = _require_dict(ctx.get("state"), "ctx.state")
    callbacks = _require_dict(ctx.get("callbacks"), "ctx.callbacks")
    services = _require_dict(ctx.get("services"), "ctx.services")
    runtime = _require_dict(ctx.get("runtime"), "ctx.runtime")
    return paths, state, callbacks, services, runtime


def normalize_patch_name(
    patch_name: str,
    ctx: Any = None,
) -> str:
    return patch_name


def should_auto_load_patch(
    patch_name: str,
    patch_path: str,
    ctx: Any = None,
) -> bool:
    return True


def extend_patch_exec_namespace(
    runtime_ns: Dict[str, Any],
    patch_name: str,
    patch_path: str,
    patch_code: str,
    ctx: Any = None,
) -> Dict[str, Any]:
    return {}


def after_apply_hot_patch(
    runtime_ns: Dict[str, Any],
    patch_name: str,
    patch_path: str,
    ctx: Any = None,
) -> None:
    return None


def should_auto_restore_daemon(
    daemon_name: str,
    daemon_file: str,
    daemon_path: str,
    ctx: Any = None,
) -> bool:
    return True


def daemon_boot_probe_seconds(
    daemon_name: str,
    daemon_file: str,
    daemon_path: str,
    default_seconds: float = 0.2,
    ctx: Any = None,
) -> float:
    return default_seconds


def extend_daemon_exec_namespace(
    exec_ns: Dict[str, Any],
    daemon_name: str,
    daemon_file: str,
    daemon_path: str,
    ctx: Any = None,
) -> Dict[str, Any]:
    return {}


def after_restore_daemon(
    daemon_name: str,
    daemon_file: str,
    daemon_path: str,
    daemon_registry: Dict[str, Any],
    ctx: Any = None,
) -> None:
    return None


def apply_hot_patch(patch_name: str, ctx: Any) -> str:
    paths, state, callbacks, services, runtime = _ctx_sections(ctx)
    patches_dir = str(paths.get("patches_dir", ""))
    runtime_ns = _require_dict(runtime.get("runtime_ns"), "ctx.runtime.runtime_ns")

    validate_skill_code = callbacks.get("validate_skill_code")
    patch_sandbox_test = callbacks.get("patch_sandbox_test")
    rebuild_agent = callbacks.get("rebuild_agent")
    if not callable(validate_skill_code):
        raise RuntimeError("ctx.callbacks.validate_skill_code 不可调用")
    if not callable(patch_sandbox_test):
        raise RuntimeError("ctx.callbacks.patch_sandbox_test 不可调用")

    memory = services.get("memory")
    post_reflection_hooks = state.get("post_reflection_hooks") or []

    normalized_patch_name = normalize_patch_name(patch_name=patch_name, ctx=ctx)
    if not isinstance(normalized_patch_name, str) or not normalized_patch_name.strip():
        raise RuntimeError("normalize_patch_name 必须返回非空字符串")

    clean = re.sub(r"[^a-zA-Z0-9_\-]", "", normalized_patch_name)
    if not clean:
        return "❌ 无效的补丁名称"

    os.makedirs(patches_dir, exist_ok=True)
    path = os.path.join(patches_dir, f"{clean}.py")
    if not os.path.abspath(path).startswith(os.path.abspath(patches_dir)):
        return "🛡️ 路径越界被拦截"
    if not os.path.exists(path):
        return f"❌ 补丁文件不存在: workspace/patches/{clean}.py"

    try:
        code = open(path, encoding="utf-8").read()
    except Exception as e:
        return f"❌ 读取失败: {e}"

    ok, reason = validate_skill_code(code)
    if not ok:
        return f"🛡️ 补丁未通过安全校验: {reason}"

    sandbox_ok, sandbox_msg = patch_sandbox_test(code, clean)
    if not sandbox_ok:
        return (
            f"🧪 沙箱预演失败: {sandbox_msg}\n\n"
            f"⚡ 下一步行动（必须立即执行）：\n"
            f"   1. 调用 read_workspace_file('patches/{clean}.py') 读取补丁代码\n"
            f"   2. 修正错误（不要使用 from workspace... import，直接使用 memory/run_skill 等全局变量）\n"
            f"   3. 调用 write_workspace_file('patches/{clean}.py', 修正后代码)\n"
            f"   → write_workspace_file 会自动重新注入，无需手动调用 apply_hot_patch"
        )

    extra_ns = extend_patch_exec_namespace(
        runtime_ns=runtime_ns,
        patch_name=clean,
        patch_path=path,
        patch_code=code,
        ctx=ctx,
    )
    if not isinstance(extra_ns, dict):
        raise RuntimeError("extend_patch_exec_namespace 必须返回 dict")
    runtime_ns.update(extra_ns)

    try:
        exec(compile(code, path, "exec"), runtime_ns)  # nosec
    except Exception as e:
        return (
            f"❌ 注入失败: {type(e).__name__}: {e}\n\n"
            f"⚡ 下一步行动（必须立即执行）：\n"
            f"   1. 调用 read_workspace_file('patches/{clean}.py') 读取补丁代码\n"
            f"   2. 找出错误（语法错误、引用了不存在的变量等）\n"
            f"   3. 调用 write_workspace_file('patches/{clean}.py', 修正后代码)\n"
            f"   4. 再次调用 apply_hot_patch('{clean}') 重新注入"
        )

    if callable(rebuild_agent):
        try:
            rebuild_agent()
        except Exception:
            pass

    hook_names = [getattr(h, "__name__", str(h)) for h in post_reflection_hooks]
    try:
        tree = ast.parse(code)
        defined_fns = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    except Exception:
        defined_fns = []

    missing_fns = [fn for fn in defined_fns if fn not in runtime_ns and not fn.startswith("_test")]
    if missing_fns:
        verify_note = f"⚠️ 以下函数未出现在全局命名空间（注入可能部分失败）: {missing_fns}"
    elif hook_names:
        verify_note = f"✅ 已验证: _post_reflection_hooks 当前钩子: {hook_names}"
    else:
        verify_note = "✅ 注入成功（无钩子注册，纯参数修改类补丁）"

    if hasattr(memory, "store"):
        memory.store("hot_patch_applied", {"patch": clean, "hooks": hook_names}, importance=0.88)

    after_apply_hot_patch(
        runtime_ns=runtime_ns,
        patch_name=clean,
        patch_path=path,
        ctx=ctx,
    )

    print(f"🔥 [热注入] 补丁 '{clean}' 已成功注入当前环境")
    return (
        f"✅ 补丁 '{clean}' 已热注入\n"
        f"  路径: workspace/patches/{clean}.py\n"
        f"  {verify_note}"
    )


def list_daemons(ctx: Any) -> str:
    _, state, _, _, _ = _ctx_sections(ctx)
    daemon_registry = _require_dict(state.get("daemon_registry"), "ctx.state.daemon_registry")

    if not daemon_registry:
        return "📭 当前没有已注册的守护进程。\n用 evolve_self('daemon', ...) 创建一个守护进程。"

    lines = [f"🛡️ 守护进程列表 ({len(daemon_registry)} 个):"]
    for name, info in daemon_registry.items():
        thread = info.get("thread")
        stop_evt = info.get("stop_event")
        alive = thread.is_alive() if thread else False
        stopped = stop_evt.is_set() if stop_evt else True
        status = "🟢 运行中" if alive and not stopped else "🔴 已停止"
        started = info.get("started_at", "未知")
        desc = info.get("description", "")[:60]
        run_count = info.get("run_count", "未知")
        last_error = info.get("last_error") or "无"
        lines.append(f"\n  [{name}]")
        lines.append(f"    状态: {status}")
        lines.append(f"    启动: {started}")
        lines.append(f"    执行次数: {run_count}")
        lines.append(f"    最近错误: {str(last_error)[:120]}")
        lines.append(f"    描述: {desc}")
    return "\n".join(lines)


def stop_daemon(daemon_name: str, ctx: Any) -> str:
    _, state, _, _, _ = _ctx_sections(ctx)
    daemon_registry = _require_dict(state.get("daemon_registry"), "ctx.state.daemon_registry")

    clean = re.sub(r"[^a-zA-Z0-9_]", "", daemon_name)
    if clean not in daemon_registry:
        registered = list(daemon_registry.keys())
        return (
            f"❌ 找不到守护进程 '{clean}'。\n"
            f"已注册的守护进程: {registered}\n"
            f"用 list_daemons() 查看完整列表。"
        )

    info = daemon_registry[clean]
    stop_evt = info.get("stop_event")
    thread = info.get("thread")

    if stop_evt and not stop_evt.is_set():
        stop_evt.set()

    if thread and thread.is_alive():
        thread.join(timeout=5.0)
        if thread.is_alive():
            return (
                f"⚠️ 守护进程 '{clean}' 停止信号已发送，但线程在5秒内未退出。\n"
                "建议检查 daemon 代码中是否有阻塞操作忘记 check stop_event。"
            )

    del daemon_registry[clean]
    return (
        f"✅ 守护进程 '{clean}' 已停止并从注册表移除。\n"
        f"剩余活跃守护进程: {list(daemon_registry.keys())}"
    )


def auto_load_patches(ctx: Any) -> None:
    paths, _, callbacks, _, runtime = _ctx_sections(ctx)
    patches_dir = str(paths.get("patches_dir", ""))
    runtime_ns = _require_dict(runtime.get("runtime_ns"), "ctx.runtime.runtime_ns")

    validate_skill_code = callbacks.get("validate_skill_code")
    if not callable(validate_skill_code):
        raise RuntimeError("ctx.callbacks.validate_skill_code 不可调用")

    if not os.path.isdir(patches_dir):
        return

    patch_files = sorted(
        f[:-3]
        for f in os.listdir(patches_dir)
        if f.endswith(".py") and not f.startswith("_") and not f.startswith("daemon_")
    )
    if not patch_files:
        return

    print(f"\n🔌 [自动补丁] 发现 {len(patch_files)} 个补丁，逐一加载...")
    for name in patch_files:
        path = os.path.join(patches_dir, f"{name}.py")

        should_load = should_auto_load_patch(patch_name=name, patch_path=path, ctx=ctx)
        if not isinstance(should_load, bool):
            print(f"   ❌ [{name}] should_auto_load_patch 必须返回 bool")
            continue
        if not should_load:
            print(f"   ⏭️  [{name}] 被 runtime_orchestration_capability 跳过")
            continue

        try:
            code = open(path, encoding="utf-8").read()
        except Exception as e:
            print(f"   ⚠️  [{name}] 读取失败: {e}")
            continue

        ok, reason = validate_skill_code(code)
        if not ok:
            print(f"   🛡️  [{name}] 安全校验未通过: {reason}")
            continue

        extra_ns = extend_patch_exec_namespace(
            runtime_ns=runtime_ns,
            patch_name=name,
            patch_path=path,
            patch_code=code,
            ctx=ctx,
        )
        if not isinstance(extra_ns, dict):
            print(f"   ❌ [{name}] extend_patch_exec_namespace 必须返回 dict")
            continue
        runtime_ns.update(extra_ns)

        try:
            exec(compile(code, path, "exec"), runtime_ns)  # nosec
            after_apply_hot_patch(
                runtime_ns=runtime_ns,
                patch_name=name,
                patch_path=path,
                ctx=ctx,
            )
            print(f"   ✅ [{name}] 已加载")
        except Exception as e:
            print(f"   ❌ [{name}] 加载失败: {type(e).__name__}: {e}")


def auto_restore_daemons(ctx: Any) -> None:
    paths, state, callbacks, services, _ = _ctx_sections(ctx)
    daemons_dir = str(paths.get("daemons_dir", ""))
    db_path = str(paths.get("db_path", ""))
    capabilities_dir = str(paths.get("capabilities_dir", ""))
    workspace_dir = str(paths.get("workspace_dir", ""))

    daemon_registry = _require_dict(state.get("daemon_registry"), "ctx.state.daemon_registry")
    event_bus = services.get("event_bus")
    memory = services.get("memory")
    send_message_to_user = services.get("send_message_to_user")
    load_capability_module = callbacks.get("load_capability_module") or services.get("load_capability_module")

    validate_skill_code = callbacks.get("validate_skill_code")
    if not callable(validate_skill_code):
        raise RuntimeError("ctx.callbacks.validate_skill_code 不可调用")

    if not os.path.isdir(daemons_dir):
        return

    daemon_files = sorted(
        f for f in os.listdir(daemons_dir) if f.startswith("daemon_") and f.endswith(".py")
    )
    if not daemon_files:
        return

    print(f"\n🛡️  [守护进程恢复] 发现 {len(daemon_files)} 个 daemon，自动重启...")
    for fname in daemon_files:
        path = os.path.join(daemons_dir, fname)
        try:
            code = open(path, encoding="utf-8").read()
        except Exception as e:
            print(f"   ⚠️  [{fname}] 读取失败: {e}")
            continue

        first_line = code.strip().splitlines()[0].strip()
        name_match = re.match(r"#\s*daemon_name:\s*([a-z0-9_]+)", first_line)
        if not name_match:
            print(f"   ⚠️  [{fname}] 缺少 daemon_name 注释，跳过")
            continue

        daemon_name = name_match.group(1)[:30]
        should_restore = should_auto_restore_daemon(
            daemon_name=daemon_name,
            daemon_file=fname,
            daemon_path=path,
            ctx=ctx,
        )
        if not isinstance(should_restore, bool):
            print(f"   ❌ [{daemon_name}] should_auto_restore_daemon 必须返回 bool")
            continue
        if not should_restore:
            print(f"   ⏭️  [{daemon_name}] 被 runtime_orchestration_capability 跳过")
            continue

        if daemon_name in daemon_registry and daemon_registry[daemon_name].get("thread") and daemon_registry[daemon_name]["thread"].is_alive():
            print(f"   ⏭️  [{daemon_name}] 已在运行，跳过")
            continue

        ok, reason = validate_skill_code(code)
        if not ok:
            print(f"   🛡️  [{daemon_name}] 安全校验未通过: {reason}")
            continue

        ns = {
            "_event_bus": event_bus,
            "DB_PATH": db_path,
            "CAPABILITIES_DIR": capabilities_dir,
            "WORKSPACE_DIR": workspace_dir,
            "memory": memory,
            "send_message_to_user": send_message_to_user,
            "load_capability_module": load_capability_module,
        }
        extra_ns = extend_daemon_exec_namespace(
            exec_ns=ns,
            daemon_name=daemon_name,
            daemon_file=fname,
            daemon_path=path,
            ctx=ctx,
        )
        if not isinstance(extra_ns, dict):
            print(f"   ❌ [{daemon_name}] extend_daemon_exec_namespace 必须返回 dict")
            continue
        ns.update(extra_ns)

        try:
            exec(compile(code, path, "exec"), ns)  # nosec
        except Exception as e:
            print(f"   ❌ [{daemon_name}] 执行失败: {e}")
            continue

        daemon_fn = ns.get("_daemon_run")
        if not callable(daemon_fn):
            print(f"   ❌ [{daemon_name}] 未找到 _daemon_run 函数")
            continue

        stop_evt = threading.Event()
        daemon_registry[daemon_name] = {
            "thread": None,
            "stop_event": stop_evt,
            "description": f"自动恢复: {fname}",
            "started_at": datetime.now().isoformat(),
            "run_count": 0,
            "last_error": None,
        }

        def _daemon_wrapper(_fn=daemon_fn, _evt=stop_evt, _nm=daemon_name):
            try:
                _fn(_evt)
            except Exception as _e:
                if _nm in daemon_registry:
                    daemon_registry[_nm]["last_error"] = str(_e)
                if hasattr(memory, "store"):
                    try:
                        memory.store("daemon_error", {"daemon": _nm, "error": str(_e)}, importance=0.7)
                    except Exception:
                        pass

        t = threading.Thread(
            target=_daemon_wrapper,
            name=f"Daemon-{daemon_name}",
            daemon=True,
        )
        t.start()
        daemon_registry[daemon_name]["thread"] = t

        wait_seconds = daemon_boot_probe_seconds(
            daemon_name=daemon_name,
            daemon_file=fname,
            daemon_path=path,
            default_seconds=0.2,
            ctx=ctx,
        )
        try:
            wait_seconds = float(wait_seconds)
        except Exception:
            print(f"   ❌ [{daemon_name}] daemon_boot_probe_seconds 必须返回数值")
            continue

        wait_seconds = max(0.0, min(wait_seconds, 3.0))
        time.sleep(wait_seconds)
        early_error = daemon_registry.get(daemon_name, {}).get("last_error")
        if early_error:
            print(f"   ⚠️  [{daemon_name}] 启动后立即崩溃: {early_error}")
            continue

        after_restore_daemon(
            daemon_name=daemon_name,
            daemon_file=fname,
            daemon_path=path,
            daemon_registry=daemon_registry,
            ctx=ctx,
        )
        print(f"   ✅ [{daemon_name}] 已恢复运行")


def evolve(
    component: str,
    improvement_description: str,
    reason: str,
    ctx: Any = None,
) -> str:
    paths, _, _, _, runtime = _ctx_sections(ctx)
    capabilities_dir = str(paths.get("capabilities_dir", ""))
    runtime_ns = _require_dict(runtime.get("runtime_ns"), "ctx.runtime.runtime_ns")

    impl = runtime_ns.get("_workspace_evolve_impl")
    if not callable(impl):
        impl_path = os.path.join(capabilities_dir, "evolution_runtime_impl.py")
        if not os.path.exists(impl_path):
            raise RuntimeError(f"缺少进化实现文件: {impl_path}")
        code = open(impl_path, encoding="utf-8").read()
        exec(compile(code, impl_path, "exec"), runtime_ns)  # nosec
        impl = runtime_ns.get("_workspace_evolve_impl")
        if not callable(impl):
            raise RuntimeError("evolution_runtime_impl.py 未定义可调用的 _workspace_evolve_impl")

    return impl(component, improvement_description, reason)
