from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QDialogButtonBox, QGroupBox, QLabel, QCheckBox, QSpinBox, QTabWidget, 
    QWidget, QListWidget, QAbstractItemView, QPushButton
)
from PySide6.QtCore import Qt

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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 - OpenToad")
        self.setModal(True)
        self.resize(500, 500)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        tabs.addTab(self._create_provider_tab(), "LLM设置")
        tabs.addTab(self._create_profile_tab(), "用户画像")
        
        layout.addWidget(tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _create_provider_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        provider_group = QGroupBox("LLM Provider")
        provider_layout = QFormLayout()
        
        self.provider_combo = QComboBox()
        for key, name in PROVIDERS:
            self.provider_combo.addItem(name, key)
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入 API Key")
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("模型名称")
        
        provider_layout.addRow("Provider:", self.provider_combo)
        provider_layout.addRow("API Key:", self.api_key_input)
        provider_layout.addRow("Model:", self.model_input)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        options_group = QGroupBox("选项")
        options_layout = QFormLayout()
        
        self.stream_checkbox = QCheckBox("启用流式输出")
        self.stream_checkbox.setChecked(True)
        
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(100, 4096)
        self.max_tokens_spin.setValue(1024)
        self.max_tokens_spin.setSuffix(" tokens")
        
        options_layout.addRow("流式输出:", self.stream_checkbox)
        options_layout.addRow("最大Token:", self.max_tokens_spin)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        return widget
    
    def _create_profile_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout()
        
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
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        interests_group = QGroupBox("兴趣领域 (可多选)")
        interests_layout = QVBoxLayout()
        
        self.interests_list = QListWidget()
        self.interests_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for field in INTEREST_FIELDS:
            self.interests_list.addItem(field)
        
        interests_layout.addWidget(self.interests_list)
        interests_group.setLayout(interests_layout)
        layout.addWidget(interests_group)
        
        prefs_group = QGroupBox("消费偏好")
        prefs_layout = QFormLayout()
        
        self.price_combo = QComboBox()
        for key, label in PRICE_SENSITIVITY:
            self.price_combo.addItem(label, key)
        
        self.factors_list = QListWidget()
        self.factors_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for key, label in DECISION_FACTORS:
            self.factors_list.addItem(label)
        
        prefs_layout.addRow("价格敏感度:", self.price_combo)
        prefs_layout.addRow("决策因素:", self.factors_list)
        
        prefs_group.setLayout(prefs_layout)
        layout.addWidget(prefs_group)
        
        return widget
    
    def _on_provider_changed(self, index: int):
        provider_key = self.provider_combo.currentData()
        default_model = PROVIDER_MODELS.get(provider_key, "")
        self.model_input.setText(default_model)
    
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
            if self.provider_combo.currentData() == settings.get("provider"):
                self.provider_combo.setCurrentIndex(i)
                break
        
        self.api_key_input.setText(settings.get("api_key", ""))
        self.model_input.setText(settings.get("model", ""))
        self.stream_checkbox.setChecked(settings.get("stream", True))
        self.max_tokens_spin.setValue(settings.get("max_tokens", 1024))
        
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
