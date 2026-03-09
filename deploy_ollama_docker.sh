#!/bin/bash

# Ollama Docker 安装和部署脚本
# 适用于系统库版本不兼容的环境

set -e

echo "=== Ollama Docker 安装脚本 ==="

# 检测系统架构
ARCH=$(uname -m)
echo "检测到系统架构：$ARCH"

# 定义 Docker 镜像
OLLAMA_IMAGE="ollama/ollama:latest"

# 定义容器名称
CONTAINER_NAME="ollama"

# 定义模型存储路径
MODEL_PATH="/var/lib/ollama/models"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误：未检测到 Docker"
    echo "请先安装 Docker:"
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

echo "Docker 版本：$(docker --version)"

# 创建模型存储目录
echo "创建模型存储目录：$MODEL_PATH"
mkdir -p "$MODEL_PATH"

# 停止并删除旧容器
echo "清理旧容器..."
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

# 启动 Ollama 容器
echo "启动 Ollama 容器..."
docker run -d \
    --name "$CONTAINER_NAME" \
    --restart=unless-stopped \
    -p 11434:11434 \
    -v "$MODEL_PATH:/root/.ollama" \
    -e OLLAMA_HOST=0.0.0.0 \
    "$OLLAMA_IMAGE"

# 等待容器启动
echo "等待容器启动..."
sleep 3

# 检查容器状态
CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null)
if [ "$CONTAINER_STATUS" != "running" ]; then
    echo "错误：容器启动失败"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

echo "Ollama 容器启动成功"

# 等待服务就绪
echo "等待服务就绪..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
        echo "服务已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "警告：服务响应超时，但容器运行正常"
        break
    fi
    sleep 1
done

# 显示版本
echo ""
echo "=== Ollama 版本 ==="
curl -s http://localhost:11434/api/version | python3 -m json.tool 2>/dev/null || curl -s http://localhost:11434/api/version

# 拉取模型
echo ""
echo "=== 拉取模型 ==="

# 拉取 qwen3 embedding 模型
echo "拉取 qwen3-embedding:4b 模型..."
docker exec "$CONTAINER_NAME" ollama pull qwen3-embedding:4b || {
    echo "警告：qwen3-embedding:4b 模型拉取失败"
}

# 拉取 qwen3 coder 模型
echo "拉取 qwen3:4b 模型..."
docker exec "$CONTAINER_NAME" ollama pull qwen3:4b || {
    echo "警告：qwen3:4b 模型拉取失败，尝试拉取 qwen2.5-coder:7b"
    docker exec "$CONTAINER_NAME" ollama pull qwen2.5-coder:7b || {
        echo "警告：qwen2.5-coder:7b 模型拉取失败"
    }
}

# 列出已安装的模型
echo ""
echo "=== 已安装的模型 ==="
docker exec "$CONTAINER_NAME" ollama list

echo ""
echo "=== Ollama Docker 部署完成 ==="
echo "服务地址：http://localhost:11434"
echo "模型存储：$MODEL_PATH"
echo ""
echo "管理命令:"
echo "  查看状态：docker ps | grep $CONTAINER_NAME"
echo "  查看日志：docker logs $CONTAINER_NAME"
echo "  停止服务：docker stop $CONTAINER_NAME"
echo "  启动服务：docker start $CONTAINER_NAME"
echo "  重启服务：docker restart $CONTAINER_NAME"
echo ""
