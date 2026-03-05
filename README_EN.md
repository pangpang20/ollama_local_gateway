# Ollama Local Gateway

[简体中文](README.md) | English

A local LLM API gateway based on Ollama, providing API format compatibility with Alibaba Qwen3 series models.

## Features

- 🚀 **Local Deployment** - Run Qwen3 series models locally using Ollama
- 🔄 **Format Conversion** - Automatically convert request/response formats, fully compatible with target API specifications
- 📡 **Streaming Output** - Supports SSE streaming for chat responses
- 🔐 **API Key Verification** - Supports header-based authentication
- 📖 **OpenAPI Documentation** - Built-in Swagger UI documentation

## Quick Start

### 1. Install Ollama

```bash
bash deploy_ollama.sh
```

Or manually:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull Models

```bash
ollama pull qwen3-embedding:4b
ollama pull qwen3:4b
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env file to set API Key
```

### 4. Start Gateway

```bash
bash start_gateway.sh
```

After the service starts:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000

## API Endpoints

### Embedding Endpoint

Convert text to vectors.

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-embedding/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Embedding-8B",
    "input": ["The capital of Brazil is Brasilia."]
  }'
```

### Chat Endpoint (Non-streaming)

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-coder-30b/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Coder-30B",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Chat Endpoint (Streaming)

```bash
curl -X POST http://localhost:8000/gateway/ti/qwen3-coder-30b/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "szc-api-key: your-api-key" \
  -d '{
    "model": "Qwen3-Coder-30B",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

## Configuration

| Environment Variable | Description | Default Value |
|---------------------|-------------|---------------|
| `SZC_API_KEY` | API verification key | Empty (no verification) |
| `OLLAMA_BASE_URL` | Ollama service URL | `http://localhost:11434` |
| `EMBEDDING_MODEL` | Embedding model name | `qwen3-embedding:4b` |
| `CHAT_MODEL` | Chat model name | `qwen3:4b` |
| `GATEWAY_HOST` | Gateway listen address | `0.0.0.0` |
| `GATEWAY_PORT` | Gateway port | `8000` |

## Project Structure

```
ollama_local_gateway/
├── deploy_ollama.sh       # Ollama installation script
├── start_gateway.sh       # Gateway startup script
├── .env.example           # Environment variables example
├── README.md              # Chinese documentation
├── README_EN.md           # English documentation
└── gateway/
    ├── main.py            # Gateway main entry
    ├── config.py          # Configuration management
    ├── requirements.txt   # Python dependencies
    ├── clients/
    │   └── ollama_client.py  # Ollama API client
    └── schemas/
        ├── embeddings.py  # Embedding data models
        └── chat.py        # Chat data models
```

## Tech Stack

- **Backend Framework**: FastAPI + Uvicorn
- **HTTP Client**: HTTPX (async)
- **Data Validation**: Pydantic
- **Model Serving**: Ollama

## Development

### Install Dependencies

```bash
cd gateway
pip3 install -r requirements.txt
```

### Start Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Notes

1. **Model Availability**: Ensure `qwen3-embedding:4b` and `qwen3:4b` models are available in Ollama's official library, otherwise modify model names in `config.py`
2. **GPU Requirements**: Running 4B+ parameter models requires sufficient GPU VRAM (8GB+ recommended)
3. **API Key**: Always set `SZC_API_KEY` in production environments

## License

MIT
