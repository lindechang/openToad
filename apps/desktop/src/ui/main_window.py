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


class MainWindow(QMainWindow):
    NAV_CHAT = 0
    NAV_SETTINGS = 1
    NAV_ABOUT = 2
    NAV_HELP = 3
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐸 OpenToad - AI Assistant")
        self.setMinimumSize(900, 650)
        
        self._apply_styles()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.settings = self._load_settings()
        
        self._create_sidebar(main_layout)
        self._create_content(main_layout)
        
        self._create_status_bar()
        
        self._init_agent()
        self._init_instance_service()
    
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
        """)
    
    def _create_sidebar(self, parent_layout):
        sidebar = QWidget()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("background-color: #252526;")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 10)
        sidebar_layout.setSpacing(5)
        
        title = QLabel("🐸 OpenToad")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        
        self.provider_label = QLabel("未连接")
        self.provider_label.setStyleSheet("color: #888; font-size: 11px; padding-bottom: 20px;")
        self.provider_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(self.provider_label)
        
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("QListWidget { background-color: transparent; border: none; }")
        
        nav_items = [
            ("💬", "对话"),
            ("⚙️", "设置"),
            ("ℹ️", "关于"),
            ("❓", "帮助"),
        ]
        
        for icon, text in nav_items:
            item = QListWidgetItem(f"{icon}  {text}")
            item.setSizeHint(QSize(0, 48))
            self.nav_list.addItem(item)
        
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        self.nav_list.setCurrentRow(0)
        sidebar_layout.addWidget(self.nav_list)
        
        sidebar_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ 清空对话")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_chat)
        sidebar_layout.addWidget(clear_btn)
        
        parent_layout.addWidget(sidebar)
    
    def _create_content(self, parent_layout):
        self.content_stack = QStackedWidget()
        
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
            "🐸 OpenToad v1.0.0\n\n"
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
        self.status_bar.showMessage("设置已保存", 3000)
    
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
        event.accept()
