from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QTabWidget,
    QWidget, QListWidget, QAbstractItemView, QPushButton, QScrollArea,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIcon, QFont
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.auth.service import AuthService

PROVIDER_DISPLAY_NAMES = {
    "anthropic": "Claude (Anthropic)",
    "openai": "OpenAI GPT",
    "deepseek": "DeepSeek",
    "qianwen": "阿里通义千问 (Qianwen)",
    "ernie": "百度文心一言 (ERNIE)",
    "hunyuan": "腾讯混元 (Hunyuan)",
    "zhipu": "智谱ChatGLM (Zhipu)",
    "kimi": "月之暗面 (Kimi)",
    "gemini": "Google Gemini",
    "ollama": "Ollama (本地)",
}

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

INTEREST_FIELDS = [
    "数码产品", "美妆护肤", "家居生活", "汽车用品", "服装时尚",
    "食品饮料", "运动健身", "图书影音", "旅游出行", "母婴育儿",
    "游戏动漫", "艺术品", "其他"
]

PRICE_SENSITIVITY = [
    ("budget", "平价实惠"),
    ("mid-range", "中端品质"),
    ("premium", "高端奢华")
]

DECISION_FACTORS = [
    ("function", "功能实用"),
    ("appearance", "外观颜值"),
    ("brand", "品牌知名度"),
    ("price", "价格优惠"),
    ("quality", "质量品质"),
    ("reviews", "用户口碑"),
    ("uniqueness", "独特稀有"),
    ("service", "售后服务")
]

AGE_RANGES = [
    ("under18", "18岁以下"),
    ("18-25", "18-25岁"),
    ("26-35", "26-35岁"),
    ("36-45", "36-45岁"),
    ("over45", "45岁以上")
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
        self.resize(550, 600)
        self.setMinimumHeight(550)
        
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
                padding: 8px;
                color: #d4d4d4;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
                color: #d4d4d4;
            }
            QComboBox:hover {
                border: 1px solid #0e639c;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
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
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
                color: #d4d4d4;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #888;
                padding: 10px 20px;
                border: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: #252526;
                color: #4ec9b0;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3c3c3c;
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
            QPushButton#test_btn {
                background-color: #2d5a2d;
            }
            QPushButton#test_btn:hover {
                background-color: #3d7a3d;
            }
            QDialogButtonBox {
                button-layout: 0;
            }
            QDialogButtonBox QPushButton {
                min-width: 80px;
            }
        """)
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        self._create_header(layout)
        
        tabs = QTabWidget()
        tabs.addTab(self._create_profile_tab(), "👤 用户画像")
        tabs.addTab(self._create_gateway_tab(), "📱 手机连接")
        tabs.addTab(self._create_options_tab(), "⚙️ 选项")
        
        layout.addWidget(tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_ok_clicked)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_header(self, parent_layout):
        header_widget = QFrame()
        header_widget.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d2d2d, stop:1 #3d3d3d); border-radius: 8px; padding: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel("🐸 OpenToad 设置")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("font-size: 12px; color: #888;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(version_label)
        
        parent_layout.addWidget(header_widget)
    
    def _create_options_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        group = QGroupBox("对话选项")
        options_layout = QFormLayout()
        options_layout.setSpacing(12)
        
        self.stream_checkbox = QCheckBox("启用流式输出 (实时显示回复)")
        self.stream_checkbox.setChecked(True)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4096)
        self.max_tokens_spin.setValue(1024)
        self.max_tokens_spin.setSuffix(" tokens")
        
        options_layout.addRow("流式输出:", self.stream_checkbox)
        options_layout.addRow("最大Token:", self.max_tokens_spin)
        
        group.setLayout(options_layout)
        layout.addWidget(group)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_profile_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        self._create_basic_info_card(layout)
        self._create_interests_card(layout)
        self._create_prefs_card(layout)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_account_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        self._create_auth_status_card(layout)
        self._create_login_card(layout)
        self._create_register_card(layout)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_auth_status_card(self, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border: 1px solid #4ec9b0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        card_layout = QHBoxLayout(card)
        
        self.auth_status_icon = QLabel("🔒")
        self.auth_status_icon.setStyleSheet("font-size: 24px;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        self.auth_status_label = QLabel("未登录")
        self.auth_status_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        
        self.auth_status_desc = QLabel("登录后可加密保护您的记忆数据")
        self.auth_status_desc.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        
        info_layout.addWidget(self.auth_status_label)
        info_layout.addWidget(self.auth_status_desc)
        
        self.logout_btn = QPushButton("登出")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
        """)
        self.logout_btn.clicked.connect(self._do_logout)
        self.logout_btn.hide()
        
        card_layout.addWidget(self.auth_status_icon)
        card_layout.addLayout(info_layout)
        card_layout.addStretch()
        card_layout.addWidget(self.logout_btn)
        
        parent_layout.addWidget(card)
        
        self._check_initial_auth_status()
    
    def _check_initial_auth_status(self):
        auth_service = self._get_auth_service()
        if auth_service.is_logged_in:
            session = auth_service.session
            self._update_auth_display(True, session.email)
        else:
            self._update_auth_display(False)
    
    def _create_login_card(self, parent_layout):
        group = QGroupBox("登录")
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.login_email_input = QLineEdit()
        self.login_email_input.setPlaceholderText("邮箱")
        
        self.login_password_input = QLineEdit()
        self.login_password_input.setPlaceholderText("密码")
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self._do_login)
        
        self.login_status_label = QLabel("")
        self.login_status_label.setStyleSheet("color: #888; font-size: 12px;")
        
        form_layout.addRow("邮箱:", self.login_email_input)
        form_layout.addRow("密码:", self.login_password_input)
        form_layout.addRow("", self.login_btn)
        form_layout.addRow("", self.login_status_label)
        
        group.setLayout(form_layout)
        parent_layout.addWidget(group)
    
    def _create_register_card(self, parent_layout):
        group = QGroupBox("注册新账号")
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        self.reg_name_input = QLineEdit()
        self.reg_name_input.setPlaceholderText("昵称")
        
        self.reg_email_input = QLineEdit()
        self.reg_email_input.setPlaceholderText("邮箱")
        
        self.reg_password_input = QLineEdit()
        self.reg_password_input.setPlaceholderText("密码")
        self.reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.reg_password2_input = QLineEdit()
        self.reg_password2_input.setPlaceholderText("确认密码")
        self.reg_password2_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self._do_register)
        
        self.register_status_label = QLabel("")
        self.register_status_label.setStyleSheet("color: #888; font-size: 12px;")
        
        form_layout.addRow("昵称:", self.reg_name_input)
        form_layout.addRow("邮箱:", self.reg_email_input)
        form_layout.addRow("密码:", self.reg_password_input)
        form_layout.addRow("确认:", self.reg_password2_input)
        form_layout.addRow("", self.register_btn)
        form_layout.addRow("", self.register_status_label)
        
        group.setLayout(form_layout)
        parent_layout.addWidget(group)
    
    def _get_auth_service(self):
        server_url = self.parent().settings.get("server_url", "http://api.opentoad.cn") if hasattr(self.parent(), 'settings') else "http://api.opentoad.cn"
        return AuthService(server_url)
    
    def _update_auth_display(self, logged_in=False, email=None):
        if logged_in and email:
            self.auth_status_icon.setText("🔓")
            self.auth_status_label.setText(f"已登录: {email}")
            self.auth_status_desc.setText("您的记忆数据已加密保护")
            self.logout_btn.show()
        else:
            self.auth_status_icon.setText("🔒")
            self.auth_status_label.setText("未登录")
            self.auth_status_desc.setText("登录后可加密保护您的记忆数据")
            self.logout_btn.hide()
    
    def _do_login(self):
        email = self.login_email_input.text().strip()
        password = self.login_password_input.text()
        
        if not email or not password:
            self.login_status_label.setText("请输入邮箱和密码")
            self.login_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")
        self.login_status_label.setText("正在登录...")
        
        auth_service = self._get_auth_service()
        self.auth_worker = AuthWorker(auth_service, 'login', email, password)
        self.auth_worker.finished.connect(self._on_login_success)
        self.auth_worker.error.connect(self._on_login_error)
        self.auth_worker.start()
    
    def _on_login_success(self, session):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登录")
        self.login_status_label.setText(f"✓ 登录成功: {session.email}")
        self.login_status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        self._update_auth_display(True, session.email)
        self.login_email_input.clear()
        self.login_password_input.clear()
        
        if hasattr(self.parent(), '_update_auth_status'):
            self.parent().session = session
            self.parent()._update_auth_status()
    
    def _on_login_error(self, error_msg):
        self.login_btn.setEnabled(True)
        self.login_btn.setText("登录")
        self.login_status_label.setText(f"✗ 登录失败: {error_msg}")
        self.login_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _do_register(self):
        name = self.reg_name_input.text().strip()
        email = self.reg_email_input.text().strip()
        password = self.reg_password_input.text()
        password2 = self.reg_password2_input.text()
        
        if not name or not email or not password:
            self.register_status_label.setText("请填写所有字段")
            self.register_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        if password != password2:
            self.register_status_label.setText("两次密码不一致")
            self.register_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.register_btn.setEnabled(False)
        self.register_btn.setText("注册中...")
        self.register_status_label.setText("正在注册...")
        
        auth_service = self._get_auth_service()
        self.auth_worker = AuthWorker(auth_service, 'register', email, password, name)
        self.auth_worker.finished.connect(self._on_register_success)
        self.auth_worker.error.connect(self._on_register_error)
        self.auth_worker.start()
    
    def _on_register_success(self, result):
        self.register_btn.setEnabled(True)
        self.register_btn.setText("注册")
        self.register_status_label.setText("✓ 注册成功！请登录")
        self.register_status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        
        self.login_email_input.setText(self.reg_email_input.text())
        self.reg_name_input.clear()
        self.reg_email_input.clear()
        self.reg_password_input.clear()
        self.reg_password2_input.clear()
    
    def _on_register_error(self, error_msg):
        self.register_btn.setEnabled(True)
        self.register_btn.setText("注册")
        self.register_status_label.setText(f"✗ 注册失败: {error_msg}")
        self.register_status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _do_logout(self):
        auth_service = self._get_auth_service()
        auth_service.logout()
        self._update_auth_display(False)
        self.login_status_label.setText("")
        self.register_status_label.setText("")
        
        if hasattr(self.parent(), '_update_auth_status'):
            self.parent().session = None
            self.parent()._update_auth_status()
    
    def _create_gateway_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        self._create_gateway_info_card(layout)
        self._create_gateway_config_card(layout)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_gateway_info_card(self, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border: 1px solid #4ec9b0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        title_label = QLabel("📱 手机 App 连接")
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #4ec9b0;")
        
        desc_label = QLabel(
            "开启后，手机客户端可以通过 WebSocket 直接与此 OpenToad 终端通讯，"
            "无需通过远程 API 服务器。"
        )
        desc_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        desc_label.setWordWrap(True)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        
        parent_layout.addWidget(card)
    
    def _create_gateway_config_card(self, parent_layout):
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
        config_layout.addRow("端口:", self.gateway_port_input)
        config_layout.addRow("", self.gateway_stream_checkbox)
        
        group.setLayout(config_layout)
        parent_layout.addWidget(group)
    
    def _create_basic_info_card(self, parent_layout):
        group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        basic_layout.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("助手名字")
        
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("助手昵称(可选)")
        
        self.age_combo = QComboBox()
        for key, label in AGE_RANGES:
            self.age_combo.addItem(label, key)
        
        self.occupation_input = QLineEdit()
        self.occupation_input.setPlaceholderText("职业")
        
        self.personality_input = QLineEdit()
        self.personality_input.setPlaceholderText("性格特点(可选)")
        
        basic_layout.addRow("名字:", self.name_input)
        basic_layout.addRow("昵称:", self.nickname_input)
        basic_layout.addRow("年龄:", self.age_combo)
        basic_layout.addRow("职业:", self.occupation_input)
        basic_layout.addRow("性格:", self.personality_input)
        
        group.setLayout(basic_layout)
        parent_layout.addWidget(group)
    
    def _create_interests_card(self, parent_layout):
        group = QGroupBox("兴趣领域 (可多选)")
        interests_layout = QVBoxLayout()
        
        self.interests_list = QListWidget()
        self.interests_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.interests_list.setMinimumHeight(120)
        for field in INTEREST_FIELDS:
            self.interests_list.addItem(field)
        
        interests_layout.addWidget(self.interests_list)
        group.setLayout(interests_layout)
        parent_layout.addWidget(group)
    
    def _create_prefs_card(self, parent_layout):
        group = QGroupBox("消费偏好")
        prefs_layout = QFormLayout()
        prefs_layout.setSpacing(12)
        
        self.price_combo = QComboBox()
        for key, label in PRICE_SENSITIVITY:
            self.price_combo.addItem(label, key)
        
        self.factors_list = QListWidget()
        self.factors_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.factors_list.setMinimumHeight(100)
        for key, label in DECISION_FACTORS:
            self.factors_list.addItem(label)
        
        prefs_layout.addRow("价格敏感度:", self.price_combo)
        prefs_layout.addRow("决策因素:", self.factors_list)
        
        group.setLayout(prefs_layout)
        parent_layout.addWidget(group)
    
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
        selected_interests = [self.interests_list.item(i).text()
                            for i in range(self.interests_list.count())
                            if self.interests_list.item(i).isSelected()]
        
        selected_factors = [self.factors_list.item(i).text()
                          for i in range(self.factors_list.count())
                          if self.factors_list.item(i).isSelected()]
        
        factor_keys = []
        for key, label in DECISION_FACTORS:
            if label in selected_factors:
                factor_keys.append(key)
        
        return {
            "stream": self.stream_checkbox.isChecked(),
            "max_tokens": self.max_tokens_spin.value(),
            "gateway_enabled": self.gateway_enabled_checkbox.isChecked(),
            "gateway_port": int(self.gateway_port_input.text() or "18989"),
            "gateway_stream": self.gateway_stream_checkbox.isChecked(),
            "profile": {
                "name": self.name_input.text(),
                "nickname": self.nickname_input.text(),
                "age_range": self.age_combo.currentData(),
                "occupation": self.occupation_input.text(),
                "personality": self.personality_input.text(),
                "interests": selected_interests,
                "price_sensitivity": self.price_combo.currentData(),
                "decision_factors": factor_keys
            }
        }
    
    def load_settings(self, settings: dict):
        self.stream_checkbox.setChecked(settings.get("stream", True))
        self.max_tokens_spin.setValue(settings.get("max_tokens", 1024))
        
        self.gateway_enabled_checkbox.setChecked(settings.get("gateway_enabled", False))
        self.gateway_port_input.setText(str(settings.get("gateway_port", 18989)))
        self.gateway_stream_checkbox.setChecked(settings.get("gateway_stream", True))
        
        profile = settings.get("profile", {})
        self.name_input.setText(profile.get("name", ""))
        self.nickname_input.setText(profile.get("nickname", ""))
        
        for i in range(self.age_combo.count()):
            if self.age_combo.itemData(i) == profile.get("age_range"):
                self.age_combo.setCurrentIndex(i)
                break
        
        self.occupation_input.setText(profile.get("occupation", ""))
        self.personality_input.setText(profile.get("personality", ""))
        
        interests = profile.get("interests", [])
        for i in range(self.interests_list.count()):
            if self.interests_list.item(i).text() in interests:
                self.interests_list.item(i).setSelected(True)
        
        for i in range(self.price_combo.count()):
            if self.price_combo.itemData(i) == profile.get("price_sensitivity"):
                self.price_combo.setCurrentIndex(i)
                break
        
        factors = profile.get("decision_factors", [])
        factor_labels = [label for key, label in DECISION_FACTORS if key in factors]
        for i in range(self.factors_list.count()):
            if self.factors_list.item(i).text() in factor_labels:
                self.factors_list.item(i).setSelected(True)
