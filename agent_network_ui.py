#!/usr/bin/env python3
"""
OpenToad - Agent Network UI Panel
直接运行此文件启动 Agent Network 面板
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from apps.desktop.src.ui.agent_network_panel import AgentNetworkPanel


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = QMainWindow()
    window.setWindowTitle('🐸 OpenToad - Agent Network Panel')
    window.setMinimumSize(1200, 700)
    window.setStyleSheet('''
        QMainWindow {
            background-color: #1e1e1e;
        }
    ''')

    central = QWidget()
    layout = QVBoxLayout(central)
    layout.setContentsMargins(0, 0, 0, 0)

    agent_panel = AgentNetworkPanel()
    layout.addWidget(agent_panel)

    window.setCentralWidget(central)
    window.show()

    print('=' * 60)
    print('🐸 OpenToad - Agent Network Panel 已启动！')
    print('=' * 60)
    print()
    print('📋 功能说明：')
    print('   • 左侧面板：Agent 列表')
    print('     - 已预置 5 个 Agent（Coordinator/Worker/Researcher/Writer/Reviewer）')
    print('     - 点击 Agent 查看详情')
    print('     - 点击「+ 添加 Agent」添加新 Agent')
    print()
    print('   • 右侧面板：任务管理')
    print('     - 「✨ 新建任务」- 创建新任务')
    print('     - 「📌 拆分任务」- 将任务拆分为子任务')
    print('     - 「🔄 刷新」- 刷新任务列表')
    print('     - 点击任务查看详情')
    print()
    print('🎨 主题：深色主题，与 OpenToad 风格一致')
    print()
    print('=' * 60)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
