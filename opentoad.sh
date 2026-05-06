#!/bin/bash

# OpenToad 启动脚本

# 切换到项目根目录
cd "$(dirname "$0")"

# 运行 OpenToad Python 脚本
if command -v python3 &> /dev/null; then
    python3 run_opentoad.py
elif command -v python &> /dev/null; then
    python run_opentoad.py
else
    echo "Error: Python not found!"
    exit 1
fi
