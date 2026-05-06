# apps/desktop/src/ui/agent_network_panel.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QSplitter,
    QTextEdit, QGroupBox, QFormLayout, QComboBox,
    QMessageBox, QScrollArea, QFrame, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QObject, QRectF
from PySide6.QtGui import QFont, QPainter, QPainterPath, QIcon, QPixmap
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agent_network import (
    AgentInfo, AgentRole, Task, TaskStatus,
    LocalAgentRegistry, TaskOrchestrator, TaskResult
)


class AgentSignals(QObject):
    task_updated = Signal(str)
    back_clicked = Signal()


class AgentNetworkPanel(QWidget):
    back_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
        """)
        self.registry = LocalAgentRegistry()
        self.orchestrator = TaskOrchestrator(self.registry)
        self.signals = AgentSignals()
        self._init_ui()
        self._init_sample_agents()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #252526; border-bottom: 1px solid #3c3c3c;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 12, 16, 12)

        back_btn = QPushButton("← 返回聊天")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        back_btn.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(back_btn)

        header_layout.addStretch()

        title = QLabel("🤖 Agent Network")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ec9b0;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        layout.addWidget(header_widget)

        splitter = QSplitter(Qt.Horizontal)

        left_panel = self._create_agents_panel()
        right_panel = self._create_tasks_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 750])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3c3c3c;
                width: 2px;
            }
        """)

        layout.addWidget(splitter)

    def _on_back_clicked(self):
        """返回按钮点击"""
        self.back_clicked.emit()

    def _create_title_widget(self, title, icon="🐸"):
        """创建标题组件"""
        title_widget = QWidget()
        title_widget.setStyleSheet("""
            background-color: #252526;
            border-bottom: 1px solid #3c3c3c;
            padding: 12px 16px;
        """)
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 8, 0, 8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 18px;")

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setStyleSheet("color: #4ec9b0; letter-spacing: 1px;")

        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        return title_widget

    def _create_agents_panel(self) -> QWidget:
        """创建 Agent 列表面板"""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        title_widget = self._create_title_widget("Agent Network", "🤖")
        panel_layout.addWidget(title_widget)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        info_label = QLabel("已注册的 Agent（点击查看详情）")
        info_label.setStyleSheet("color: #888; font-size: 12px; padding-bottom: 8px;")
        content_layout.addWidget(info_label)

        self.agent_list = QListWidget()
        self.agent_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 6px;
                margin: 4px 0;
                background-color: #2d3d4a;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        self.agent_list.itemClicked.connect(self._on_agent_selected)
        content_layout.addWidget(self.agent_list, 1)

        btn_layout = QHBoxLayout()
        self.btn_add_agent = QPushButton("+ 添加 Agent")
        self.btn_add_agent.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.btn_add_agent.clicked.connect(self._add_sample_agent)
        btn_layout.addWidget(self.btn_add_agent)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        agent_info_group = QGroupBox("Agent 详情")
        agent_info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        agent_info_layout = QFormLayout(agent_info_group)
        agent_info_layout.setSpacing(10)

        self.agent_name_label = QLabel("-")
        self.agent_name_label.setStyleSheet("color: #d4d4d4; font-size: 13px;")
        self.agent_role_label = QLabel("-")
        self.agent_role_label.setStyleSheet("color: #4ec9b0; font-size: 13px; font-weight: bold;")
        self.agent_status_label = QLabel("-")
        self.agent_status_label.setStyleSheet("color: #888; font-size: 13px;")

        agent_info_layout.addRow("名称:", self.agent_name_label)
        agent_info_layout.addRow("角色:", self.agent_role_label)
        agent_info_layout.addRow("状态:", self.agent_status_label)
        content_layout.addWidget(agent_info_group)

        panel_layout.addWidget(content_widget)

        return panel

    def _create_tasks_panel(self) -> QWidget:
        """创建任务面板"""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        title_widget = self._create_title_widget("Task Management", "📋")
        panel_layout.addWidget(title_widget)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 8px;
            }
            QListWidget::item {
                padding: 10px 14px;
                border-radius: 6px;
                margin: 3px 0;
                background-color: #2d3d4a;
                border: none;
                font-size: 13px;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        self.task_list.itemClicked.connect(self._on_task_selected)
        content_layout.addWidget(self.task_list, 1)

        btn_layout = QHBoxLayout()

        self.btn_new_task = QPushButton("✨ 新建任务")
        self.btn_new_task.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.btn_new_task.clicked.connect(self._show_new_task_dialog)

        self.btn_split_task = QPushButton("📌 拆分任务")
        self.btn_split_task.setStyleSheet("""
            QPushButton {
                background-color: #3c7d3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4a9a4a;
            }
        """)
        self.btn_split_task.clicked.connect(self._split_selected_task)

        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.btn_refresh.clicked.connect(self._refresh_task_list)

        btn_layout.addWidget(self.btn_new_task)
        btn_layout.addWidget(self.btn_split_task)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        task_detail_group = QGroupBox("任务详情")
        task_detail_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        task_detail_layout = QVBoxLayout(task_detail_group)

        self.task_detail_text = QTextEdit()
        self.task_detail_text.setReadOnly(True)
        self.task_detail_text.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 12px;
                font-size: 13px;
                color: #d4d4d4;
                line-height: 1.6;
            }
        """)
        task_detail_layout.addWidget(self.task_detail_text)
        content_layout.addWidget(task_detail_group)

        panel_layout.addWidget(content_widget)

        return panel

    def _init_sample_agents(self):
        """初始化示例 Agent"""
        agents = [
            AgentInfo(
                agent_id="coordinator-1",
                name="Main Coordinator",
                role=AgentRole.COORDINATOR
            ),
            AgentInfo(
                agent_id="worker-1",
                name="Worker Agent",
                role=AgentRole.WORKER
            ),
            AgentInfo(
                agent_id="researcher-1",
                name="Research Agent",
                role=AgentRole.RESEARCHER
            ),
            AgentInfo(
                agent_id="writer-1",
                name="Writer Agent",
                role=AgentRole.WRITER
            ),
            AgentInfo(
                agent_id="reviewer-1",
                name="Reviewer Agent",
                role=AgentRole.REVIEWER
            )
        ]
        for agent in agents:
            self.registry.register(agent)
        self._refresh_agent_list()

    def _refresh_agent_list(self):
        """刷新 Agent 列表"""
        self.agent_list.clear()
        for agent in self.registry.get_all():
            status_icon = "🟢" if agent.status == "online" else "🔴"
            role_emoji = {
                "coordinator": "🎯",
                "worker": "⚙️",
                "researcher": "🔍",
                "writer": "✍️",
                "reviewer": "✅"
            }
            emoji = role_emoji.get(agent.role.value, "🤖")

            item_text = f"{status_icon} {emoji} {agent.name}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, agent.agent_id)

            font = QFont()
            font.setPointSize(13)
            item.setFont(font)

            self.agent_list.addItem(item)

    def _refresh_task_list(self):
        """刷新任务列表"""
        self.task_list.clear()
        for task in self.orchestrator.get_all_tasks():
            status_icons = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌"
            }
            icon = status_icons.get(task.status, "❓")
            prefix = "📌" if not task.parent_task_id else "   ↳"

            desc_preview = task.description[:45] + "..." if len(task.description) > 45 else task.description
            item_text = f"{prefix} {icon} {desc_preview}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task.task_id)

            font = QFont()
            font.setPointSize(12)
            item.setFont(font)

            self.task_list.addItem(item)

    def _add_sample_agent(self):
        """添加示例 Agent"""
        count = len(self.registry.get_all()) + 1
        worker = AgentInfo(
            agent_id=f"worker-{count}",
            name=f"Worker {count}",
            role=AgentRole.WORKER
        )
        self.registry.register(worker)
        self._refresh_agent_list()

        QMessageBox.information(
            self,
            "添加成功",
            f"已添加新 Agent: {worker.name}",
            QMessageBox.Ok
        )

    def _on_agent_selected(self, item):
        """Agent 被选中"""
        agent_id = item.data(Qt.UserRole)
        agent = self.registry.get_by_id(agent_id)
        if agent:
            self.agent_name_label.setText(agent.name)
            self.agent_role_label.setText(f"{agent.role.value} 🎯")

            status_text = "🟢 在线" if agent.status == "online" else "🔴 离线"
            self.agent_status_label.setText(status_text)

    def _on_task_selected(self, item):
        """任务被选中"""
        task_id = item.data(Qt.UserRole)
        task = self.orchestrator.get_task(task_id)
        if task:
            status_emoji = {
                "pending": "⏳ 等待中",
                "in_progress": "🔄 进行中",
                "completed": "✅ 已完成",
                "failed": "❌ 失败"
            }

            detail = f"""📋 任务详情

🔑 ID: {task.task_id}
📝 描述: {task.description}
📊 状态: {status_emoji.get(task.status.value, task.status.value)}"""

            if task.assigned_agent_id:
                assigned_agent = self.registry.get_by_id(task.assigned_agent_id)
                agent_name = assigned_agent.name if assigned_agent else task.assigned_agent_id
                detail += f"\n👤 分配给: {agent_name}"

            detail += f"\n⏰ 创建时间: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

            if task.subtask_ids:
                detail += f"\n📌 子任务数: {len(task.subtask_ids)}"

            if task.result:
                detail += f"\n\n📤 结果:\n{task.result}"

            if task.error:
                detail += f"\n\n⚠️ 错误:\n{task.error}"

            self.task_detail_text.setText(detail)

    def _show_new_task_dialog(self):
        """显示新建任务对话框"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("✨ 新建任务")
        dialog.setText("请输入任务描述:")
        dialog.setIcon(QMessageBox.Icon.Information)

        text_box = QTextEdit()
        text_box.setPlaceholderText("例如：帮我搜索并整理关于 AI Agent 的最新资讯...")
        text_box.setMinimumHeight(100)
        text_box.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 10px;
                color: #d4d4d4;
                font-size: 13px;
            }
        """)
        dialog.layout().addWidget(text_box)

        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        dialog.button(QMessageBox.StandardButton.Ok).setText("创建")
        dialog.button(QMessageBox.StandardButton.Cancel).setText("取消")

        if dialog.exec() == QMessageBox.StandardButton.Ok:
            description = text_box.toPlainText().strip()
            if description:
                task = self.orchestrator.create_task(description)

                agent = self.orchestrator.find_agent_for_task(task)
                if agent:
                    self.orchestrator.assign_task(task.task_id, agent.agent_id)
                    import time
                    time.sleep(0.5)
                    result = TaskResult(
                        task_id=task.task_id,
                        success=True,
                        output=f"任务已由 {agent.name} 完成"
                    )
                    self.orchestrator.update_task_result(result)

                self._refresh_task_list()

                QMessageBox.information(
                    self,
                    "任务创建成功",
                    f"任务已创建并自动分配给合适的 Agent",
                    QMessageBox.Ok
                )
            else:
                QMessageBox.warning(
                    self,
                    "输入为空",
                    "请输入任务描述",
                    QMessageBox.Ok
                )

    def _split_selected_task(self):
        """拆分选中的任务"""
        current_item = self.task_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "未选中任务",
                "请先在列表中选择一个任务",
                QMessageBox.Ok
            )
            return

        task_id = current_item.data(Qt.UserRole)
        task = self.orchestrator.get_task(task_id)
        if not task:
            return

        if task.subtask_ids:
            QMessageBox.warning(
                self,
                "任务已拆分",
                "此任务已经包含子任务，无法再次拆分",
                QMessageBox.Ok
            )
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle("📌 拆分任务")
        dialog.setText("请输入子任务描述（每行一个）:")

        text_box = QTextEdit()
        text_box.setPlaceholderText("例如：\n1. 搜索相关信息\n2. 整理资料\n3. 撰写报告")
        text_box.setMinimumHeight(150)
        text_box.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                padding: 10px;
                color: #d4d4d4;
                font-size: 13px;
            }
        """)
        dialog.layout().addWidget(text_box)

        dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        dialog.button(QMessageBox.StandardButton.Ok).setText("拆分")
        dialog.button(QMessageBox.StandardButton.Cancel).setText("取消")

        if dialog.exec() == QMessageBox.StandardButton.Ok:
            lines = text_box.toPlainText().strip().split("\n")
            subtask_descriptions = [line.strip() for line in lines if line.strip()]

            if subtask_descriptions:
                subtasks = self.orchestrator.split_task(task_id, subtask_descriptions)

                import time
                for subtask in subtasks:
                    agent = self.orchestrator.find_agent_for_task(subtask)
                    if agent:
                        self.orchestrator.assign_task(subtask.task_id, agent.agent_id)
                        time.sleep(0.3)
                        result = TaskResult(
                            task_id=subtask.task_id,
                            success=True,
                            output=f"子任务由 {agent.name} 完成"
                        )
                        self.orchestrator.update_task_result(result)

                self._refresh_task_list()

                QMessageBox.information(
                    self,
                    "任务拆分成功",
                    f"已将任务拆分为 {len(subtasks)} 个子任务，并自动分配给 Agent",
                    QMessageBox.Ok
                )
            else:
                QMessageBox.warning(
                    self,
                    "输入为空",
                    "请输入至少一个子任务",
                    QMessageBox.Ok
                )
