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
    }
    raw = os.getenv("MIMO_TIMEOUT_SEC") or os.getenv("IFLOW_TIMEOUT_SEC")
    try:
        return float(raw) if raw else default_map.get(model_type, 90.0)
    except Exception:
        return default_map.get(model_type, 90.0)

def get_mimo_llm(model_type="general", temperature=0.7):
    """
    获取 Xiaomi MiMo 的 AI 模型实例。
    """
    
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    model_name = os.getenv("MIMO_MODEL", "mimo-v2-pro")

    request_timeout = _resolve_timeout(model_type)

    print(f"🔌 [连接中] 正在接入 MiMo 神经单元: {model_name}...")

    if not api_key:
        print("⚠️  [警告] MIMO_API_KEY 未设置，请在 .env 中配置。")

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
        print(f"❌ MiMo 初始化失败: {e}")
        return None

# --- 测试区域 ---
if __name__ == "__main__":
    print("🚀 测试 MiMo 标准接口...")
    llm = get_mimo_llm()
    if llm:
        print("✅ MiMo 实例创建成功（可通过取消以下注释进行调用测试）。")
        # try:
        #     res = llm.invoke("你好")
        #     print(f"回答成功: {res.content}")
        # except Exception as e:
        #     print(f"❌ API 调用失败: {e}")
    else:
        print("❌ MiMo 实例创建失败。")
