"""
反思质量守卫 —— 通过 TTR（词汇多样性）自动检测空转独白。
作为 _post_reflection_hooks 钩子注册，每次自主反思完后自动触发。
利用 _working_memory 跨反思累计空转计数，连续空转时采取更强的干预。
"""

import importlib.util as _ilu
import os as _os

_TTR_THRESHOLD   = 0.55   # 低于此值视为词汇重复→空转（中文字符级）
_MIN_WORDS       = 20     # 太短的文本跳过判断
_STREAK_WARN     = 3      # 连续空转多少次后降低动机
_STREAK_CRITICAL = 6      # 连续空转多少次后强制切换话题


def _ttr_quality_hook(ctx: dict) -> dict:
    """
    检测反思独白质量，并跨反思累计空转计数。
    返回: {'importance': float, 'ttr': float, 'hollow': bool, 'wm_updates': dict}
    """
    reply = ctx.get("reply", "")
    wm    = ctx.get("working_memory", {})   # 读取跨反思工作记忆

    if not reply:
        return {}

    try:
        _skill_path = _os.path.join(
            _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
            "skills", "skill_lightweight_language_complexity_analyzer.py"
        )
        if not _os.path.exists(_skill_path):
            return {}

        _spec = _ilu.spec_from_file_location("_ttr_skill", _skill_path)
        _mod  = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)

        r = _mod.main(reply).get("result", {})
        ttr        = r.get("ttr", 1.0)
        word_count = r.get("total_word_count", 0)
        avg_len    = r.get("avg_sentence_length", 0)

        if word_count < _MIN_WORDS:
            return {"ttr": ttr, "hollow": False, "wm_updates": {}}

        is_hollow     = ttr < _TTR_THRESHOLD
        hollow_streak = wm.get("hollow_streak", 0)  # 从工作记忆读取当前 streak

        if is_hollow:
            hollow_streak += 1
            tag = f"⚠️ 空转 (连续第 {hollow_streak} 次)"
            print(f"   📊 反思质量 [{tag}] TTR={ttr:.3f} 词={word_count} 句均长={avg_len:.1f}")

            if hollow_streak >= _STREAK_CRITICAL:
                # 强制切换：降低好奇心 + 拉高焦虑触发话题切换
                if "emotion" in globals():
                    emotion.curiosity = max(0.05, emotion.curiosity - 0.25)    # noqa
                    emotion.anxiety   = min(0.9,  emotion.anxiety   + 0.20)    # noqa
                print(f"   🚨 [守卫] 连续空转 {hollow_streak} 次，强制干预：降好奇+升焦虑促话题切换")
                if "memory" in globals():
                    memory.store("guard_critical",  # noqa
                        f"连续空转 {hollow_streak} 次，强制干预：降好奇+升焦虑 ttr={ttr:.3f}",
                        importance=0.6, tags=["guard", "hollow", "critical"])
                importance = 0.15
            elif hollow_streak >= _STREAK_WARN:
                if "emotion" in globals():
                    emotion.curiosity = max(0.1, emotion.curiosity - 0.15)     # noqa
                print(f"   ⚠️  [守卫] 连续空转 {hollow_streak} 次，降低好奇心")
                if "memory" in globals():
                    memory.store("guard_warn",  # noqa
                        f"连续空转 {hollow_streak} 次，降低好奇心 ttr={ttr:.3f}",
                        importance=0.4, tags=["guard", "hollow", "warn"])
                importance = 0.2
            else:
                if "emotion" in globals():
                    emotion.curiosity = max(0.1, emotion.curiosity - 0.10)     # noqa
                importance = 0.25

            return {
                "importance":  importance,
                "ttr":         ttr,
                "hollow":      True,
                "wm_updates":  {"hollow_streak": hollow_streak},
            }
        else:
            # 有效反思：重置 streak
            if hollow_streak > 0:
                print(f"   ✅ 反思质量恢复 TTR={ttr:.3f}（此前连续空转 {hollow_streak} 次，已重置）")
                if "memory" in globals():
                    memory.store("guard_recovery",  # noqa
                        f"反思质量恢复 ttr={ttr:.3f}，此前连续空转 {hollow_streak} 次",
                        importance=0.35, tags=["guard", "recovery"])
            return {
                "importance":  0.7,
                "ttr":         ttr,
                "hollow":      False,
                "wm_updates":  {"hollow_streak": 0},
            }

    except Exception as _e:
        print(f"   ⚠️  [TTR守卫] 异常: {_e}")
        return {}


# ── 注册（避免重复）──────────────────────────────────────────────────────────
if "_post_reflection_hooks" in globals():
    # 移除旧的同名钩子再重新注册
    _post_reflection_hooks[:] = [  # noqa
        h for h in _post_reflection_hooks  # noqa
        if getattr(h, "__name__", "") != "_ttr_quality_hook"
    ]
    _post_reflection_hooks.append(_ttr_quality_hook)  # noqa
    print("   🔌 [patch] reflection_quality_guard 已注册到 _post_reflection_hooks")
else:
    print("   ⚠️  [patch] _post_reflection_hooks 不存在，守卫无法注册")
