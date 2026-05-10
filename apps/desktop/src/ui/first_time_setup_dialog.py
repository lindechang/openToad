from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal


class FirstTimeSetupDialog(QDialog):
    """首次设置对话框 - 让用户设置记忆体名字"""
    
    setup_complete = Signal(str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欢迎使用 OpenToad")
        self.setMinimumSize(400, 280)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; }
            QLabel { color: #d4d4d4; }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 12px 14px;
                font-size: 14px;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border: 2px solid #4ec9b0;
                background-color: #424242;
            }
            QLineEdit::placeholder { color: #888; }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #5fd9be; }
            QPushButton:pressed { background-color: #3db99e; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        header = QLabel("🐸 欢迎使用 OpenToad")
        header.setStyleSheet("font-size: 24px; color: #4ec9b0; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        desc = QLabel("你的记忆体还没取名字呢\n给它起个名字吧～")
        desc.setStyleSheet("font-size: 14px; color: #888; line-height: 1.6;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(16)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("给你的记忆体取个名字")
        self.name_input.returnPressed.connect(self._on_next)
        
        owner_layout = QHBoxLayout()
        owner_label = QLabel("你的名字：")
        owner_label.setStyleSheet("font-size: 14px; color: #aaa; min-width: 80px;")
        owner_layout.addWidget(owner_label)
        owner_layout.addWidget(self.name_input, 1)
        form_layout.addLayout(owner_layout)
        
        layout.addWidget(form_frame)
        
        hint = QLabel("💡 记忆体的名字就是 AI 的名字，你随时可以修改")
        hint.setStyleSheet("font-size: 12px; color: #666;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        
        layout.addSpacing(10)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.next_btn = QPushButton("开始使用 →")
        self.next_btn.setFixedSize(140, 44)
        self.next_btn.clicked.connect(self._on_next)
        btn_layout.addWidget(self.next_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_next(self):
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(
                self, 
                "请输入名字", 
                "请给你的记忆体取个名字！"
            )
            self.name_input.setFocus()
            return
        
        self.setup_complete.emit(name, "AI 助手", "")
        self.accept()
    
    def get_values(self):
        return {
            "name": self.name_input.text().strip() or "小蛙",
            "role": "AI 助手",
            "owner_name": ""
        }
