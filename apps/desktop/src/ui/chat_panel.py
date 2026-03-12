from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QTextCursor, QColor, QPalette

class AgentWorker(QObject):
    finished = Signal(str)
    error = Signal(str)
    streaming = Signal(str)
    
    def __init__(self, agent, message, stream=True):
        super().__init__()
        self.agent = agent
        self.message = message
        self.stream = stream
    
    def run(self):
        try:
            if self.stream:
                result = self.agent.chat_stream(self.message, self.streaming.emit)
            else:
                result = self.agent.chat_sync(self.message)
                self.streaming.emit(result)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ChatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 对话显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                color: #d4d4d4;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # 输入区域
        input_container = QWidget()
        input_container.setStyleSheet("""
            background-color: #252526;
            border-radius: 8px;
            padding: 5px;
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息... (Enter 发送)")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                color: #d4d4d4;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """)
        self.input_field.returnPressed.connect(self._send_message)
        
        self.send_button = QPushButton("发送")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
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
        """)
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        layout.addWidget(input_container)
        
        self.agent = None
        self.worker = None
        self.current_streaming_message = ""
    
    def set_agent(self, agent):
        self.agent = agent
    
    def _send_message(self):
        if not self.agent:
            self.append_message("System", "⚠️ 请先在设置中配置 LLM Provider")
            return
        
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.append_message("You", message, is_user=True)
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.input_field.setPlaceholderText("正在思考...")
        
        self.current_streaming_message = ""
        
        stream_enabled = getattr(self.agent, 'stream_enabled', True)
        
        self.worker = AgentWorker(self.agent, message, stream_enabled)
        self.worker.streaming.connect(self._on_streaming)
        self.worker.finished.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.run()
    
    def _on_streaming(self, text: str):
        self.current_streaming_message += text
        self._update_last_message("OpenToad", self.current_streaming_message, is_streaming=True)
    
    def _on_result(self, result: str):
        self.append_message("OpenToad", result, is_streaming=False)
        self.send_button.setEnabled(True)
        self.input_field.setPlaceholderText("输入消息... (Enter 发送)")
    
    def _on_error(self, error: str):
        self.append_message("Error", f"❌ {error}", is_error=True)
        self.send_button.setEnabled(True)
        self.input_field.setPlaceholderText("输入消息... (Enter 发送)")
    
    def append_message(self, role: str, content: str, is_user=False, is_error=False, is_streaming=False):
        colors = {
            "You": "#569cd6",
            "OpenToad": "#4ec9b0",
            "System": "#dcdcaa",
            "Error": "#f44747"
        }
        
        color = colors.get(role, "#d4d4d4")
        
        if is_user:
            html = f'<div style="margin: 10px 0;">' \
                   f'<span style="color: {color}; font-weight: bold; font-size: 14px;">👤 You</span><br>' \
                   f'<span style="color: #d4d4d4; font-size: 14px; line-height: 1.5;">{self._format_content(content)}</span>' \
                   f'</div>'
        elif is_error:
            html = f'<div style="margin: 10px 0; padding: 10px; background-color: #3c2020; border-radius: 5px;">' \
                   f'<span style="color: {color}; font-weight: bold; font-size: 14px;">⚠️ Error</span><br>' \
                   f'<span style="color: #d4d4d4; font-size: 14px; line-height: 1.5;">{self._format_content(content)}</span>' \
                   f'</div>'
        elif is_streaming:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.select(QTextCursor.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
            
            html = f'<div style="margin: 10px 0;">' \
                   f'<span style="color: {color}; font-weight: bold; font-size: 14px;">🐸 OpenToad</span><br>' \
                   f'<span style="color: #d4d4d4; font-size: 14px; line-height: 1.5;">{self._format_content(content)}</span><span style="color: #666;">▌</span>' \
                   f'</div>'
        else:
            html = f'<div style="margin: 10px 0;">' \
                   f'<span style="color: {color}; font-weight: bold; font-size: 14px;">🐸 OpenToad</span><br>' \
                   f'<span style="color: #d4d4d4; font-size: 14px; line-height: 1.5;">{self._format_content(content)}</span>' \
                   f'</div>'
        
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _update_last_message(self, role: str, content: str, is_streaming=False):
        self.append_message(role, content, is_streaming=is_streaming)
    
    def _format_content(self, content: str):
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        content = content.replace("\n", "<br>")
        
        content = content.replace("```", "&nbsp;```&nbsp;")
        content = content.replace("`", "&nbsp;`&nbsp;")
        
        return content
    
    def clear(self):
        self.chat_display.clear()
