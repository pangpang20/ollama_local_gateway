import os
from dotenv import load_dotenv

load_dotenv()

# Ollama 配置
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# API Key 配置
API_KEY = os.getenv("SZC_API_KEY", "")

# 模型配置
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:4b")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen3:4b")

# 网关配置
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "8000"))
