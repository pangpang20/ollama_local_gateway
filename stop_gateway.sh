#!/bin/bash

# 网关停止脚本

set -e

echo "=== 停止 Ollama Gateway 服务 ==="

# 查找并停止 uvicorn 进程
PID=$(pgrep -f "uvicorn main:app")

if [ -z "$PID" ]; then
    echo "未找到运行中的网关服务"
    exit 0
fi

echo "找到网关进程：$PID"
echo "正在停止服务..."

# 停止进程
kill $PID

# 等待进程结束
for i in {1..10}; do
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "网关服务已停止"
        exit 0
    fi
    sleep 1
done

# 如果进程还在运行，强制停止
if ps -p $PID > /dev/null 2>&1; then
    echo "进程未响应，强制停止..."
    kill -9 $PID
    echo "网关服务已强制停止"
fi
