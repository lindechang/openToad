from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from ui.chat_panel import ChatPanel
from ui.settings_dialog import SettingsDialog
from agent_wrapper import AgentWrapper
import json
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenToad")
        self.setMinimumSize(800, 600)
        
        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # 对话面板
        self.chat_panel = ChatPanel()
        layout.addWidget(self.chat_panel)
        
        # 工具栏
        self._create_toolbar()
        
        # 加载设置
        self.settings = self._load_settings()
        self._init_agent()
    
    def _create_toolbar(self):
        toolbar = self.addToolBar("Main")
        toolbar.addAction("Settings", self._show_settings)
    
    def _show_settings(self):
        dialog = SettingsDialog(self)
        # 加载当前设置
        print(f"Current settings before dialog: {self.settings}")
        dialog.provider_combo.setCurrentText(self.settings.get("provider", "anthropic"))
        dialog.api_key_input.setText(self.settings.get("api_key", ""))
        dialog.model_input.setText(self.settings.get("model", "claude-3-5-sonnet-20241022"))
        
        if dialog.exec():
            # 保存新设置
            new_settings = dialog.get_settings()
            print(f"New settings from dialog: {new_settings}")
            self.settings = new_settings
            self._save_settings()
            self._init_agent()
    
    def _init_agent(self):
        if self.settings.get("api_key"):
            try:
                agent = AgentWrapper(
                    self.settings["provider"],
                    self.settings["api_key"],
                    self.settings["model"]
                )
                self.chat_panel.set_agent(agent)
                self.chat_panel.append_message("System", f"已连接到 {self.settings['provider']} 服务")
            except Exception as e:
                self.chat_panel.append_message("Error", f"初始化 agent 失败: {str(e)}")
    
    def _load_settings(self):
        settings_path = os.path.expanduser("~/.opentoad/settings.json")
        print(f"Loading settings from: {settings_path}")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    print(f"Loaded settings: {settings}")
                    return settings
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
                pass
        print("No settings file found, using defaults")
        return {
            "provider": "anthropic",
            "api_key": "",
            "model": "claude-3-5-sonnet-20241022"
        }
    
    def _save_settings(self):
        settings_path = os.path.expanduser("~/.opentoad")
        os.makedirs(settings_path, exist_ok=True)
        settings_file = os.path.join(settings_path, "settings.json")
        print(f"Saving settings to: {settings_file}")
        print(f"Settings to save: {self.settings}")
        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
