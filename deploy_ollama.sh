#!/bin/bash

# Ollama 安装和部署脚本

set -e

echo "=== Ollama 安装脚本 ==="

# 检测系统架构
ARCH=$(uname -m)
echo "检测到系统架构：$ARCH"

# 定义离线安装包路径
OFFLINE_PACKAGE="ollama-linux-amd64.tar.zst"

# 安装 Ollama
if [ -f "$OFFLINE_PACKAGE" ]; then
    echo "检测到离线安装包：$OFFLINE_PACKAGE"
    echo "使用离线安装模式..."

    # 检查是否安装了 zstd
    if ! command -v zstd &> /dev/null; then
        echo "错误：离线安装需要 zstd 工具，请先安装 zstd"
        echo "安装方法："
        echo "  Ubuntu/Debian: sudo apt-get install zstd"
        echo "  CentOS/RHEL: sudo yum install zstd"
        echo "  或使用在线安装模式"
        exit 1
    fi

    # 解压离线安装包到临时目录
    echo "正在解压安装包..."
    TEMP_DIR=$(mktemp -d)
    sudo tar --use-compress-program=zstd -xf "$OFFLINE_PACKAGE" -C "$TEMP_DIR" || {
        echo "解压失败，请检查安装包是否完整"
        rm -rf "$TEMP_DIR"
        exit 1
    }

    # 复制文件到系统目录
    echo "正在安装文件..."
    sudo cp -r "$TEMP_DIR/bin/ollama" /usr/local/bin/
    sudo cp -r "$TEMP_DIR/lib/ollama" /usr/local/lib/ollama

    # 清理临时目录
    rm -rf "$TEMP_DIR"

    # 设置环境变量（添加到用户 profile）
    if ! grep -q "OLLAMA_MODELS" ~/.bashrc 2>/dev/null; then
        echo "" >> ~/.bashrc
        echo "export OLLAMA_MODELS=/usr/local/lib/ollama" >> ~/.bashrc
        echo "export LD_LIBRARY_PATH=/usr/local/lib/ollama:\$LD_LIBRARY_PATH" >> ~/.bashrc
    fi

    # 设置执行权限
    sudo chmod +x /usr/local/bin/ollama

    echo "离线安装完成"
else
    echo "未检测到离线安装包，使用在线安装模式..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 检查安装结果
if command -v ollama &> /dev/null; then
    echo "Ollama 安装成功"
    ollama --version
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
echo "拉取  qwen3-embedding:4b 模型..."
ollama pull  qwen3-embedding:4b || {
    echo "警告： qwen3-embedding:4b 模型拉取失败，可能需要使用其他 embedding 模型"
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
