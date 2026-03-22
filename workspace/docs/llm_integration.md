# LLM 接入指南 (LLM Integration Guide)

**火凤凰 (Phoenix)** 默认通过 `iflow_adapter.py` 接入模型。为了支持多模型分工，系统将大脑划分为三个核心单元：
- `llm_agent`: 通用推理、决策与工具调用。
- `llm_forge`: 代码生成、技能锻造（需要强的代码理解能力）。
- `llm_think`: 深度反思、长链推理（推荐使用 DeepSeek-R1 等模型）。

## 方式一：修改环境变量 (最简单)

如果你的 Provider 支持 OpenAI 兼容接口（如 One-API, New-API, 或 DeepSeek/OpenRouter），只需修改 `.env`：

```bash
# iFlow 基础配置
IFLOW_API_KEY=your_api_key_here
IFLOW_BASE_URL=https://api.your-provider.com/v1

# 模型指定
DEFAULT_MODEL=gpt-4o           # 对应 llm_agent
CODER_MODEL=claude-3-5-sonnet  # 对应 llm_forge
REASONING_MODEL=deepseek-reasoner # 对应 llm_think
```

## 方式二：接入原生 Provider (LangChain)

如果你想使用非 OpenAI 兼容的 SDK（如原生的 Anthropic 或 Google Gemini），请修改 `iflow_adapter.py`。

### 1. 安装依赖
```bash
pip install langchain-anthropic langchain-google-genai
```

### 2. 修改适配器逻辑
在 `iflow_adapter.py` 中，你可以根据 `model_name` 或通过新增环境变量来切换类：

```python
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def get_iflow_llm(model_type="general", temperature=0.7):
    # ... 原有获取 model_name 的逻辑 ...
    
    if "claude" in model_name.lower():
        return ChatAnthropic(model=model_name, api_key=...)
    elif "gemini" in model_name.lower():
        return ChatGoogleGenerativeAI(model=model_name, api_key=...)
    else:
        # 默认使用 OpenAI 兼容类
        return ChatOpenAI(model=model_name, base_url=...)
```

## 方式三：接入本地模型 (Ollama / vLLM)

如果你希望在本地运行：

1. **Ollama**:
   将 `IFLOW_BASE_URL` 设置为 `http://localhost:11434/v1`，并在 `DEFAULT_MODEL` 中填写你 pull 的模型名称（如 `llama3`）。

2. **vLLM**:
   将 `IFLOW_BASE_URL` 指向 vLLM 的 API server 地址。

## 性能调优建议

- **Context Window**: 建议为 `llm_agent` 提供至少 32k 的上下文，以支持长对话恢复。
- **Temperature**: 系统默认 `temperature=0.7`。对于 `llm_forge`（代码生成），建议在调用时设为 `0.2` 或更低。
- **Timeout**: 在 `iflow_adapter.py` 中有针对不同单元的超时设置 (`_resolve_timeout`)。如果使用慢推理模型（如 R1），请确保 `thinker` 的超时时间足够长（默认 240s）。
