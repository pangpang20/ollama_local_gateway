#!/bin/bash

# Ollama 安装和部署脚本

set -e

echo "=== Ollama 安装脚本 ==="

# 检测系统架构
ARCH=$(uname -m)
echo "检测到系统架构：$ARCH"

# 安装 Ollama
echo "正在安装 Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 检查安装结果
if command -v ollama &> /dev/null; then
    echo "Ollama 安装成功"
else
    echo "Ollama 安装失败"
    exit 1
fi

# 启动 Ollama 服务（后台运行）
echo "正在启动 Ollama 服务..."
nohup ollama serve > /var/log/ollama.log 2>&1 &

# 等待服务启动
sleep 5

# 拉取模型
echo "正在拉取模型..."

# 拉取 qwen3 embedding 模型
echo "拉取 qwen3-embedding-4b 模型..."
ollama pull qwen3-embedding-4b || {
    echo "警告：qwen3-embedding-4b 模型拉取失败，可能需要使用其他 embedding 模型"
}

# 拉取 qwen3 coder 模型
echo "拉取 qwen3:4b 模型..."
ollama pull qwen3:4b || {
    echo "警告：qwen3:4b 模型拉取失败，尝试拉取 qwen2.5-coder:7b"
    ollama pull qwen2.5-coder:7b
}

# 列出已安装的模型
echo ""
echo "=== 已安装的模型 ==="
ollama list

echo ""
echo "=== Ollama 安装完成 ==="
echo "服务地址：http://localhost:11434"
echo ""
echo "手动启动服务：ollama serve"
echo "查看模型列表：ollama list"
