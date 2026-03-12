from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QGroupBox, QLabel, QCheckBox, QSpinBox
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


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置 - OpenToad")
        self.setModal(True)
        self.resize(450, 350)
        
        layout = QVBoxLayout(self)
        
        # Provider 设置
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
        
        # 选项设置
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
        
        # 说明
        info_label = QLabel("💡 支持多平台LLM API，按需配置")
        info_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(info_label)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.initial_api_key = ""
    
    def _on_provider_changed(self, index: int):
        provider_key = self.provider_combo.currentData()
        default_model = PROVIDER_MODELS.get(provider_key, "")
        self.model_input.setText(default_model)
    
    def get_settings(self):
        return {
            "provider": self.provider_combo.currentData(),
            "api_key": self.api_key_input.text(),
            "model": self.model_input.text(),
            "stream": self.stream_checkbox.isChecked(),
            "max_tokens": self.max_tokens_spin.value()
        }
