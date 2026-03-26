from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QTextCursor, QColor, QPalette, QKeyEvent, QFont, QTextCharFormat, QTextFormat
import re
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))


class ChatWorker(QThread):
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
    first_response_complete = Signal(object, str, str)
    
    def _load_icons(self):
        icons_dir = os.path.join(PROJECT_ROOT, 'icons')
        self.icon_user = os.path.join(icons_dir, 'opentoad-logo-120.png')
        self.icon_opentoad = os.path.join(icons_dir, 'opentoad-logo-120.png')
        self.icon_system = ""
        self.icon_error = ""
    
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
        """)
        
        self._load_icons()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: #d4d4d4;
            }
        """)
        layout.addWidget(self.chat_display, 1)
        
        input_container = QWidget()
        input_container.setStyleSheet("""
            background-color: #252526;
            border-top: 1px solid #3c3c3c;
            padding: 10px;
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
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
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.send_button.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_container)
        
        self.agent = None
        self.worker = None
        self.current_streaming_message = ""
        self.last_message_role = None
        self.input_field.setFocus()
        self._first_response_done = False
        self._first_user_message = ""
        self._messages = []
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_L:
            self.clear()
        else:
            super().keyPressEvent(event)
    
    def set_agent(self, agent):
        self.agent = agent
    
    def _send_message(self):
        if not self.agent:
            self.append_message("System", "⚠️ 请先在设置中配置 LLM Provider")
            return
        
        message = self.input_field.text().strip()
        if not message:
            return
        
        if not self._first_response_done:
            self._first_user_message = message
        
        self._messages.append({"role": "You", "content": message, "is_user": True})
        self._render_messages()
        
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.send_button.setText("⏳")
        self.input_field.setPlaceholderText("正在思考...")
        
        self.current_streaming_message = ""
        
        stream_enabled = getattr(self.agent, 'stream_enabled', True)
        
        self.worker = ChatWorker(self.agent, message, stream_enabled)
        self.worker.streaming.connect(self._on_streaming)
        self.worker.finished.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    
    def _render_messages(self):
        all_html = ""
        for msg in self._messages:
            all_html += self._build_message_html(msg["role"], msg["content"], 
                is_user=msg.get("is_user", False), 
                is_error=msg.get("is_error", False),
                is_streaming=msg.get("is_streaming", False))
        
        self.chat_display.setHtml(all_html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _build_message_html(self, role, content, is_user=False, is_error=False, is_streaming=False):
        timestamp = datetime.now().strftime("%H:%M")
        
        colors = {
            "You": "#569cd6",
            "OpenToad": "#4ec9b0",
            "System": "#dcdcaa",
            "Error": "#f44747"
        }
        
        emoji_map = {
            "You": "👤",
            "OpenToad": "🐸",
            "System": "⚙️",
            "Error": "⚠️"
        }
        
        icon = emoji_map.get(role, "💬")
        color = colors.get(role, "#d4d4d4")
        
        if is_user:
            return f'''
            <div style="display: flex; flex-direction: column; align-items: flex-end; margin: 10px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span style="color: #888; font-size: 12px; margin-right: 8px;">{timestamp}</span>
                    <span style="color: #888; font-size: 12px; font-weight: 500;">You</span>
                    <span style="margin-left: 8px;">{icon}</span>
                </div>
                <div style="max-width: 80%; padding: 10px; background-color: #0e639c; border-radius: 8px;">
                    <div style="color: #ffffff; font-size: 14px;">
                        {self._format_content(content)}
                    </div>
                </div>
            </div>
            '''
        elif is_error:
            return f'''
            <div style="display: flex; flex-direction: column; align-items: flex-start; margin: 10px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span style="margin-right: 8px;">{icon}</span>
                    <span style="color: #f44747; font-size: 12px; font-weight: 500;">Error</span>
                    <span style="color: #888; font-size: 12px; margin-left: 8px;">{timestamp}</span>
                </div>
                <div style="max-width: 80%; padding: 10px; background-color: #3c2020; border-radius: 8px; border-left: 3px solid #f44747;">
                    <div style="color: #d4d4d4; font-size: 14px;">
                        {self._format_content(content)}
                    </div>
                </div>
            </div>
            '''
        else:
            return f'''
            <div style="display: flex; flex-direction: column; align-items: flex-start; margin: 10px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <span style="margin-right: 8px;">{icon}</span>
                    <span style="color: {color}; font-size: 12px; font-weight: 500;">OpenToad</span>
                    <span style="color: #888; font-size: 12px; margin-left: 8px;">{timestamp}</span>
                </div>
                <div style="max-width: 80%; padding: 10px; background-color: #2d3d4a; border-radius: 8px; border-left: 3px solid {color};">
                    <div style="color: #d4d4d4; font-size: 14px;">
                        {self._format_content(content)}{'<span style="color: #666;">▌</span>' if is_streaming else ''}
                    </div>
                </div>
            </div>
            '''
    
    def _on_streaming(self, text: str):
        self.current_streaming_message += text
        
        if self._messages and self._messages[-1]["role"] == "OpenToad" and self._messages[-1].get("is_streaming"):
            self._messages[-1]["content"] = self.current_streaming_message
        else:
            self._messages.append({"role": "OpenToad", "content": self.current_streaming_message, "is_streaming": True})
        
        self._render_messages()
    
    def _on_result(self, result: str):
        self.current_streaming_message = result
        
        if self._messages and self._messages[-1]["role"] == "OpenToad":
            self._messages[-1]["content"] = result
            self._messages[-1]["is_streaming"] = False
        else:
            self._messages.append({"role": "OpenToad", "content": result, "is_streaming": False})
        
        self._render_messages()
        
        if not self._first_response_done:
            self._first_response_done = True
            self.first_response_complete.emit(self, self._first_user_message, result)
        
        self.send_button.setEnabled(True)
        self.send_button.setText("发送")
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setFocus()
    
    def _on_error(self, error: str):
        self.append_message("Error", f"❌ {error}", is_error=True)
        self.send_button.setEnabled(True)
        self.send_button.setText("发送")
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setFocus()
    
    def append_message(self, role: str, content: str, is_user=False, is_error=False, is_streaming=False):
        self._messages.append({
            "role": role, 
            "content": content, 
            "is_user": is_user,
            "is_error": is_error,
            "is_streaming": is_streaming
        })
        self._render_messages()
    
    def _format_content(self, content: str):
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        content = re.sub(r'`(.+?)`', r'<code style="background: #3c3c3c; padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 12px;">\1</code>', content)
        
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        def code_block_replace(match):
            lang = match.group(1) or ''
            code = match.group(2)
            return f'<div style="margin: 10px 0; border-radius: 4px; overflow: hidden; border: 1px solid #444;"><div style="background: #282a36; padding: 4px 8px; font-size: 12px; color: #888; border-bottom: 1px solid #444;">{lang if lang else "Code"}</div><pre style="background: #282a36; padding: 8px; margin: 0; overflow-x: auto; font-family: monospace; font-size: 12px;"><code>{code}</code></pre></div>'
        
        content = re.sub(code_block_pattern, code_block_replace, content, flags=re.DOTALL)
        
        content = content.replace("\n", "<br>")
        
        return content
    
    def clear(self):
        self._messages = []
        self.chat_display.clear()