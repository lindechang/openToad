from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QLineEdit, QFormLayout, QScrollArea, QComboBox, QGroupBox, QCheckBox,
    QSpinBox)
from PySide6.QtCore import Qt, QThread, Signal
import os
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager
except ImportError:
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager

PROVIDERS = [
    ("anthropic", "Claude (Anthropic)"),
    ("openai", "OpenAI GPT"),
    ("deepseek", "DeepSeek"),
    ("qianwen", "阿里通义千问 (Qianwen)"),
    ("ernie", "百度文心一言 (ERNIE)"),
    ("hunyuan", "腾讯混元 (Hunyuan)"),
    ("zhipu", "智谱ChatGLM (Zhipu)"),
    ("kimi", "月之暗面 (Kimi)"),
    ("gemini", "Google Gemini"),
    ("ollama", "Ollama (本地)"),
]

PROVIDER_MODELS = {
    "anthropic": [
        ("claude-sonnet-4-20260220", "Claude Sonnet 4.6 (最新)"),
        ("claude-opus-4-20260220", "Claude Opus 4.6 (最强)"),
        ("claude-3-7-sonnet-20250219", "Claude 3.7 Sonnet"),
        ("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku"),
    ],
    "openai": [
        ("gpt-5.4", "GPT-5.4 (最新)"),
        ("gpt-5.4-pro", "GPT-5.4 Pro (最强)"),
        ("gpt-5.4-mini", "GPT-5.4 Mini"),
        ("gpt-5.3", "GPT-5.3"),
        ("gpt-5", "GPT-5"),
        ("gpt-4o", "GPT-4o"),
        ("gpt-4-turbo", "GPT-4 Turbo"),
        ("gpt-4", "GPT-4"),
        ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
    ],
    "deepseek": [
        ("deepseek-chat", "DeepSeek V3.2 (最新)"),
        ("deepseek-reasoner", "DeepSeek R2 (推理)"),
        ("deepseek-coder", "DeepSeek Coder V3"),
    ],
    "qianwen": [
        ("qwen3.5-plus", "Qwen 3.5 Plus (最新)"),
        ("qwen3-max", "Qwen 3 Max (最强)"),
        ("qwen-plus", "Qwen Plus"),
        ("qwen-turbo", "Qwen Turbo"),
        ("qwen3-omni", "Qwen 3 Omni (多模态)"),
    ],
    "ernie": [
        ("ernie-5.0", "文心一言 5.0 (最新)"),
        ("ernie-4.5-300B-A47B", "ERNIE 4.5 300B"),
        ("ernie-4.5-VL-424B-A47B", "ERNIE 4.5 VL (多模态)"),
        ("ernie-bot-turbo", "ERNIE Turbo"),
    ],
    "hunyuan": [
        ("hunyuan-t1-20250711", "混元 T1 (最新)"),
        ("hunyuan", "混元标准版"),
        ("hunyuan-pro", "混元 Pro"),
    ],
    "zhipu": [
        ("glm-5", "GLM-5 (最新)"),
        ("glm-4.7", "GLM-4.7"),
        ("glm-4.7-flash", "GLM-4.7 Flash (快速)"),
        ("glm-4.6", "GLM-4.6"),
        ("glm-4-flash", "GLM-4 Flash"),
    ],
    "kimi": [
        ("kimi-k2.5", "Kimi K2.5 (最新多模态)"),
        ("kimi-k2-turbo-preview", "Kimi K2 Turbo (快速)"),
        ("kimi-k2-thinking", "Kimi K2 Thinking (推理)"),
        ("moonshot-v1-128k", "Moonshot V1 128K"),
        ("moonshot-v1-32k", "Moonshot V1 32K"),
    ],
    "gemini": [
        ("gemini-3.1-pro", "Gemini 3.1 Pro (最新)"),
        ("gemini-2.0-flash", "Gemini 2.0 Flash (1M上下文)"),
        ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
    ],
    "ollama": [
        ("llama3.3", "Llama 3.3 (最新)"),
        ("llama3.1", "Llama 3.1"),
        ("qwen2.5", "Qwen 2.5"),
        ("mistral", "Mistral"),
        ("codellama", "Code Llama"),
    ],
}

PROVIDER_DISPLAY_NAMES = {k: v for k, v in PROVIDERS}


class LLMConfigWorker(QThread):
    finished = Signal(bool, str)
    
    def __init__(self, provider, api_key, model):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.model = model
    
    def run(self):
        try:
            from src.providers import create_provider, ChatOptions, Message
            llm = create_provider(self.provider, self.api_key)
            options = ChatOptions(
                model=self.model,
                messages=[Message(role="user", content="Hello")]
            )
            response = llm.chat(options)
            self.finished.emit(True, "")
        except Exception as e:
            self.finished.emit(False, str(e))


class LLMConfigPanel(QWidget):
    back_clicked = Signal()
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._configs = []
        self._current_index = -1
        self._memory_storage = None
        self._session = None
        self._default_config_id = None
        self.setup_ui()
    
    def set_session(self, session):
        self._session = session
        self._update_memory_storage()
    
    def _update_memory_storage(self):
        try:
            from src.memory import MemoryStorage
            user_id = None
            memory_id = None
            
            if self._session and hasattr(self._session, 'user_id') and self._session.user_id:
                user_id = str(self._session.user_id)
                memory_id = getattr(self._session, 'memory_id', None)
            
            if self._session and hasattr(self._session, 'encryption_key') and self._session.encryption_key:
                crypto = CryptoManager(self._session.encryption_key)
                self._memory_storage = MemoryStorage(crypto=crypto, user_id=user_id, memory_id=memory_id)
            else:
                self._memory_storage = MemoryStorage(user_id=user_id, memory_id=memory_id)
            
            if self.window() and hasattr(self.window(), '_memory_storage'):
                self.window()._memory_storage = self._memory_storage
            
            self._load_from_memory()
        except Exception as e:
            print(f"Error updating memory storage: {e}")
            self._memory_storage = None
            self._configs = []
            self.llm_list.clear()
            self._load_configs_empty()
    
    def _load_from_memory(self):
        if self._memory_storage:
            try:
                configs = self._memory_storage.get_llm_configs()
                self._configs = configs
                self.llm_list.clear()
                for config in self._configs:
                    provider = PROVIDER_DISPLAY_NAMES.get(config.get("provider", ""), config.get("provider", ""))
                    self.llm_list.addItem(provider)
                
                import json
                from pathlib import Path
                meta_path = Path.home() / ".opentoad" / "memory.meta"
                self._default_config_id = None
                if meta_path.exists():
                    try:
                        with open(meta_path, 'r') as f:
                            meta = json.load(f)
                        self._default_config_id = meta.get('default_llm_config')
                    except Exception:
                        pass
                
                if not self._default_config_id and self._configs:
                    self._default_config_id = self._configs[0].get("id", self._configs[0].get("provider"))
                    self._save_default_to_memory()
                
                self._update_list_display()
                
                if self._default_config_id:
                    for i, c in enumerate(self._configs):
                        if c.get("id", c.get("provider")) == self._default_config_id:
                            self.llm_list.setCurrentRow(i)
                            break
                elif self._configs:
                    self.llm_list.setCurrentRow(0)
            except Exception as e:
                print(f"Error loading LLM configs from memory: {e}")
    
    def _load_configs_empty(self):
        self._configs = []
        self.llm_list.clear()
        self._default_config_id = None
    
    def _update_list_display(self):
        for i in range(self.llm_list.count()):
            config = self._configs[i] if i < len(self._configs) else None
            if config:
                provider = PROVIDER_DISPLAY_NAMES.get(config.get("provider", ""), config.get("provider", ""))
                config_id = config.get("id", config.get("provider"))
                if config_id == self._default_config_id:
                    self.llm_list.item(i).setText(f"⭐ {provider}")
                else:
                    self.llm_list.item(i).setText(provider)
    
    def load_configs(self, settings):
        if self._memory_storage:
            self._load_from_memory()
        else:
            self._configs = settings.get("llm_configs", [])
            self.llm_list.clear()
            for config in self._configs:
                provider = PROVIDER_DISPLAY_NAMES.get(config.get("provider", ""), config.get("provider", ""))
                self.llm_list.addItem(provider)
            
            current_config = settings.get("current_llm_config")
            if current_config:
                for i, c in enumerate(self._configs):
                    if c.get("provider") == current_config.get("provider"):
                        self.llm_list.setCurrentRow(i)
                        break
            elif self._configs:
                self.llm_list.setCurrentRow(0)
    
    def get_current_config(self):
        if 0 <= self._current_index < len(self._configs):
            return self._configs[self._current_index]
        return None
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("🤖 LLM 配置管理")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 10px;")
        layout.addWidget(header)
        
        back_btn = QPushButton("← 返回对话")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #d4d4d4;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        back_btn.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        content_layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        list_label = QLabel("已保存的配置:")
        list_label.setStyleSheet("color: #888; font-size: 12px;")
        left_panel.addWidget(list_label)
        
        self.llm_list = QListWidget()
        self.llm_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                color: #d4d4d4;
                min-width: 180px;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
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
        self.llm_list.itemSelectionChanged.connect(self._on_config_selected)
        left_panel.addWidget(self.llm_list)
        
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("➕ 新建")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d5a2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3d7a3d;
            }
        """)
        self.add_btn.clicked.connect(self._add_config)
        
        self.delete_btn = QPushButton("🗑️ 删除")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_config)
        
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addStretch()
        left_panel.addLayout(btn_row)
        
        self.default_btn = QPushButton("⭐ 设为默认")
        self.default_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a00;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #6a6a00;
            }
        """)
        self.default_btn.clicked.connect(self._set_default)
        left_panel.addWidget(self.default_btn)
        
        left_panel.addStretch()
        content_layout.addLayout(left_panel)
        
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        form_label = QLabel("配置详情")
        form_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        right_panel.addWidget(form_label)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.provider_combo = QComboBox()
        for key, name in PROVIDERS:
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("API Key")
        
        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedWidth(35)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                padding: 6px;
                font-size: 14px;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_key)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.toggle_btn)
        
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        
        form_layout.addRow("服务商:", self.provider_combo)
        form_layout.addRow("API Key:", api_key_layout)
        form_layout.addRow("模型:", self.model_combo)
        
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.save_btn.clicked.connect(self._save_config)
        
        self.test_btn = QPushButton("🔗 测试")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d5a2d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d7a3d;
            }
        """)
        self.test_btn.clicked.connect(self._test_connection)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.test_btn)
        btn_layout.addStretch()
        
        form_layout.addRow("", btn_layout)
        
        self.status_label = QLabel("选择或创建一个配置")
        self.status_label.setStyleSheet("color: #888; font-size: 12px; padding-top: 10px;")
        form_layout.addRow("", self.status_label)
        
        right_panel.addWidget(form_frame)
        right_panel.addStretch()
        
        content_layout.addLayout(right_panel, 1)
        container_layout.addLayout(content_layout)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        self._populate_model_combo(self.provider_combo.currentData())
    
    def _on_config_selected(self):
        row = self.llm_list.currentRow()
        self._current_index = row
        
        if 0 <= row < len(self._configs):
            config = self._configs[row]
            self.api_key_input.setText(config.get("api_key", ""))
            
            provider = config.get("provider", "")
            for i in range(self.provider_combo.count()):
                if self.provider_combo.itemData(i) == provider:
                    self.provider_combo.setCurrentIndex(i)
                    break
            
            self._populate_model_combo(provider)
            saved_model = config.get("model", "")
            for i in range(self.model_combo.count()):
                if self.model_combo.itemText(i) == saved_model or self.model_combo.itemData(i) == saved_model:
                    self.model_combo.setCurrentIndex(i)
                    break
            else:
                index = self.model_combo.findText(saved_model)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                else:
                    self.model_combo.setCurrentText(saved_model)
            
            provider_display = PROVIDER_DISPLAY_NAMES.get(provider, provider)
            self.status_label.setText(f"已选择: {provider_display}")
            self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
        else:
            self._clear_form()
    
    def _clear_form(self):
        self.api_key_input.clear()
        self.model_combo.clear()
        if self.provider_combo.count() > 0:
            self.provider_combo.setCurrentIndex(0)
        self._populate_model_combo(self.provider_combo.currentData())
    
    def _add_config(self):
        self._clear_form()
        self._current_index = -1
        self.llm_list.clearSelection()
        self.status_label.setText("新配置")
        self.status_label.setStyleSheet("color: #f1c40f; font-size: 12px; padding-top: 10px;")
    
    def _delete_config(self):
        row = self.llm_list.currentRow()
        if 0 <= row < len(self._configs):
            config = self._configs[row]
            provider_display = PROVIDER_DISPLAY_NAMES.get(config.get("provider", ""), config.get("provider", ""))
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除配置 '{provider_display}' 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                config = self._configs[row]
                config_id = config.get("id", config.get("provider", ""))
                if self._memory_storage:
                    self._memory_storage.delete_llm_config(config_id)
                del self._configs[row]
                self.llm_list.takeItem(row)
                
                if self._default_config_id == config_id:
                    self._default_config_id = self._configs[0].get("id", self._configs[0].get("provider")) if self._configs else None
                    self._save_default_to_memory()
                
                self._clear_form()
                self.config_changed.emit(self._get_all_settings())
    
    def _save_config(self):
        provider = self.provider_combo.currentData()
        api_key = self.api_key_input.text().strip()
        model = self.model_combo.currentData().strip() if self.model_combo.currentData() else self.model_combo.currentText().strip()
        
        if not api_key:
            QMessageBox.warning(self, "保存失败", "请输入 API Key")
            return
        
        provider_display = PROVIDER_DISPLAY_NAMES.get(provider, provider)
        config_id = provider
        
        if 0 <= self._current_index < len(self._configs):
            config = self._configs[self._current_index]
            config["provider"] = provider
            config["api_key"] = api_key
            config["model"] = model
            self.llm_list.item(self._current_index).setText(provider_display)
        else:
            config = {
                "id": config_id,
                "provider": provider,
                "api_key": api_key,
                "model": model
            }
            self._configs.append(config)
            self.llm_list.addItem(provider_display)
            self._current_index = len(self._configs) - 1
            self.llm_list.setCurrentRow(self._current_index)
            
            if len(self._configs) == 1:
                self._default_config_id = config_id
                self._save_default_to_memory()
        
        if self._memory_storage:
            self._memory_storage.save_llm_config(config_id, provider, api_key, model)
        
        self.status_label.setText("✓ 已保存到记忆体")
        self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
        self.api_key_input.clear()
        self._update_list_display()
        self.config_changed.emit(self._get_all_settings())
    
    def _get_all_settings(self):
        current = self.get_current_config()
        default_config = None
        if self._default_config_id:
            for c in self._configs:
                if c.get("id", c.get("provider")) == self._default_config_id:
                    default_config = c
                    break
        
        if not default_config and self._configs:
            default_config = self._configs[0]
        
        return {
            "llm_configs": self._configs,
            "current_llm_config": current,
            "default_llm_config": default_config,
            "provider": (default_config or current or {}).get("provider"),
            "api_key": (default_config or current or {}).get("api_key"),
            "model": (default_config or current or {}).get("model"),
        }
    
    def _on_provider_changed(self, index):
        provider_key = self.provider_combo.currentData()
        self._populate_model_combo(provider_key)
        self.api_key_input.clear()
        self._current_index = -1
        self.llm_list.clearSelection()
    
    def _populate_model_combo(self, provider_key):
        self.model_combo.blockSignals(True)
        self.model_combo.clear()
        models = PROVIDER_MODELS.get(provider_key, [])
        for model_id, model_name in models:
            self.model_combo.addItem(model_name, model_id)
        self.model_combo.blockSignals(False)
        if self.model_combo.count() > 0:
            self.model_combo.setCurrentIndex(0)
    
    def _on_model_changed(self, index):
        pass
    
    def _toggle_key(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁")
    
    def _test_connection(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "测试失败", "请输入 API Key")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        self.status_label.setText("正在测试连接...")
        
        self.worker = LLMConfigWorker(
            self.provider_combo.currentData(),
            api_key,
            self.model_combo.currentData().strip() if self.model_combo.currentData() else self.model_combo.currentText().strip()
        )
        self.worker.finished.connect(self._on_test_finished)
        self.worker.start()
    
    def _set_default(self):
        row = self.llm_list.currentRow()
        if 0 <= row < len(self._configs):
            config = self._configs[row]
            self._default_config_id = config.get("id", config.get("provider"))
            self._update_list_display()
            self.status_label.setText("✓ 已设为默认")
            self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
            if self._memory_storage:
                try:
                    self._memory_storage.save_setting("default_llm_config", self._default_config_id)
                except Exception:
                    pass
            self._save_default_to_memory()
            self.config_changed.emit(self._get_all_settings())
    
    def _save_default_to_memory(self):
        try:
            import json
            from pathlib import Path
            meta_path = Path.home() / ".opentoad" / "memory.meta"
            meta = {}
            if meta_path.exists():
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                except Exception:
                    pass
            meta['default_llm_config'] = self._default_config_id
            meta_path.parent.mkdir(parents=True, exist_ok=True)
            with open(meta_path, 'w') as f:
                json.dump(meta, f)
        except Exception as e:
            print(f"Error saving default config: {e}")
    
    def _on_test_finished(self, success, error):
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔗 测试")
        
        if success:
            self.status_label.setText("✓ 连接成功！")
            self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
            QMessageBox.information(self, "测试成功", "✓ LLM 连接成功！")
        else:
            self.status_label.setText(f"✗ 连接失败: {error}")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
            QMessageBox.critical(self, "测试失败", f"连接失败:\n{error}")
    
    def _on_back_clicked(self):
        self.back_clicked.emit()
