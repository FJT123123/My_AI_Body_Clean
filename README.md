# My AI Body / OpenClaw

An experimental autonomous-agent runtime that explores continuity, persistent memory, self-modeling, dynamic capabilities, skills, daemons, patches, and workspace-level evolution.

> This repository is a research system, not a production-safe autonomous runtime. Generated or dynamically loaded code can perform local actions. Run it only in an isolated environment with credentials and filesystem access scoped to the minimum required.

## Current runtime entrypoint

The current root runtime is:

```bash
python openclaw_continuity.py
```

`openclaw_continuity.py` contains the continuity kernel and coordinates the persistent memory, emotional state, evolution metrics, tool discovery, capabilities, skills, daemons, patches, and the main agent loop.

## Repository layout

- `openclaw_continuity.py` — continuity kernel and current executable entrypoint
- `iflow_adapter.py` — iFlow/OpenAI-compatible model adapter
- `mimo_adapter.py` — Xiaomi MiMo/OpenAI-compatible model adapter
- `workspace/capabilities/` — runtime capabilities and capability implementations
- `workspace/skills/` — generated or curated skills
- `workspace/tools/` — callable tools and diagnostics
- `workspace/daemons/` — background runtime components
- `workspace/patches/` — runtime patch experiments
- `workspace/rules/` — generated or curated runtime rules
- `workspace/docs/` — architecture and generation-rule documentation
- `PLAN/` and `AAA/` — research notes and experimental artifacts; these are not part of the minimal runtime contract

## Quick start

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in at least one provider configuration in `.env`, then run:

```bash
python openclaw_continuity.py
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Model providers

Select the provider with:

```env
LLM_PROVIDER=iflow
```

Supported root adapters currently include:

- `iflow` through `IFLOW_API_KEY` and `IFLOW_BASE_URL`
- `mimo` through `MIMO_API_KEY` and `MIMO_BASE_URL`

Model names and request timeouts can be overridden in `.env`; see `.env.example`.

## Persistence

The continuity runtime stores local state under `workspace/`, including SQLite memory and evolution state. Database files, logs, generated media, and common validation outputs are excluded by `.gitignore` and should not be treated as source code.

Before switching branches or replacing a runtime, back up any local memory database that you intend to preserve.

## Dependencies

`requirements.txt` contains the core runtime dependencies. Individual generated capabilities may require additional packages such as media, OCR, browser, or platform-specific libraries. Those optional dependencies should be documented alongside the capability that uses them rather than silently added to the core runtime.

## Validation

The repository smoke workflow checks:

- required project-contract files exist
- root runtime files are valid Python syntax
- no external API call is required during the check

A passing smoke check does not prove autonomous behavior, model connectivity, memory correctness, or safety. Those require focused tests and controlled integration environments.

## License

MIT. See `LICENSE`.
