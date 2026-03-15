from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QTabWidget,
    QWidget, QListWidget, QAbstractItemView, QPushButton, QScrollArea,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QIcon, QFont

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
    "anthropic": "claude-3-5-sonnet-20241022",
    "openai": "gpt-4o",
    "deepseek": "deepseek-chat",
    "qianwen": "qwen-turbo",
    "ernie": "ernie-bot",
    "hunyuan": "hunyuan-latest",
    "zhipu": "glm-4",
    "kimi": "moonshot-v1-8k",
    "gemini": "gemini-1.5-flash",
    "ollama": "llama2",
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
            from src.providers import create_provider
            llm = create_provider(self.provider, self.api_key)
            response = llm.chat("Hello")
            self.finished.emit(True, "", "")
        except Exception as e:
            self.finished.emit(False, str(e), "")


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
        tabs.addTab(self._create_provider_tab(), "🤖 LLM设置")
        tabs.addTab(self._create_profile_tab(), "👤 用户画像")
        
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
    
    def _create_provider_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        self._create_current_config_card(layout)
        self._create_provider_card(layout)
        self._create_options_card(layout)
        
        layout.addStretch()
        scroll.setWidget(widget)
        return scroll
    
    def _create_current_config_card(self, parent_layout):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2d4a3d;
                border: 1px solid #4ec9b0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        card_layout = QHBoxLayout(card)
        
        icon_label = QLabel("✓")
        icon_label.setStyleSheet("font-size: 20px; color: #4ec9b0;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        
        self.current_provider_label = QLabel("未设置")
        self.current_provider_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #ffffff;")
        
        self.current_model_label = QLabel("")
        self.current_model_label.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        
        info_layout.addWidget(self.current_provider_label)
        info_layout.addWidget(self.current_model_label)
        
        card_layout.addWidget(icon_label)
        card_layout.addLayout(info_layout)
        card_layout.addStretch()
        
        parent_layout.addWidget(card)
    
    def _create_provider_card(self, parent_layout):
        group = QGroupBox("LLM 配置")
        group_layout = QFormLayout()
        group_layout.setSpacing(12)
        group_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.provider_combo = QComboBox()
        for key, name in PROVIDERS:
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入 API Key")
        
        self.toggle_key_btn = QPushButton("👁")
        self.toggle_key_btn.setFixedWidth(35)
        self.toggle_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                padding: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        self.toggle_key_btn.clicked.connect(self._toggle_api_key_visibility)
        
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.toggle_key_btn)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("模型名称")
        self.model_input.textChanged.connect(self._update_current_config_display)
        
        self.test_btn = QPushButton("测试连接")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self._test_connection)
        
        test_layout = QHBoxLayout()
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        
        group_layout.addRow("Provider:", self.provider_combo)
        group_layout.addRow("API Key:", api_key_layout)
        group_layout.addRow("Model:", self.model_input)
        group_layout.addRow("", test_layout)
        
        group.setLayout(group_layout)
        parent_layout.addWidget(group)
    
    def _create_options_card(self, parent_layout):
        group = QGroupBox("选项设置")
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
        parent_layout.addWidget(group)
    
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
    
    def _on_provider_changed(self, index: int):
        provider_key = self.provider_combo.currentData()
        default_model = PROVIDER_MODELS.get(provider_key, "")
        self.model_input.setText(default_model)
        self._update_current_config_display()
    
    def _update_current_config_display(self):
        provider = self.provider_combo.currentData()
        model = self.model_input.text() or PROVIDER_MODELS.get(provider, "default")
        
        provider_display = PROVIDER_DISPLAY_NAMES.get(provider, provider)
        self.current_provider_label.setText(provider_display)
        self.current_model_label.setText(f"模型: {model}")
    
    def _test_connection(self):
        provider = self.provider_combo.currentData()
        api_key = self.api_key_input.text()
        model = self.model_input.text()
        
        if not api_key:
            QMessageBox.warning(self, "测试连接", "请输入 API Key")
            return
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        
        # 创建并启动测试连接线程
        self.test_worker = TestConnectionWorker(provider, api_key, model)
        self.test_worker.finished.connect(self._on_test_finished)
        self.test_worker.start()
    
    def _on_test_finished(self, success, error, response):
        provider = self.provider_combo.currentData()
        model = self.model_input.text()
        
        if success:
            QMessageBox.information(self, "测试连接", 
                f"✓ 连接成功！\n\nProvider: {PROVIDER_DISPLAY_NAMES.get(provider, provider)}\nModel: {model}")
        else:
            QMessageBox.critical(self, "测试连接", 
                f"✗ 连接失败\n\n错误: {error}")
        
        self.test_btn.setEnabled(True)
        self.test_btn.setText("测试连接")
    
    def _on_ok_clicked(self):
        api_key = self.api_key_input.text().strip()
        if not api_key:
            reply = QMessageBox.question(
                self, "确认",
                "API Key 未设置，是否保存？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
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
            "provider": self.provider_combo.currentData(),
            "api_key": self.api_key_input.text(),
            "model": self.model_input.text(),
            "stream": self.stream_checkbox.isChecked(),
            "max_tokens": self.max_tokens_spin.value(),
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
        for i in range(self.provider_combo.count()):
            if self.provider_combo.itemData(i) == settings.get("provider"):
                self.provider_combo.setCurrentIndex(i)
                break
        
        self.api_key_input.setText(settings.get("api_key", ""))
        self.model_input.setText(settings.get("model", ""))
        self.stream_checkbox.setChecked(settings.get("stream", True))
        self.max_tokens_spin.setValue(settings.get("max_tokens", 1024))
        
        self._update_current_config_display()
        
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
