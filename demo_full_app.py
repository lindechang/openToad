#!/usr/bin/env python3
"""
OpenToad - 完整功能演示应用
展示 Agent Network 与主应用的集成
"""
import sys
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QTextEdit,
    QSplitter, QGroupBox, QFormLayout, QMessageBox, QFrame, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont

from apps.desktop.src.ui.agent_network_panel import AgentNetworkPanel


class MiniSidebar(QWidget):
    """简化版侧边栏"""
    chat_clicked = Signal()
    agent_network_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedWidth(180)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            border-right: 1px solid #333;
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addSpacing(10)

        # Agent Network 按钮
        agent_btn = QPushButton("🤖 Agent Network")
        agent_btn.setStyleSheet("""
            QPushButton {
                background-color: #3c7d3c;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 8px 12px;
                padding: 10px 12px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4a9a4a;
            }
        """)
        agent_btn.clicked.connect(self.agent_network_clicked.emit)
        layout.addWidget(agent_btn)

        # 返回聊天按钮
        chat_btn = QPushButton("💬 返回聊天")
        chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 0 12px;
                padding: 10px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        chat_btn.clicked.connect(self.chat_clicked.emit)
        layout.addWidget(chat_btn)

        layout.addStretch()

        # 版本信息
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("""
            color: #666;
            font-size: 11px;
            padding: 10px;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)


class ChatPage(QWidget):
    """模拟聊天页面"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题
        header = QLabel("💬 聊天")
        header.setStyleSheet("""
            background-color: #252526;
            color: #4ec9b0;
            font-size: 18px;
            font-weight: bold;
            padding: 15px 20px;
            border-bottom: 1px solid #3c3c3c;
        """)
        layout.addWidget(header)

        # 聊天区域
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        chat_layout.setContentsMargins(20, 20, 20, 20)

        info = QLabel("""
🐸 欢迎使用 OpenToad！

这是一个完整的 Agent-to-Agent 协作系统演示。

💡 功能特点：
• 多 Agent 协同工作
• 任务自动拆分与分配
• 角色分工（Coordinator/Worker/Researcher/Writer）
• 任务结果自动汇总

🔧 如何使用：
1. 点击左侧「🤖 Agent Network」进入 Agent 管理页面
2. 创建任务并拆分
3. 观察任务如何在 Agent 之间分配
4. 点击「← 返回聊天」返回此页面

⚙️ 配置：
• 在左侧点击「⚙️ 设置」配置 LLM API
• 支持 Claude、GPT、DeepSeek 等多种模型
        """)

        info.setStyleSheet("""
            background-color: #252526;
            border: 1px solid #3c3c3c;
            border-radius: 12px;
            padding: 20px;
            color: #d4d4d4;
            font-size: 14px;
            line-height: 1.8;
        """)
        chat_layout.addWidget(info)

        chat_layout.addStretch()

        layout.addWidget(chat_area)


class FullDemoApp(QMainWindow):
    """完整功能演示应用"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐸 OpenToad - Agent Network 完整演示")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)

        self._setup_ui()

    def _setup_ui(self):
        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 侧边栏
        self.sidebar = MiniSidebar()
        self.sidebar.agent_network_clicked.connect(self._show_agent_network)
        self.sidebar.chat_clicked.connect(self._show_chat)
        layout.addWidget(self.sidebar)

        # 分割线
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #333;")
        separator.setFixedWidth(1)
        layout.addWidget(separator)

        # 内容区域
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack, 1)

        # 聊天页面
        self.chat_page = ChatPage()
        self.content_stack.addWidget(self.chat_page)

        # Agent Network 页面
        self.agent_network_page = AgentNetworkPanel()
        self.agent_network_page.back_clicked.connect(self._show_chat)
        self.content_stack.addWidget(self.agent_network_page)

        # 默认显示聊天页面
        self.content_stack.setCurrentWidget(self.chat_page)

        # 状态栏
        self.statusBar().showMessage("🐸 OpenToad - Agent-to-Agent 协作系统")

    def _show_agent_network(self):
        """显示 Agent Network 页面"""
        self.content_stack.setCurrentWidget(self.agent_network_page)
        self.statusBar().showMessage("🤖 Agent Network - 管理多 Agent 协作")

    def _show_chat(self):
        """显示聊天页面"""
        self.content_stack.setCurrentWidget(self.chat_page)
        self.statusBar().showMessage("💬 返回聊天页面")


def main():
    print("=" * 70)
    print("🐸 OpenToad - Agent Network 完整演示")
    print("=" * 70)
    print()
    print("这个演示应用展示了：")
    print()
    print("1. ✅ 完整的侧边栏导航")
    print("   • 🤖 Agent Network 按钮（绿色高亮）")
    print("   • 💬 返回聊天按钮")
    print()
    print("2. ✅ 聊天页面")
    print("   • 功能说明和快速开始指南")
    print("   • 完整的使用说明")
    print()
    print("3. ✅ Agent Network 面板（完整功能）")
    print("   • Agent 列表管理")
    print("   • 任务创建和拆分")
    print("   • 任务详情展示")
    print("   • 返回按钮（已连接）")
    print()
    print("=" * 70)
    print()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = FullDemoApp()
    window.show()

    print("✅ 演示应用已启动！")
    print()
    print("💡 使用提示：")
    print("   1. 点击侧边栏的「🤖 Agent Network」进入 Agent 管理页面")
    print("   2. 在 Agent Network 页面中：")
    print("      - 查看左侧的 Agent 列表")
    print("      - 点击「✨ 新建任务」创建任务")
    print("      - 选择任务后点击「📌 拆分任务」拆分任务")
    print("      - 点击任务查看详情")
    print("   3. 点击「← 返回聊天」返回此页面")
    print()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
