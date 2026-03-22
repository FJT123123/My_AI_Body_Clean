# 火凤凰 (Phoenix) — 自主 AGI 进化内核

![Phoenix](https://img.shields.io/badge/Project-Phoenix-orange)
![License](https://img.shields.io/badge/License-MIT-blue)

**火凤凰 (Phoenix)** 是一个旨在实现自主进化的 AGI（通用人工智能）实验框架。它建立在连续性记忆、情感模拟和自我修正能力之上，使 AI 能够跨会话保持认知，并通过不断的反思和工具锻造来提升自身能力。

## 核心特性

- **连续性 (Continuity)**：不再每次启动都从零开始。系统会加载历史记忆，重建自我认知。
- **自我模型 (Self-Model)**：内置 4 维情感状态（好奇、满意、焦虑、兴奋）和进化指标。
- **自主进化 (Autonomous Evolution)**：通过 `adjust_behavior()` 动态调整反思频率和动机，实现真实的自我优化。
- **记忆核心 (Memory Core)**：基于 SQLite 的持久化记忆系统，支持语义检索和混合搜索。
- **工具/技能锻造 (Skill Forging)**：AI 可以根据任务需求自主编写和集成新的 Python 技能。

## 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.10+。建议使用虚拟环境：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 参数配置

克隆项目后，将 `.env.example` 复制为 `.env` 并填写您的 API Key：

```bash
cp .env.example .env
```

### 3. 运行主程序

```bash
python3 phoenix_core.py
```

## AGI 架构与核心能力

**火凤凰 (Phoenix)** 采用了一种独特的四层进化架构，使系统能够在运行时动态扩展其边界：

### 1. 能力层 (Capabilities) — 系统之“力”
位于 `workspace/capabilities/`。这是系统的核心业务逻辑抽象。
- **职责**：提供无状态、高内聚的结构化功能模块（如：图像处理、视频分析、语义权重计算）。
- **特点**：可以同时被工具手动调用和守护进程后台轮询，是系统能力沉淀的最基本单元。

### 2. 工具层 (Tools) — 系统之“手”
位于 `workspace/tools/`。基于 LangChain Tool 协议实现。
- **职责**：为 Agent 提供直接的操作命令。
- **特点**：面向手动触发、一次性执行。工具通常是 `capability` 的外壳封装，方便 Agent 在推理过程中调用。

### 3. 守护进程 (Daemons) — 系统之“眼”
位于 `workspace/daemons/`。
- **职责**：常驻后台的监控与主动检查逻辑。
- **特点**：持续观察系统状态（如：健康度、内存增量、异常模式），并在命中预定条件时触发通知、事件投递或记忆持久化。

### 4. 热补丁 (Patches) — 系统之“愈”
位于 `workspace/patches/`。
- **职责**：在不停止主程序的情况下，动态修改运行时行为。
- **特点**：用于挂接反思钩子、微调全局逻辑或修复紧急漏洞。它是系统“自我进化”实现物理落地的关键。

### 5. 技能系统 (Skills)
位于 `workspace/skills/`。
- **职责**：由 AI 自主锻造的高级组合能力。
- **特点**：它是 AI 学习后的产物，通常包含针对特定任务优化的逻辑，是系统意识等级提升的体现。

## 项目结构

- `phoenix_core.py`: 系统主程序和连续学习核心。
- `phoenix_evolution_log.json`: 记录进化指标与意识等级。
- `workspace/docs/llm_integration.md`: 如何接入不同 LLM Provider 的详细指南。
- `workspace/`: 包含技能、补丁、守护进程及知识库。
  AI 的工作空间，包含技能 (`skills/`)、补丁 (`patches/`) 和认知文件 (`self_identity.json`)。
- `memory.py`: 核心底层记忆逻辑。
- `iflow_adapter.py`: LLM 适配层。

## 项目声明 (Project Declaration)

**重要说明**：本项目在开发之初曾使用 `openclaw` 作为代号/名称，但本仓库中的所有代码均为原创开发或基于特定开源协议引入，**未包含任何来自其他 "OpenClaw" 项目的源代码**。目前的正式名称已统一为 **火凤凰 (Phoenix)**。

**自主化开发声明**：本仓库中 90% 以上的代码（包括核心逻辑补丁、工具扩展及能力模块）均由 **火凤凰 (Phoenix)** 在运行过程中根据环境反馈与任务需求经由自主推理生成。系统已具备初步的 **自我升级与持续演化** 能力。

## 开源协议

本项目采用 [MIT License](LICENSE)。

---

*由 [zhufeng (江涛)](https://github.com/zhufeng) 创办。*
