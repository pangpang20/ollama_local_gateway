#!/bin/bash

# 网关启动脚本

set -e

cd "$(dirname "$0")/gateway"

# 使用 Python 3.10
PYTHON_CMD=/usr/local/python3.10/bin/python3.10
PIP_CMD=/usr/local/python3.10/bin/pip3

# 检查环境变量
if [ -z "$SZC_API_KEY" ]; then
    echo "警告：SZC_API_KEY 环境变量未设置，将跳过 API Key 验证"
fi

# 安装依赖
echo "检查 Python 依赖..."
$PIP_CMD install -r requirements.txt -q

# 启动服务
echo "正在启动网关服务..."
echo "服务地址：http://0.0.0.0:8000"
echo ""

$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port 8000
