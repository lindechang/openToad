from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QGroupBox
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Provider 设置
        provider_group = QGroupBox("LLM Provider")
        provider_layout = QFormLayout()
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["anthropic", "openai", "deepseek", "ollama"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.model_input = QLineEdit()
        self.model_input.setText("claude-3-5-sonnet-20241022")
        
        provider_layout.addRow("Provider:", self.provider_combo)
        provider_layout.addRow("API Key:", self.api_key_input)
        provider_layout.addRow("Model:", self.model_input)
        
        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # 保存初始 API key
        self.initial_api_key = ""
    
    def _on_provider_changed(self, provider: str):
        models = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "openai": "gpt-4o",
            "deepseek": "deepseek-chat",
            "ollama": "llama2"
        }
        self.model_input.setText(models.get(provider, ""))
    
    def get_settings(self):
        return {
            "provider": self.provider_combo.currentText(),
            "api_key": self.api_key_input.text(),
            "model": self.model_input.text()
        }
