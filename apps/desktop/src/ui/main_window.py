from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QStatusBar, QListWidget, QListWidgetItem, QStackedWidget, QScrollArea, 
    QMessageBox, QPushButton, QFrame, QLineEdit, QFormLayout)
from PySide6.QtCore import Qt, QTimer, QSize, Signal, QThread
from PySide6.QtGui import QIcon, QPalette, QColor, QFont
import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from ui.memory_sidebar import MemorySidebar, SessionSidebar
from agent_wrapper import AgentWrapper
from src.client import InstanceService, ClientConfig
from src.gateway import GatewayServer, GatewayConfig, AIHandler
from src.auth.service import AuthService
from src.crypto.cipher import CryptoManager


class AuthWorker(QThread):
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, auth_service, action, email=None, password=None, name=None):
        super().__init__()
        self.auth_service = auth_service
        self.action = action
        self.email = email
        self.password = password
        self.name = name
    
    def run(self):
        try:
            if self.action == 'login':
                result = self.auth_service.login(self.email, self.password)
                self.finished.emit(result)
            elif self.action == 'register':
                result = self.auth_service.register(self.email, self.password, self.name)
                self.finished.emit(result)
            elif self.action == 'logout':
                self.auth_service.logout()
                self.finished.emit(True)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    NAV_CHAT = 0
    NAV_LLM = 1
    NAV_SETTINGS = 2
    NAV_MEMORY = 3
    NAV_ACCOUNT = 4
    NAV_ABOUT = 5
    NAV_HELP = 6
    
    def _load_icons(self):
        self.icons = {}
        icons_dir = os.path.join(PROJECT_ROOT, 'icons')
        sizes = {'60': 60, '120': 120, '256': 256, '520': 520}
        for size, _ in sizes.items():
            icon_path = os.path.join(icons_dir, f'opentoad-logo-{size}.png')
            if os.path.exists(icon_path):
                self.icons[size] = icon_path
        
        self.app_icon = os.path.join(icons_dir, 'opentoad-logo-256.png')
    
    def _apply_window_icon(self):
        if os.path.exists(self.app_icon):
            self.setWindowIcon(QIcon(self.app_icon))
    
    def __init__(self, session=None):
        super().__init__()
        self.session = session
        self.setWindowTitle("OpenToad - AI Assistant")
        self.setMinimumSize(900, 650)
        
        self._load_icons()
        self._apply_window_icon()
        
        self._apply_styles()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.settings = self._load_settings()
        self._sidebar_collapsed = False
        self._sidebar_width_expanded = 180
        self._sidebar_width_collapsed = 65
        
        self._create_sidebar(main_layout)
        self._create_content(main_layout)
        
        self._create_status_bar()
        
        self._ensure_unbound_memory()
        self._init_memory_storage()
        self._init_agent()
        self._init_instance_service()
        self._init_gateway()
        self._update_auth_status()
    
    def _init_memory_storage(self):
        from src.memory import MemoryStorage
        
        self._memory_storage = MemoryStorage()
        
        if self.session and hasattr(self.session, 'memory_id') and self.session.memory_id:
            user_id = str(self.session.user_id) if self.session.user_id else None
            memory_id = self.session.memory_id
            
            if self.session.encryption_key:
                from src.crypto.cipher import CryptoManager
                crypto = CryptoManager(self.session.encryption_key)
                self._memory_storage = MemoryStorage(user_id=user_id, memory_id=memory_id, crypto=crypto)
            else:
                self._memory_storage = MemoryStorage(user_id=user_id, memory_id=memory_id)
    
    def _ensure_unbound_memory(self):
        from src.memory import MemoryStorage
        from pathlib import Path
        
        memories_dir = Path.home() / ".opentoad"
        unbound_exists = False
        
        shared_mem = memories_dir / "memory.db"
        if shared_mem.exists():
            try:
                storage = MemoryStorage(db_path=str(shared_mem))
                info = storage.get_memory_info()
                if not info.get("bound_user_id"):
                    unbound_exists = True
            except Exception:
                pass
        
        if not unbound_exists:
            MemoryStorage.create_unbound_memory("新记忆体")
            print("Created new unbound memory")
    
    def _update_auth_status(self):
        email = None
        logged_in = False
        if self.session:
            email = self.session.email
            logged_in = True
        else:
            auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
            if auth_service.is_logged_in:
                self.session = auth_service.session
                self._ensure_memory_id()
                email = self.session.email
                logged_in = True
        
        self.sidebar.set_account(email, logged_in)
    
    def _ensure_memory_id(self):
        if not self.session or not self.session.user_id:
            return
        
        from src.memory import MemoryStorage
        from src.crypto.cipher import CryptoManager
        from ui.memory_selector_dialog import MemorySelectorDialog
        
        memories = MemoryStorage.list_user_memories(str(self.session.user_id))
        
        existing_memory_ids = [m.get("memory_id") for m in memories if m.get("memory_id")]
        
        if not self.session.memory_id or self.session.memory_id not in existing_memory_ids:
            dialog = MemorySelectorDialog(self.session.user_id, self.session.encryption_key, self)
            dialog.memory_selected.connect(lambda action, memory_id: self._on_memory_selected(action, memory_id))
            dialog.exec()
            
            if not self.session.memory_id:
                return
        
        if hasattr(self, 'llm_config_page'):
            self.llm_config_page.set_session(self.session)
    
    def _init_instance_service(self):
        try:
            server_url = self.settings.get("server_url", "http://toadapi.cocofei.com")
            instance_id = self.settings.get("instance_id")
            
            config = ClientConfig()
            config.server_url = server_url
            if instance_id:
                config.instance_id = instance_id
            
            self.instance_service = InstanceService(config)
            self.instance_service.start()
            
            if not instance_id:
                self.settings["instance_id"] = self.instance_service.instance_id
                self._save_settings()
            
            print(f"Instance service started: {self.instance_service.instance_id}")
        except Exception as e:
            import traceback
            print(f"Failed to start instance service: {e}")
            traceback.print_exc()
    
    def _init_gateway(self):
        self.gateway_server = None
        self.gateway_ai_handler = None
        
        gateway_enabled = self.settings.get("gateway_enabled", False)
        if not gateway_enabled:
            return
        
        try:
            provider = self.settings.get("provider", "openai")
            api_key = self.settings.get("api_key", "")
            model = self.settings.get("model", "gpt-4o-mini")
            port = self.settings.get("gateway_port", 18989)
            stream = self.settings.get("gateway_stream", True)
            
            self.gateway_ai_handler = AIHandler(
                provider_type=provider,
                api_key=api_key,
                model=model,
                stream=stream
            )
            
            async def handle_message(instance_id: str, content: str):
                async for chunk in self.gateway_ai_handler.handle_message(instance_id, content):
                    yield chunk
            
            config = GatewayConfig(host="0.0.0.0", port=port)
            self.gateway_server = GatewayServer(config=config, on_message=handle_message)
            self.gateway_server.start(background=True)
            
            print(f"Gateway started on port {port}")
            self.status_bar.showMessage(f"Gateway 已启动: ws://0.0.0.0:{port}/ws", 5000)
        except Exception as e:
            import traceback
            print(f"Failed to start gateway: {e}")
            traceback.print_exc()
    
    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                color: #d4d4d4;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                min-height: 40px;
            }
            QLineEdit:focus {
                border: 2px solid #0e639c;
                background-color: #424242;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8f;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #4ec9b0;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 1px solid #0e639c;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
            }
            QCheckBox {
                spacing: 10px;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #0e639c;
                border: 2px solid #0e639c;
            }
            QToolBar {
                background-color: #252526;
                border: none;
                spacing: 8px;
                padding: 8px;
                border-radius: 8px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                padding: 10px;
                border-radius: 6px;
            }
            QToolBar QToolButton:hover {
                background-color: #3c3c3c;
            }
            QStatusBar {
                background-color: #252526;
                color: #888;
                border-top: 1px solid #3c3c3c;
                padding: 4px 12px;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 8px;
                margin: 4px 0;
                color: #d4d4d4;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #3c3c3c;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #555;
            }
            QScrollBar:horizontal {
                background: #1e1e1e;
                height: 8px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #3c3c3c;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #555;
            }
            QTabWidget {
                background-color: #1e1e1e;
                border: none;
            }
            QTabBar {
                background-color: #252526;
                border-bottom: 1px solid #3c3c3c;
            }
            QTabBar::tab {
                background-color: #252526;
                color: #888;
                padding: 10px 20px;
                margin-right: 2px;
                border-radius: 8px 8px 0 0;
            }
            QTabBar::tab:hover {
                background-color: #3c3c3c;
                color: #d4d4d4;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #4ec9b0;
                border-bottom: 2px solid #4ec9b0;
            }
        """)
    
    def _create_sidebar(self, parent_layout):
        self.sidebar = MemorySidebar()
        self.sidebar.new_chat_clicked.connect(self._on_new_chat)
        self.sidebar.settings_clicked.connect(self._show_settings)
        self.sidebar.account_clicked.connect(self._show_account)
        self.sidebar.about_clicked.connect(self._show_about)
        self.sidebar.llm_clicked.connect(self._show_llm)
        parent_layout.addWidget(self.sidebar)
        
        self.session_sidebar = SessionSidebar()
        self.session_sidebar.new_session_clicked.connect(self._on_new_chat)
        self.session_sidebar.session_selected.connect(self._on_session_selected)
        self.session_sidebar.session_deleted.connect(self._on_session_deleted)
        parent_layout.addWidget(self.session_sidebar)
    
    def _create_content(self, parent_layout):
        self.content_stack = QStackedWidget()
        parent_layout.addWidget(self.content_stack)
        
        self.chat_container = QWidget()
        chat_container_layout = QVBoxLayout(self.chat_container)
        chat_container_layout.setContentsMargins(0, 0, 0, 0)
        chat_container_layout.setSpacing(0)
        
        self._chat_stacked = QStackedWidget()
        chat_container_layout.addWidget(self._chat_stacked, 1)
        
        self._sessions = []
        self._create_new_chat_session()
        self.session_sidebar.add_session("会话 1")
        
        self.content_stack.addWidget(self.chat_container)
        
        from ui.llm_config_panel import LLMConfigPanel
        self.llm_config_page = LLMConfigPanel()
        self.llm_config_page.set_session(self.session)
        self.llm_config_page.config_changed.connect(self._on_llm_config_changed)
        self.llm_config_page.back_clicked.connect(self._go_to_chat)
        self.content_stack.addWidget(self.llm_config_page)
        
        self.settings_page = QWidget()
        settings_layout = QVBoxLayout(self.settings_page)
        settings_layout.setContentsMargins(30, 20, 30, 20)
        
        settings_header = QLabel("⚙️ 设置")
        settings_header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 20px;")
        settings_layout.addWidget(settings_header)
        
        settings_scroll = QScrollArea()
        settings_scroll.setWidgetResizable(True)
        settings_scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        settings_container = QWidget()
        settings_container_layout = QVBoxLayout(settings_container)
        
        self.settings_widget = SettingsDialog(self)
        self.settings_widget.load_settings(self.settings)
        settings_container_layout.addWidget(self.settings_widget)
        
        settings_scroll.setWidget(settings_container)
        settings_layout.addWidget(settings_scroll)
        
        save_btn = QPushButton("💾 保存设置")
        save_btn.clicked.connect(self._save_settings_from_ui)
        settings_layout.addWidget(save_btn)
        
        self.content_stack.addWidget(self.settings_page)
        
        self.memory_bind_page = self._create_memory_bind_page()
        self.content_stack.addWidget(self.memory_bind_page)
        
        self.account_page = self._create_account_page()
        self.content_stack.addWidget(self.account_page)
        
        self.about_page = self._create_about_page()
        self.content_stack.addWidget(self.about_page)
    
    def _create_new_chat_session(self):
        chat_panel = ChatPanel()
        index = self._chat_stacked.addWidget(chat_panel)
        
        self._sessions.append({
            'panel': chat_panel,
            'index': index
        })
        
        self._init_agent_for_session(chat_panel)
        
        return index
    
    def _init_agent_for_session(self, chat_panel):
        from src.memory import MemoryStorage
        
        if hasattr(self, '_memory_storage') and self._memory_storage:
            try:
                configs = self._memory_storage.get_llm_configs()
                if configs:
                    config = configs[0]
                    agent = AgentWrapper(
                        config["provider"],
                        config["api_key"],
                        config["model"],
                        session=self.session
                    )
                    chat_panel.set_agent(agent)
                    return
            except Exception as e:
                chat_panel.append_message("Error", f"初始化失败: {str(e)}")
                return
        
        chat_panel.append_message("OpenToad", """👋 欢迎使用 OpenToad！

要开始对话，请先完成以下设置：

1️⃣ 配置 LLM
   点击左侧菜单「🤖 LLM」添加 API Key

💡 提示：
   • LLM 配置存储在记忆体中
   • 登录账号后可加密保护您的数据
   • 支持多种大语言模型（DeepSeek、OpenAI、Claude 等）

点击「🤖 LLM」开始配置...""")
    
    def _on_chat_tab_selected(self, index):
        if 0 <= index < len(self._sessions):
            self._chat_stacked.setCurrentIndex(self._sessions[index]['index'])
    
    def _on_session_selected(self, index):
        if 0 <= index < len(self._sessions):
            self._chat_stacked.setCurrentIndex(self._sessions[index]['index'])
    
    def _on_session_deleted(self, row):
        if 0 <= row < len(self._sessions):
            panel = self._sessions[row]['panel']
            self._chat_stacked.removeWidget(panel)
            panel.deleteLater()
            self._sessions.pop(row)
            if self._sessions:
                new_index = min(row, len(self._sessions) - 1)
                self.session_sidebar.session_list.setCurrentRow(new_index)
                self._chat_stacked.setCurrentIndex(self._sessions[new_index]['index'])
    
    def _on_new_chat(self):
        index = self._create_new_chat_session()
        session_num = len(self._sessions)
        self.session_sidebar.add_session(f"会话 {session_num}")
        self._chat_stacked.setCurrentIndex(index)
    
    def _on_memory_selected_from_sidebar(self, memory_id):
        self.sidebar.set_memory_id(memory_id)
    
    def _on_sidebar_login_clicked(self):
        self._show_account()
    
    def _show_settings(self):
        if hasattr(self, 'settings_page'):
            self.content_stack.setCurrentWidget(self.settings_page)
    
    def _show_llm(self):
        self.content_stack.setCurrentWidget(self.llm_config_page)
    
    def _show_account(self):
        self.content_stack.setCurrentWidget(self.account_page)
        self._check_account_status()
    
    def _show_about(self):
        self.content_stack.setCurrentWidget(self.about_page)
    
    def _create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("ℹ️ 关于")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 20px;")
        layout.addWidget(header)
        
        text = QLabel(
            "OpenToad v1.0.0\n\n"
            "Self-Sustainable AI Assistant\n\n"
            "支持多模型:\n"
            "Claude, GPT, DeepSeek,\n"
            "通义千问, 文心一言, 混元,\n"
            "ChatGLM, Kimi, Gemini"
        )
        text.setStyleSheet("color: #d4d4d4; font-size: 14px; line-height: 1.8;")
        layout.addWidget(text)
        
        layout.addStretch()
        return page
    
    def _create_help_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("❓ 帮助")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 20px;")
        layout.addWidget(header)
        
        text = QLabel(
            "使用说明：\n\n"
            "1. 在「LLM」中配置您的 API Key\n"
            "2. 选择您偏好的 AI 模型\n"
            "3. 开始与 AI 助手对话\n\n"
            "快捷键：\n"
            "• Enter - 发送消息\n"
            "• Ctrl+L - 清空对话"
        )
        text.setStyleSheet("color: #d4d4d4; font-size: 14px; line-height: 1.8;")
        layout.addWidget(text)
        
        layout.addStretch()
        return page
    
    def _create_memory_bind_page(self):
        from ui.memory_bind_panel import MemoryBindPanel
        panel = MemoryBindPanel()
        panel.reset_complete.connect(self._on_memory_reset_complete)
        if self.session:
            panel.set_session(self.session)
        return panel
    
    def _on_memory_reset_complete(self):
        self.nav_list.setCurrentRow(self.NAV_CHAT)
        self.status_bar.showMessage("记忆体已重置，请在对话中为我命名", 5000)
    
    def _create_account_page(self):
        from PySide6.QtWidgets import QFrame, QFormLayout, QScrollArea
        
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("🔐 账号管理")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 10px;")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        self._create_account_status_widget(container_layout)
        self._create_inline_login_widget(container_layout)
        self._create_inline_register_widget(container_layout)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        return page
    
    def _create_account_status_widget(self, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border: 1px solid #4ec9b0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card_layout = QHBoxLayout(card)
        
        self.account_icon = QLabel("🔒")
        self.account_icon.setStyleSheet("font-size: 36px;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        
        self.account_status_label = QLabel("未登录")
        self.account_status_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        
        self.account_desc_label = QLabel("登录后可加密保护您的记忆数据")
        self.account_desc_label.setStyleSheet("font-size: 13px; color: #aaaaaa;")
        
        info_layout.addWidget(self.account_status_label)
        info_layout.addWidget(self.account_desc_label)
        
        self.account_logout_btn = QPushButton("登出")
        self.account_logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
        """)
        self.account_logout_btn.clicked.connect(self._do_account_logout)
        self.account_logout_btn.hide()
        
        card_layout.addWidget(self.account_icon)
        card_layout.addLayout(info_layout)
        card_layout.addStretch()
        card_layout.addWidget(self.account_logout_btn)
        
        parent_layout.addWidget(card)
        
        self._check_account_status()
    
    def _create_inline_login_widget(self, parent_layout):
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 15px;
            }
            QGroupBox {
                font-weight: bold;
                color: #4ec9b0;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        title = QLabel("登录已有账号")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.account_login_email = QLineEdit()
        self.account_login_email.setPlaceholderText("邮箱")
        
        self.account_login_password = QLineEdit()
        self.account_login_password.setPlaceholderText("密码")
        self.account_login_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("邮箱:", self.account_login_email)
        form_layout.addRow("密码:", self.account_login_password)
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.account_login_btn = QPushButton("登录")
        self.account_login_btn.clicked.connect(self._do_inline_login)
        btn_layout.addWidget(self.account_login_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.account_login_status = QLabel("")
        self.account_login_status.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.account_login_status)
        
        parent_layout.addWidget(group)
    
    def _create_inline_register_widget(self, parent_layout):
        group = QFrame()
        group.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        title = QLabel("注册新账号")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.account_reg_name = QLineEdit()
        self.account_reg_name.setPlaceholderText("昵称")
        
        self.account_reg_email = QLineEdit()
        self.account_reg_email.setPlaceholderText("邮箱")
        
        self.account_reg_password = QLineEdit()
        self.account_reg_password.setPlaceholderText("密码")
        self.account_reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.account_reg_password2 = QLineEdit()
        self.account_reg_password2.setPlaceholderText("确认密码")
        self.account_reg_password2.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("昵称:", self.account_reg_name)
        form_layout.addRow("邮箱:", self.account_reg_email)
        form_layout.addRow("密码:", self.account_reg_password)
        form_layout.addRow("确认:", self.account_reg_password2)
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.account_reg_btn = QPushButton("注册")
        self.account_reg_btn.clicked.connect(self._do_inline_register)
        btn_layout.addWidget(self.account_reg_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.account_reg_status = QLabel("")
        self.account_reg_status.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.account_reg_status)
        
        parent_layout.addWidget(group)
    
    def _check_account_status(self):
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        if auth_service.is_logged_in:
            session = auth_service.session
            self.account_icon.setText("🔓")
            self.account_status_label.setText(f"已登录: {session.email}")
            self.account_desc_label.setText("您的记忆数据已加密保护")
            self.account_logout_btn.show()
            self.session = session
            self.llm_config_page.set_session(session)
        else:
            self.account_icon.setText("🔒")
            self.account_status_label.setText("未登录")
            self.account_desc_label.setText("登录后可加密保护您的记忆数据")
            self.account_logout_btn.hide()
            self.session = None
            self.llm_config_page.set_session(None)
    
    def _do_inline_login(self):
        email = self.account_login_email.text().strip()
        password = self.account_login_password.text()
        
        if not email or not password:
            self.account_login_status.setText("请输入邮箱和密码")
            self.account_login_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.account_login_btn.setEnabled(False)
        self.account_login_btn.setText("登录中...")
        
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        self._auth_worker = AuthWorker(auth_service, 'login', email, password)
        self._auth_worker.finished.connect(self._on_inline_login_success)
        self._auth_worker.error.connect(self._on_inline_login_error)
        self._auth_worker.start()
    
    def _on_inline_login_success(self, session):
        self.account_login_btn.setEnabled(True)
        self.account_login_btn.setText("登录")
        self.account_login_status.setText(f"✓ 登录成功: {session.email}")
        self.account_login_status.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        
        from src.memory import MemoryStorage
        from src.crypto.cipher import CryptoManager
        from ui.memory_selector_dialog import MemorySelectorDialog
        
        self.session = session
        
        memories = MemoryStorage.list_user_memories(str(session.user_id))
        
        if not session.memory_id or not any(m.get("memory_id") == session.memory_id for m in memories):
            dialog = MemorySelectorDialog(session.user_id, session.encryption_key, self)
            dialog.memory_selected.connect(lambda action, memory_id: self._on_memory_selected(action, memory_id))
            dialog.exec()
            
            if not session.memory_id:
                self.account_login_status.setText("请选择记忆体")
                self.account_login_status.setStyleSheet("color: #f1c40f; font-size: 12px;")
                return
        else:
            self._apply_session()
        
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        auth_service.update_memory_id(session.memory_id)
        
        self.account_login_email.clear()
        self.account_login_password.clear()
    
    def _on_memory_selected(self, action, memory_id):
        from src.memory import MemoryStorage
        from src.crypto.cipher import CryptoManager
        from src.auth.service import AuthService
        
        if action == "create_unbound":
            self.session.memory_id = memory_id
            self.session = None
            
            new_session = MemoryStorage.create_unbound_memory()
            auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
            auth_service.logout()
            
            self.llm_config_page.set_session(None)
            
            if hasattr(self, 'chat_panel') and hasattr(self, 'chat_panel', 'agent') and self.chat_panel.agent:
                self.chat_panel.agent.update_session(None)
            
            self._check_account_status()
            self._update_auth_status()
            
            QMessageBox.information(self, "提示", "已创建新的未绑定记忆体。")
            return
        
        self.session.memory_id = memory_id
        
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        auth_service.update_memory_id(memory_id)
        
        self._apply_session()
    
    def _apply_session(self):
        from src.memory import MemoryStorage
        from src.crypto.cipher import CryptoManager
        
        if self.session and self.session.memory_id:
            user_id = str(self.session.user_id) if self.session.user_id else None
            memory_id = self.session.memory_id
            
            if self.session.encryption_key:
                crypto = CryptoManager(self.session.encryption_key)
                self._memory_storage = MemoryStorage(user_id=user_id, memory_id=memory_id, crypto=crypto)
            else:
                self._memory_storage = MemoryStorage(user_id=user_id, memory_id=memory_id)
        else:
            self._memory_storage = MemoryStorage()
        
        self.llm_config_page.set_session(self.session)
        
        if hasattr(self, 'chat_panel') and hasattr(self.chat_panel, 'agent') and self.chat_panel.agent:
            self.chat_panel.agent.update_session(self.session)
        
        if hasattr(self, 'memory_bind_page'):
            self.memory_bind_page.set_session(self.session)
        
        self._check_account_status()
        self._update_auth_status()
    
    def _on_inline_login_error(self, error_msg):
        self.account_login_btn.setEnabled(True)
        self.account_login_btn.setText("登录")
        self.account_login_status.setText(f"✗ 登录失败: {error_msg}")
        self.account_login_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _do_inline_register(self):
        name = self.account_reg_name.text().strip()
        email = self.account_reg_email.text().strip()
        password = self.account_reg_password.text()
        password2 = self.account_reg_password2.text()
        
        if not name or not email or not password:
            self.account_reg_status.setText("请填写所有字段")
            self.account_reg_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        if password != password2:
            self.account_reg_status.setText("两次密码不一致")
            self.account_reg_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.account_reg_btn.setEnabled(False)
        self.account_reg_btn.setText("注册中...")
        
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        self._auth_worker = AuthWorker(auth_service, 'register', email, password, name)
        self._auth_worker.finished.connect(self._on_inline_register_success)
        self._auth_worker.error.connect(self._on_inline_register_error)
        self._auth_worker.start()
    
    def _on_inline_register_success(self, result):
        self.account_reg_btn.setEnabled(True)
        self.account_reg_btn.setText("注册")
        self.account_reg_status.setText("✓ 注册成功！请登录")
        self.account_reg_status.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        
        self.account_login_email.setText(self.account_reg_email.text())
        self.account_reg_name.clear()
        self.account_reg_email.clear()
        self.account_reg_password.clear()
        self.account_reg_password2.clear()
    
    def _on_inline_register_error(self, error_msg):
        self.account_reg_btn.setEnabled(True)
        self.account_reg_btn.setText("注册")
        self.account_reg_status.setText(f"✗ 注册失败: {error_msg}")
        self.account_reg_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _do_account_logout(self):
        from src.memory import MemoryStorage
        
        auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        auth_service.logout()
        
        MemoryStorage.create_unbound_memory("新记忆体")
        
        self.session = None
        self.llm_config_page.set_session(None)
        
        if hasattr(self, 'chat_panel') and hasattr(self, 'chat_panel', 'agent') and self.chat_panel.agent:
            self.chat_panel.agent.update_session(None)
        
        self._check_account_status()
        self._update_auth_status()
        self.account_login_status.setText("")
        self.account_reg_status.setText("")
    
    def _on_nav_changed(self, index):
        if not hasattr(self, 'content_stack'):
            return
        self.content_stack.setCurrentIndex(index)
        
        if index == self.NAV_LLM:
            self.status_bar.showMessage("LLM 配置")
        elif index == self.NAV_SETTINGS:
            self.status_bar.showMessage("设置")
        elif index == self.NAV_MEMORY:
            self.status_bar.showMessage("记忆体")
            if hasattr(self, 'memory_bind_page'):
                self.memory_bind_page.set_session(self.session)
        elif index == self.NAV_ACCOUNT:
            self.status_bar.showMessage("账号")
            self._check_account_status()
        elif index == self.NAV_ABOUT:
            self.status_bar.showMessage("关于")
        elif index == self.NAV_HELP:
            self.status_bar.showMessage("帮助")
        else:
            self.status_bar.showMessage("对话")
    
    def _show_page(self, page):
        if page == 'llm':
            self.content_stack.setCurrentWidget(self.llm_config_page)
        elif page == 'settings':
            if hasattr(self, 'settings_page'):
                self.content_stack.setCurrentWidget(self.settings_page)
    
    def _go_to_chat(self):
        self.content_stack.setCurrentWidget(self.chat_container)
    
    def _on_llm_config_changed(self, llm_settings):
        self.settings.update(llm_settings)
        self._save_settings()
        
        for session in self._sessions:
            self._init_agent_for_session(session['panel'])
        
        current_chat = self._chat_stacked.currentWidget()
        if current_chat:
            configs = self._memory_storage.get_llm_configs() if hasattr(self, '_memory_storage') else []
            if configs:
                self.provider_label.setText(f"✓ {configs[0]['provider']}")
        
        self.status_bar.showMessage("LLM 配置已更新", 3000)
    
    def _create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _save_settings_from_ui(self):
        new_settings = self.settings_widget.get_settings()
        self.settings = new_settings
        self._save_settings()
        self._save_profile(new_settings.get("profile", {}))
        self._init_agent()
        self._restart_gateway()
        self.status_bar.showMessage("设置已保存", 3000)
    
    def _restart_gateway(self):
        if hasattr(self, 'gateway_server') and self.gateway_server:
            try:
                self.gateway_server.stop()
                print("Gateway stopped for restart")
            except Exception as e:
                print(f"Error stopping gateway: {e}")
            self.gateway_server = None
            self.gateway_ai_handler = None
        
        gateway_enabled = self.settings.get("gateway_enabled", False)
        if gateway_enabled:
            self._init_gateway()
    
    def _toggle_sidebar(self):
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        self._sidebar_collapsed = not self._sidebar_collapsed
        
        if self._sidebar_collapsed:
            target_width = self._sidebar_width_collapsed
            collapsed = True
        else:
            target_width = self._sidebar_width_expanded
            collapsed = False
        
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.sidebar.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.valueChanged.connect(lambda v: self.sidebar.setFixedWidth(v))
        self.animation.finished.connect(lambda: self._set_sidebar_collapsed(collapsed))
        self.animation.start()
    
    def _set_sidebar_collapsed(self, collapsed: bool):
        if collapsed:
            self.sidebar_title.hide()
            self.provider_label.hide()
            self.auth_label.hide()
            self.clear_btn.hide()
        else:
            self.sidebar_title.show()
            self.provider_label.show()
            self.auth_label.show()
            self.clear_btn.show()
        
        for i, (icon, text) in enumerate(self.nav_items_data):
            item = self.nav_list.item(i)
            if item:
                if collapsed:
                    item.setText(icon)
                    item.setSizeHint(QSize(50, 44))
                else:
                    item.setText(f"{icon}  {text}")
                    item.setSizeHint(QSize(160, 44))
    
    def _clear_chat(self):
        current_chat = self._chat_stacked.currentWidget()
        if current_chat:
            current_chat.clear()
        self.status_bar.showMessage("对话已清空", 2000)
    
    def _init_agent(self):
        for session in self._sessions:
            self._init_agent_for_session(session['panel'])
    
    def _first_greeting(self, agent=None):
        if agent is None:
            return
        try:
            greeting = agent.greet()
            self.chat_panel.append_message("OpenToad", greeting)
        except Exception as e:
            import traceback
            print(f"Greeting error: {e}")
            traceback.print_exc()
    
    def _load_settings(self):
        settings_path = os.path.join(os.getcwd(), "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "server_url": "http://api.opentoad.cn"
        }
    
    def _save_settings(self):
        settings_file = os.path.join(os.getcwd(), "settings.json")
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _save_profile(self, profile_data):
        if not profile_data:
            return
        try:
            from src.profile import save_profile, UserProfile
            profile = UserProfile(
                name=profile_data.get("name", ""),
                nickname=profile_data.get("nickname", ""),
                age_range=profile_data.get("age_range", ""),
                occupation=profile_data.get("occupation", ""),
                personality=profile_data.get("personality", ""),
                interests=profile_data.get("interests", []),
                price_sensitivity=profile_data.get("price_sensitivity", "mid-range"),
                decision_factors=profile_data.get("decision_factors", [])
            )
            save_profile(profile)
        except Exception as e:
            print(f"Error saving profile: {e}")
    
    def closeEvent(self, event):
        if hasattr(self, 'instance_service'):
            try:
                self.instance_service.stop()
                print("Instance service stopped")
            except Exception as e:
                print(f"Error stopping instance service: {e}")
        
        if hasattr(self, 'gateway_server') and self.gateway_server:
            try:
                self.gateway_server.stop()
                print("Gateway stopped")
            except Exception as e:
                print(f"Error stopping gateway: {e}")
        
        event.accept()
