# Ollama 本地网关

[English](README_EN.md) | 简体中文

基于 Ollama 的本地大模型 API 网关，提供与通义千问 Qwen3 系列模型兼容的接口格式。

## 功能特性

- 🚀 **本地部署** - 使用 Ollama 在本地运行 Qwen3 系列模型
- 🔄 **格式转换** - 自动转换请求/响应格式，完全兼容目标 API 规范
- 📡 **流式输出** - 支持 SSE 流式对话输出
- 🔐 **API Key 验证** - 支持请求头认证
- 📖 **OpenAPI 文档** - 内置 Swagger UI 文档

## 快速开始

### 1. 安装 Ollama

```bash
bash deploy_ollama.sh
```

或手动安装：
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. 拉取模型

```bash
ollama pull qwen3-embedding-4b
ollama pull qwen3:4b
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置 API Key
```

### 4. 启动网关

```bash
bash start_gateway.sh
```

服务启动后访问：
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000

## API 接口

### Embedding 接口

将文本转换为向量。

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-embedding/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Embedding-8B",
    "input": ["The capital of Brazil is Brasilia."]
  }'
```

### 对话接口（非流式）

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-coder-30b/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Coder-30B",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 对话接口（流式）

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-coder-30b/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Coder-30B",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": true
  }'
```

## 配置说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `SZC_API_KEY` | API 验证密钥 | 空（不验证） |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | `http://localhost:11434` |
| `EMBEDDING_MODEL` | Embedding 模型名称 | `qwen3-embedding-4b` |
| `CHAT_MODEL` | 对话模型名称 | `qwen3:4b` |
| `GATEWAY_HOST` | 网关监听地址 | `0.0.0.0` |
| `GATEWAY_PORT` | 网关端口 | `8000` |

## 项目结构

```
ollama_local_gateway/
├── deploy_ollama.sh       # Ollama 安装脚本
├── start_gateway.sh       # 网关启动脚本
├── .env.example           # 环境变量示例
├── README.md              # 中文文档
├── README_EN.md           # 英文文档
└── gateway/
    ├── main.py            # 网关主入口
    ├── config.py          # 配置管理
    ├── requirements.txt   # Python 依赖
    ├── clients/
    │   └── ollama_client.py  # Ollama API 客户端
    └── schemas/
        ├── embeddings.py  # Embedding 数据模型
        └── chat.py        # 对话数据模型
```

## 技术栈

- **后端框架**: FastAPI + Uvicorn
- **HTTP 客户端**: HTTPX (异步)
- **数据验证**: Pydantic
- **模型服务**: Ollama

## 开发

### 安装依赖

```bash
cd gateway
pip3 install -r requirements.txt
```

### 启动开发服务器

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 注意事项

1. **模型可用性**: 确保 Ollama 官方库中有 `qwen3-embedding-4b` 和 `qwen3:4b` 模型，否则需要修改 `config.py` 中的模型名称
2. **GPU 要求**: 运行 4B+ 参数模型需要足够的 GPU 显存（建议 8GB+）
3. **API Key**: 生产环境务必设置 `SZC_API_KEY`

## License

MIT
