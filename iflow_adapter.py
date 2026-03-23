import os
import sys

# AGI Rebirth: 增加本地依赖库路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_lib_path = os.path.join(_current_dir, "lib")
if os.path.exists(_lib_path) and _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

# 加载环境变量
load_dotenv()


def _resolve_timeout(model_type="general"):
    default_map = {
        "general": 90.0,
        "coder": 180.0,
        "thinker": 240.0,
        "vision": 120.0,
    }
    env_key_map = {
        "general": "IFLOW_GENERAL_TIMEOUT_SEC",
        "coder": "IFLOW_CODER_TIMEOUT_SEC",
        "thinker": "IFLOW_THINKER_TIMEOUT_SEC",
        "vision": "IFLOW_VISION_TIMEOUT_SEC",
    }
    raw = os.getenv(env_key_map.get(model_type, "")) or os.getenv("IFLOW_TIMEOUT_SEC")
    try:
        return float(raw) if raw else default_map.get(model_type, 90.0)
    except Exception:
        return default_map.get(model_type, 90.0)

def get_iflow_llm(model_type="general", temperature=0.7):
    """
    获取 iFlow 的 AI 模型实例。
    
    参数 model_type:
      - 'general':  通用对话 (qwen3-max)
      - 'coder':    写代码专用 (qwen3-coder-plus)
      - 'thinker':  深度推理 (deepseek-r1)
    """
    
    api_key = os.getenv("IFLOW_API_KEY")
    base_url = os.getenv("IFLOW_BASE_URL")
    
    # 根据用途自动选择最佳模型
    if model_type == "coder":
        model_name = os.getenv("CODER_MODEL", "qwen3-coder-plus")
    elif model_type == "thinker":
        model_name = os.getenv("REASONING_MODEL", "qwen3-235b-a22b-thinking-2507")
    elif model_type == "vision":
        model_name = os.getenv("VISION_MODEL", "qwen-vl-max")  # iFlow支持视觉的模型
    else:
        model_name = os.getenv("DEFAULT_MODEL", "qwen3-max")

    request_timeout = _resolve_timeout(model_type)

    print(f"🔌 [连接中] 正在接入神经单元: {model_name}...")

    try:
        llm = ChatOpenAI(
            model=model_name,
            api_key=SecretStr(api_key) if api_key else None,
            base_url=base_url,
            temperature=temperature,
            model_kwargs={"max_tokens": 4096},
            max_retries=2,
            timeout=request_timeout,
        )
        return llm
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return None

# --- 测试区域 ---
if __name__ == "__main__":
    print("🚀 测试 iFlow 标准接口...")
    
    # 1. 测试写代码能力
    coder = get_iflow_llm("coder")
    print("\n📝 [测试写代码] 正在请求 qwen3-coder-plus...")
    if coder is None:
        raise RuntimeError("coder 模型初始化失败")
    res = coder.invoke("用 Python 写一个 Hello World 函数")
    print(f"回答: {res.content[:50]}...")

    # 2. 测试深度思考能力 (可选)
    # thinker = get_iflow_llm("thinker")
    # print("\n🤔 [测试深度思考] 正在请求 deepseek-r1...")
    # res = thinker.invoke("为什么天空是蓝色的？")
    # print(f"回答: {res.content[:50]}...")
    
    print("\n✅ 能源系统自检完成。")