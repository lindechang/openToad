from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QTabWidget,
    QWidget, QListWidget, QListWidgetItem, QAbstractItemView, QPushButton, 
    QScrollArea, QFrame, QMessageBox, QTextEdit, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QThread, QSize
from PySide6.QtGui import QIcon, QFont
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.auth.service import AuthService


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

NAV_ITEMS = [
    ("🤖", "AI 对话"),
    ("🌰", "记忆体"),
    ("📱", "手机连接"),
    ("⚙️", "外观"),
    ("🔔", "通知"),
    ("🔒", "隐私"),
    ("ℹ️", "关于"),
]

class TestConnectionWorker(QThread):
    finished = Signal(bool, str, str)
    
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
            self.finished.emit(True, "", "")
        except Exception as e:
            self.finished.emit(False, str(e), "")


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


class SettingsDialog(QDialog):
    connection_test_clicked = Signal(str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 - OpenToad")
        self.setModal(True)
        self.resize(700, 500)
        self.setMinimumSize(650, 450)
        
        self._setup_styles()
        self._init_ui()
    
    def _setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #d4d4d4;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                background-color: #252526;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #4ec9b0;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px 12px;
                color: #d4d4d4;
                font-size: 13px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
            QLineEdit::placeholder {
                color: #888;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px 12px;
                color: #d4d4d4;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 1px solid #0e639c;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #888;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
                color: #d4d4d4;
            }
            QCheckBox {
                spacing: 8px;
                color: #d4d4d4;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid #555;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                background-color: #0e639c;
                border-color: #0e639c;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: none;
                padding: 8px;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 6px;
                color: #d4d4d4;
                font-size: 13px;
            }
            QListWidget::item:selected {
                background-color: #0e639c;
                color: #ffffff;
            }
            QListWidget::item:hover:!selected {
                background-color: #2d2d2d;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
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
            QPushButton#test_btn {
                background-color: #2d5a2d;
            }
            QPushButton#test_btn:hover {
                background-color: #3d7a3d;
            }
            QPushButton#toggle_password {
                background-color: transparent;
                border: none;
                padding: 4px;
                font-size: 16px;
                min-width: 30px;
            }
            QPushButton#toggle_password:hover {
                background-color: #3c3c3c;
            }
            QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #d4d4d4;
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: #252526;
            }
            QFrame#nav_separator {
                background-color: #3c3c3c;
                min-height: 1px;
                max-height: 1px;
                margin: 8px 16px;
            }
        """)
    
    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._create_nav_panel(main_layout)
        self._create_content_panel(main_layout)
        
        self.nav_list.currentRowChanged.connect(self._on_nav_changed)
        self.nav_list.setCurrentRow(0)
    
    def _create_nav_panel(self, parent_layout):
        nav_widget = QWidget()
        nav_widget.setFixedWidth(180)
        nav_widget.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #3c3c3c;")
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(8, 20, 8, 20)
        nav_layout.setSpacing(4)
        
        header = QLabel("🐸 设置")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0; padding: 8px 16px;")
        nav_layout.addWidget(header)
        
        self.nav_list = QListWidget()
        self.nav_list.setFocusPolicy(Qt.NoFocus)
        
        for icon, text in NAV_ITEMS:
            item = QListWidgetItem(f"  {icon}  {text}")
            item.setSizeHint(QSize(160, 40))
            self.nav_list.addItem(item)
        
        nav_layout.addWidget(self.nav_list)
        nav_layout.addStretch()
        
        parent_layout.addWidget(nav_widget)
    
    def _create_content_panel(self, parent_layout):
        self.content_stack = QStackedWidget()
        
        self.content_stack.addWidget(self._create_llm_page())
        self.content_stack.addWidget(self._create_memory_page())
        self.content_stack.addWidget(self._create_gateway_page())
        self.content_stack.addWidget(self._create_appearance_page())
        self.content_stack.addWidget(self._create_notification_page())
        self.content_stack.addWidget(self._create_privacy_page())
        self.content_stack.addWidget(self._create_about_page())
        
        parent_layout.addWidget(self.content_stack, 1)
    
    def _on_nav_changed(self, index):
        self.content_stack.setCurrentIndex(index)
    
    def _create_llm_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("AI 对话")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 20px;")
        layout.addWidget(header)
        
        provider_label = QLabel("服务商")
        provider_label.setStyleSheet("font-size: 13px; color: #d4d4d4; margin-bottom: 6px;")
        layout.addWidget(provider_label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.setFixedHeight(40)
        for key, name in PROVIDERS:
            self.provider_combo.addItem(name, key)
        layout.addWidget(self.provider_combo)
        
        layout.addSpacing(15)
        
        api_key_label = QLabel("API Key")
        api_key_label.setStyleSheet("font-size: 13px; color: #d4d4d4; margin-bottom: 6px;")
        layout.addWidget(api_key_label)
        
        api_key_container = QWidget()
        api_key_layout = QHBoxLayout(api_key_container)
        api_key_layout.setContentsMargins(0, 0, 0, 0)
        api_key_layout.setSpacing(4)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("输入 API Key")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setFixedHeight(40)
        
        toggle_btn = QPushButton("👁")
        toggle_btn.setObjectName("toggle_password")
        toggle_btn.setFixedWidth(40)
        toggle_btn.setFixedHeight(40)
        toggle_btn.clicked.connect(self._toggle_api_key)
        toggle_btn.setToolTip("显示/隐藏密码")
        
        api_key_layout.addWidget(self.api_key_input, 1)
        api_key_layout.addWidget(toggle_btn)
        
        layout.addWidget(api_key_container)
        
        layout.addSpacing(20)
        
        btn_layout = QHBoxLayout()
        
        self.save_llm_btn = QPushButton("保存")
        self.save_llm_btn.setFixedWidth(100)
        self.save_llm_btn.setFixedHeight(40)
        btn_layout.addWidget(self.save_llm_btn)
        
        self.test_llm_btn = QPushButton("测试连接")
        self.test_llm_btn.setFixedWidth(100)
        self.test_llm_btn.setFixedHeight(40)
        self.test_llm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d5a2d;
            }
            QPushButton:hover { background-color: #3d7a3d; }
        """)
        btn_layout.addWidget(self.test_llm_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.llm_status_label = QLabel("")
        self.llm_status_label.setStyleSheet("color: #888; font-size: 12px; margin-top: 10px;")
        layout.addWidget(self.llm_status_label)
        
        layout.addStretch()
        return page
    
    def _create_memory_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("🌰 记忆体设置")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.memory_name_input = QLineEdit()
        self.memory_name_input.setPlaceholderText("记忆体名称")
        
        self.memory_desc_input = QTextEdit()
        self.memory_desc_input.setPlaceholderText("记忆体描述（可选）")
        self.memory_desc_input.setMaximumHeight(80)
        
        form_layout.addRow("名称", self.memory_name_input)
        form_layout.addRow("描述", self.memory_desc_input)
        
        layout.addLayout(form_layout)
        
        self.memory_info_label = QLabel("")
        self.memory_info_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.memory_info_label)
        
        btn_layout = QHBoxLayout()
        
        self.save_memory_btn = QPushButton("保存")
        self.save_memory_btn.clicked.connect(self._save_memory_settings)
        btn_layout.addWidget(self.save_memory_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.memory_status_label = QLabel("")
        self.memory_status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.memory_status_label)
        
        self._load_memory_info()
        
        layout.addStretch()
        
        return page
    
    def _load_memory_info(self):
        try:
            main_window = self.parent()
            if hasattr(main_window, '_memory_storage'):
                info = main_window._memory_storage.get_memory_info()
                if info:
                    self.memory_name_input.setText(info.get("name", ""))
                    self.memory_desc_input.setText(info.get("description", ""))
                    
                    is_bound = info.get("bound_user_id") is not None
                    created = info.get("created_at", "")
                    status = f"已绑定 · 创建于 {created[:10]}" if is_bound else f"未绑定 · 创建于 {created[:10]}"
                    self.memory_info_label.setText(status)
        except Exception as e:
            self.memory_status_label.setText(f"加载失败: {e}")
            self.memory_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _save_memory_settings(self):
        name = self.memory_name_input.text().strip()
        if not name:
            self.memory_status_label.setText("请输入记忆体名称")
            self.memory_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        try:
            main_window = self.parent()
            if hasattr(main_window, '_memory_storage'):
                main_window._memory_storage.update_memory_info(name, self.memory_desc_input.toPlainText().strip())
                main_window._update_sidebar_memory_name()
                self.memory_status_label.setText("✓ 已保存")
                self.memory_status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        except Exception as e:
            self.memory_status_label.setText(f"保存失败: {e}")
            self.memory_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _populate_models(self, provider):
        pass
    
    def _on_provider_changed(self, index):
        pass
    
    def _toggle_api_key(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def _create_appearance_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("⚙️ 外观")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        group = QGroupBox("对话选项")
        options_layout = QFormLayout()
        options_layout.setSpacing(12)
        
        self.stream_checkbox = QCheckBox("启用流式输出 (实时显示回复)")
        self.stream_checkbox.setChecked(True)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4096)
        self.max_tokens_spin.setValue(1024)
        self.max_tokens_spin.setSuffix(" tokens")
        
        options_layout.addRow("流式输出", self.stream_checkbox)
        options_layout.addRow("最大Token", self.max_tokens_spin)
        
        group.setLayout(options_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        return page
    
    def _create_notification_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("🔔 通知设置")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        group = QGroupBox("通知")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)
        
        self.notify_enabled = QCheckBox("启用通知")
        self.notify_enabled.setChecked(True)
        group_layout.addWidget(self.notify_enabled)
        
        self.notify_sound = QCheckBox("提示音")
        self.notify_sound.setChecked(True)
        group_layout.addWidget(self.notify_sound)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        return page
    
    def _create_privacy_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("🔒 隐私设置")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        group = QGroupBox("隐私")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)
        
        self.privacy_local = QCheckBox("本地存储所有数据")
        self.privacy_local.setChecked(True)
        self.privacy_local.setEnabled(False)
        group_layout.addWidget(self.privacy_local)
        
        self.privacy_encrypt = QCheckBox("启用数据加密")
        self.privacy_encrypt.setChecked(True)
        group_layout.addWidget(self.privacy_encrypt)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        return page
    
    def _create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("ℹ️ 关于")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setSpacing(10)
        
        name_label = QLabel("🐸 OpenToad")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ec9b0;")
        
        version_label = QLabel("版本 1.0.0")
        version_label.setStyleSheet("font-size: 13px; color: #aaaaaa;")
        
        desc_label = QLabel("你的 AI 记忆分身\n独立执行 · 长期记忆 · 主动行动")
        desc_label.setStyleSheet("font-size: 13px; color: #aaaaaa; margin-top: 10px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(version_label)
        info_layout.addWidget(desc_label)
        
        layout.addWidget(info_card)
        
        layout.addStretch()
        return page
    
    def _create_gateway_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        header = QLabel("📱 手机连接")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0; margin-bottom: 10px;")
        layout.addWidget(header)
        
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        
        desc_label = QLabel(
            "开启后，手机客户端可以通过 WebSocket 直接与此 OpenToad 终端通讯，无需通过远程 API 服务器。"
        )
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 13px;")
        desc_label.setWordWrap(True)
        
        info_layout.addWidget(desc_label)
        layout.addWidget(info_card)
        
        group = QGroupBox("Gateway 配置")
        config_layout = QFormLayout()
        config_layout.setSpacing(12)
        
        self.gateway_enabled_checkbox = QCheckBox("启用 Gateway 服务")
        self.gateway_enabled_checkbox.setChecked(False)
        
        self.gateway_port_input = QLineEdit()
        self.gateway_port_input.setPlaceholderText("18989")
        self.gateway_port_input.setMaxLength(5)
        
        self.gateway_stream_checkbox = QCheckBox("启用流式输出")
        self.gateway_stream_checkbox.setChecked(True)
        
        config_layout.addRow("", self.gateway_enabled_checkbox)
        config_layout.addRow("端口", self.gateway_port_input)
        config_layout.addRow("", self.gateway_stream_checkbox)
        
        group.setLayout(config_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        return page
    
    def _toggle_api_key_visibility(self):
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_key_btn.setText("🔒")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_key_btn.setText("👁")
    
    def _on_ok_clicked(self):
        self.accept()
    
    def get_settings(self):
        return {
            "stream": self.stream_checkbox.isChecked(),
            "max_tokens": self.max_tokens_spin.value(),
            "gateway_enabled": self.gateway_enabled_checkbox.isChecked(),
            "gateway_port": int(self.gateway_port_input.text() or "18989"),
            "gateway_stream": self.gateway_stream_checkbox.isChecked(),
        }
    
    def load_settings(self, settings: dict):
        self.stream_checkbox.setChecked(settings.get("stream", True))
        self.max_tokens_spin.setValue(settings.get("max_tokens", 1024))
        
        self.gateway_enabled_checkbox.setChecked(settings.get("gateway_enabled", False))
        self.gateway_port_input.setText(str(settings.get("gateway_port", 18989)))
        self.gateway_stream_checkbox.setChecked(settings.get("gateway_stream", True))
