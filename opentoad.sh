#!/bin/bash

# OpenToad 启动脚本

# 切换到项目根目录
cd "$(dirname "$0")"

# 运行 OpenToad Python 脚本
/usr/local/opt/python@3.9/bin/python3 run_opentoad.py
