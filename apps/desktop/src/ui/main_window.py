from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QStatusBar, QListWidget, QListWidgetItem, QStackedWidget, QScrollArea, 
    QMessageBox, QPushButton)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QPalette, QColor, QFont
from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from agent_wrapper import AgentWrapper
import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.client import InstanceService, ClientConfig
from src.gateway import GatewayServer, GatewayConfig, AIHandler


class MainWindow(QMainWindow):
    NAV_CHAT = 0
    NAV_SETTINGS = 1
    NAV_ABOUT = 2
    NAV_HELP = 3
    
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
    
    def __init__(self):
        super().__init__()
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
        
        self._init_agent()
        self._init_instance_service()
        self._init_gateway()
    
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
                background-color: #252526;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
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
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QToolBar {
                background-color: #2d2d2d;
                border: none;
                spacing: 5px;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QToolBar QToolButton:hover {
                background-color: #3c3c3c;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QListWidget {
                background-color: #252526;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px 15px;
                border-radius: 8px;
                margin: 4px 0;
                color: #d4d4d4;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 0px;
            }
            QScrollBar:horizontal {
                background: transparent;
                height: 0px;
            }
        """)
    
    def _create_sidebar(self, parent_layout):
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property
        
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(self._sidebar_width_expanded)
        self.sidebar.setStyleSheet("background-color: #252526;")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 10, 5, 10)
        sidebar_layout.setSpacing(5)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 20px;
                color: #d4d4d4;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
                border-radius: 8px;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
        
        self.sidebar_title = QLabel("OpenToad")
        self.sidebar_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #4ec9b0;")
        self.sidebar_title.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.toggle_btn)
        header_layout.addWidget(self.sidebar_title)
        sidebar_layout.addWidget(header_widget)
        
        self.provider_label = QLabel("未连接")
        self.provider_label.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        self.provider_label.setAlignment(Qt.AlignCenter)
        self.provider_label.setWordWrap(True)
        sidebar_layout.addWidget(self.provider_label)
        
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 12px 10px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #3c3c3c;
            }
        """)
        
        self.nav_items_data = [
            ("💬", "对话"),
            ("⚙️", "设置"),
            ("ℹ️", "关于"),
            ("❓", "帮助"),
        ]
        
        for icon, text in self.nav_items_data:
            item = QListWidgetItem(f"{icon}  {text}")
            item.setSizeHint(QSize(0, 44))
            self.nav_list.addItem(item)
        
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        self.nav_list.setCurrentRow(0)
        sidebar_layout.addWidget(self.nav_list)
        
        sidebar_layout.addStretch()
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self._clear_chat)
        sidebar_layout.addWidget(self.clear_btn)
        
        parent_layout.addWidget(self.sidebar)
    
    def _create_content(self, parent_layout):
        self.content_stack = QStackedWidget()
        parent_layout.addWidget(self.content_stack)
        
        self.chat_panel = ChatPanel()
        self.content_stack.addWidget(self.chat_panel)
        
        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
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
        
        self.content_stack.addWidget(settings_page)
        
        about_page = QWidget()
        about_layout = QVBoxLayout(about_page)
        about_layout.setContentsMargins(30, 20, 30, 20)
        
        about_header = QLabel("ℹ️ 关于")
        about_header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 20px;")
        about_layout.addWidget(about_header)
        
        about_text = QLabel(
            "OpenToad v1.0.0\n\n"
            "Self-Sustainable AI Assistant\n\n"
            "支持多模型:\n"
            "Claude, GPT, DeepSeek,\n"
            "通义千问, 文心一言, 混元,\n"
            "ChatGLM, Kimi, Gemini"
        )
        about_text.setStyleSheet("color: #d4d4d4; font-size: 14px; line-height: 1.8;")
        about_layout.addWidget(about_text)
        
        about_layout.addStretch()
        self.content_stack.addWidget(about_page)
        
        help_page = QWidget()
        help_layout = QVBoxLayout(help_page)
        help_layout.setContentsMargins(30, 20, 30, 20)
        
        help_header = QLabel("❓ 帮助")
        help_header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 20px;")
        help_layout.addWidget(help_header)
        
        help_text = QLabel(
            "使用说明：\n\n"
            "1. 在「设置」中配置您的 API Key\n"
            "2. 选择您偏好的 AI 模型\n"
            "3. 开始与 AI 助手对话\n\n"
            "快捷键：\n"
            "• Enter - 发送消息\n"
            "• Ctrl+L - 清空对话"
        )
        help_text.setStyleSheet("color: #d4d4d4; font-size: 14px; line-height: 1.8;")
        help_layout.addWidget(help_text)
        
        help_layout.addStretch()
        self.content_stack.addWidget(help_page)
        
        parent_layout.addWidget(self.content_stack)
    
    def _on_nav_changed(self, index):
        if not hasattr(self, 'content_stack'):
            return
        self.content_stack.setCurrentIndex(index)
        
        if index == self.NAV_SETTINGS:
            self.status_bar.showMessage("设置")
        elif index == self.NAV_ABOUT:
            self.status_bar.showMessage("关于")
        elif index == self.NAV_HELP:
            self.status_bar.showMessage("帮助")
        else:
            self.status_bar.showMessage("对话")
    
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
            self.clear_btn.hide()
        else:
            self.sidebar_title.show()
            self.provider_label.show()
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
        self.chat_panel.clear()
        self.status_bar.showMessage("对话已清空", 2000)
    
    def _init_agent(self):
        if self.settings.get("api_key"):
            try:
                agent = AgentWrapper(
                    self.settings["provider"],
                    self.settings["api_key"],
                    self.settings["model"]
                )
                self.chat_panel.set_agent(agent)
                provider_name = self.settings["provider"]
                self.provider_label.setText(f"✓ {provider_name}")
                self.status_bar.showMessage(f"已连接到 {provider_name}", 3000)
                
                QTimer.singleShot(500, lambda: self._first_greeting(agent))
            except Exception as e:
                self.chat_panel.append_message("Error", f"初始化失败: {str(e)}")
                self.provider_label.setText("✗ 连接失败")
                self.status_bar.showMessage(f"连接失败: {str(e)}", 5000)
    
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
            "provider": "anthropic",
            "api_key": "",
            "model": "claude-3-5-sonnet-20241022"
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
