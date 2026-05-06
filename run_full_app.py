#!/usr/bin/env python3
"""
OpenToad - 完整主应用
包含所有功能：聊天、设置、账号、记忆体 + Agent Network
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # 导入并运行主应用
    from apps.desktop.src.main import main
    main()
