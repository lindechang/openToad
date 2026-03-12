from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QThread, Signal, QObject

class AgentWorker(QObject):
    finished = Signal(str)
    error = Signal(str)
    
    def __init__(self, agent, message):
        super().__init__()
        self.agent = agent
        self.message = message
    
    def run(self):
        try:
            result = self.agent.chat_sync(self.message)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        self.agent = None
        self.worker = None
    
    def set_agent(self, agent):
        self.agent = agent
    
    def _send_message(self):
        if not self.agent:
            self.append_message("System", "请先在设置中配置 LLM Provider")
            return
        
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.append_message("You", message)
        self.input_field.clear()
        self.send_button.setEnabled(False)
        
        # 异步执行
        self.worker = AgentWorker(self.agent, message)
        self.worker.finished.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.run()
    
    def _on_result(self, result: str):
        self.append_message("OpenToad", result)
        self.send_button.setEnabled(True)
    
    def _on_error(self, error: str):
        self.append_message("Error", error)
        self.send_button.setEnabled(True)
    
    def append_message(self, role: str, content: str):
        self.chat_display.append(f"<b>{role}:</b><br>{content}<br>")
