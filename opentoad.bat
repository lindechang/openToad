@echo off

REM OpenToad 启动脚本 (Windows)

REM 切换到项目根目录
cd /d "%~dp0"

REM 运行 OpenToad Python 脚本
python run_opentoad.py

REM 暂停以查看输出（可选）
pause