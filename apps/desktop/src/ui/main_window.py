from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStatusBar, QToolBar, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPalette, QColor
from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from agent_wrapper import AgentWrapper
import json
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐸 OpenToad - AI Assistant")
        self.setMinimumSize(900, 650)
        
        self._apply_styles()
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._create_header(main_layout)
        
        self.chat_panel = ChatPanel()
        main_layout.addWidget(self.chat_panel)
        
        self._create_toolbar()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        self.settings = self._load_settings()
        self._init_agent()
    
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
        """)
    
    def _create_header(self, parent_layout):
        header = QWidget()
        header.setStyleSheet("background-color: #2d2d2d; padding: 10px;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title = QLabel("🐸 OpenToad")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ec9b0;")
        
        self.provider_label = QLabel("未连接")
        self.provider_label.setStyleSheet("color: #888; font-size: 12px;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.provider_label)
        
        parent_layout.addWidget(header)
    
    def _create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        settings_action = QAction("⚙️ 设置", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
        
        clear_action = QAction("🗑️ 清空", self)
        clear_action.triggered.connect(self._clear_chat)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        about_action = QAction("ℹ️ 关于", self)
        about_action.triggered.connect(self._show_about)
        toolbar.addAction(about_action)
    
    def _show_settings(self):
        dialog = SettingsDialog(self)
        dialog.load_settings(self.settings)
        
        if dialog.exec():
            new_settings = dialog.get_settings()
            self.settings = new_settings
            self._save_settings()
            self._save_profile(new_settings.get("profile", {}))
            self._init_agent()
            self.status_bar.showMessage("设置已保存", 3000)
    
    def _clear_chat(self):
        self.chat_panel.clear()
        self.status_bar.showMessage("对话已清空", 2000)
    
    def _show_about(self):
        QMessageBox.about(self, "关于 OpenToad",
            "🐸 OpenToad v1.0.0\n\n"
            "Self-Sustainable AI Assistant\n\n"
            "支持多模型: Claude, GPT, DeepSeek,\n"
            "通义千问, 文心一言, 混元, ChatGLM, Kimi, Gemini"
        )
    
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
