#!/usr/bin/env python3
"""
简化的 OpenToad 测试脚本
只测试 Agent Network 集成到主窗口
"""
import sys
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

from apps.desktop.src.ui.agent_network_panel import AgentNetworkPanel


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = QMainWindow()
    window.setWindowTitle('🐸 OpenToad - Agent Network 集成测试')
    window.setMinimumSize(1200, 700)
    window.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
    """)

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)

    header = QWidget()
    header.setStyleSheet("background-color: #252526; border-bottom: 1px solid #3c3c3c; padding: 10px 20px;")
    header_layout = QHBoxLayout(header)

    title = QLabel("🐸 OpenToad - Agent Network 集成测试")
    title.setStyleSheet("color: #4ec9b0; font-size: 18px; font-weight: bold;")
    header_layout.addWidget(title)

    info = QLabel("测试侧边栏 + Agent Network 面板")
    info.setStyleSheet("color: #888; font-size: 12px;")
    header_layout.addWidget(info)

    layout.addWidget(header)

    agent_panel = AgentNetworkPanel()

    def on_back():
        print("返回按钮被点击")

    agent_panel.back_clicked.connect(on_back)
    layout.addWidget(agent_panel)

    window.setCentralWidget(central)
    window.show()

    print("=" * 60)
    print("✅ OpenToad Agent Network 集成测试已启动！")
    print("=" * 60)
    print()
    print("📋 测试功能：")
    print("   • 完整的 Agent Network 面板")
    print("   • 返回按钮（已连接到 on_back 方法）")
    print("   • Agent 列表管理")
    print("   • 任务创建和拆分")
    print()
    print("🎨 UI 特点：")
    print("   • 深色主题，与 OpenToad 一致")
    print("   • 青色高亮 (#4ec9b0)")
    print("   • 圆角边框设计")
    print()
    print("=" * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
