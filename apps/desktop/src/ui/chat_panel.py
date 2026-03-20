from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QTextCursor, QColor, QPalette, QKeyEvent, QFont, QTextCharFormat, QTextFormat
import re
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))


class ChatPanel(QWidget):
    def _load_icons(self):
        icons_dir = os.path.join(PROJECT_ROOT, 'icons')
        self.icon_user = os.path.join(icons_dir, 'opentoad-logo-60.png')
        self.icon_opentoad = os.path.join(icons_dir, 'opentoad-logo-60.png')
        self.icon_system = ""
        self.icon_error = ""


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
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
            }
        """)
        
        self._load_icons()
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
        self.chat_display.setFont(QFont("SF Pro Text", 13))
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
        self.input_field.setPlaceholderText("输入消息... (Enter 发送, Ctrl+Shift+S 清空)")
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
            QLineEdit:focus {
                border: 2px solid #0e639c;
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
        self.last_message_role = None
        self.input_field.setFocus()
    
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
        
        self.append_message("You", message, is_user=True)
        self.input_field.clear()
        self.send_button.setEnabled(False)
        self.send_button.setText("⏳")
        self.input_field.setPlaceholderText("正在思考...")
        
        self.current_streaming_message = ""
        self.last_message_role = None
        
        stream_enabled = getattr(self.agent, 'stream_enabled', True)
        
        self.worker = ChatWorker(self.agent, message, stream_enabled)
        self.worker.streaming.connect(self._on_streaming)
        self.worker.finished.connect(self._on_result)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    
    def _on_streaming(self, text: str):
        self.current_streaming_message += text
        self._update_last_message("OpenToad", self.current_streaming_message, is_streaming=True)
    
    def _on_result(self, result: str):
        self.append_message("OpenToad", result, is_streaming=False)
        self.send_button.setEnabled(True)
        self.send_button.setText("发送")
        self.input_field.setPlaceholderText("输入消息... (Enter 发送)")
        self.input_field.setFocus()
    
    def _on_error(self, error: str):
        self.append_message("Error", f"❌ {error}", is_error=True)
        self.send_button.setEnabled(True)
        self.send_button.setText("发送")
        self.input_field.setPlaceholderText("输入消息... (Enter 发送)")
        self.input_field.setFocus()
    
    def append_message(self, role: str, content: str, is_user=False, is_error=False, is_streaming=False):
        timestamp = datetime.now().strftime("%H:%M")
        
        colors = {
            "You": "#569cd6",
            "OpenToad": "#4ec9b0",
            "System": "#dcdcaa",
            "Error": "#f44747"
        }
        
        def get_icon(role):
            icon_map = {
                "You": self.icon_user,
                "OpenToad": self.icon_opentoad,
            }
            icon_path = icon_map.get(role)
            if icon_path and os.path.exists(icon_path):
                return f'<img src="{icon_path}" width="16" height="16" style="vertical-align: middle;">'
            emoji_map = {
                "You": "👤",
                "OpenToad": "🐸",
                "System": "⚙️",
                "Error": "⚠️"
            }
            return emoji_map.get(role, "💬")
        
        color = colors.get(role, "#d4d4d4")
        icon = get_icon(role)
        
        if is_user:
            html = f'''
            <div style="margin: 12px 0; padding: 12px; background-color: #2d4a3e; border-radius: 12px; border-left: 4px solid #4ec9b0;">
                <div style="color: #888; font-size: 11px; margin-bottom: 6px;">
                    {icon} You · {timestamp}
                </div>
                <div style="color: #d4d4d4; font-size: 14px; line-height: 1.6;">
                    {self._format_content(content)}
                </div>
            </div>
            '''
        elif is_error:
            html = f'''
            <div style="margin: 12px 0; padding: 12px; background-color: #3c2020; border-radius: 12px; border-left: 4px solid #f44747;">
                <div style="color: #f44747; font-size: 11px; margin-bottom: 6px;">
                    {icon} Error · {timestamp}
                </div>
                <div style="color: #d4d4d4; font-size: 14px; line-height: 1.6;">
                    {self._format_content(content)}
                </div>
            </div>
            '''
        elif is_streaming:
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.select(QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()
            
            html = f'''
            <div style="margin: 12px 0; padding: 12px; background-color: #2d3d4a; border-radius: 12px; border-left: 4px solid #569cd6;">
                <div style="color: #888; font-size: 11px; margin-bottom: 6px;">
                    {icon} OpenToad · {timestamp}
                </div>
                <div style="color: #d4d4d4; font-size: 14px; line-height: 1.6;">
                    {self._format_content(content)}<span style="color: #666;">▌</span>
                </div>
            </div>
            '''
        else:
            html = f'''
            <div style="margin: 12px 0; padding: 12px; background-color: #2d3d4a; border-radius: 12px; border-left: 4px solid #569cd6;">
                <div style="color: #888; font-size: 11px; margin-bottom: 6px;">
                    {icon} OpenToad · {timestamp}
                </div>
                <div style="color: #d4d4d4; font-size: 14px; line-height: 1.6;">
                    {self._format_content(content)}
                </div>
            </div>
            '''
        
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _update_last_message(self, role: str, content: str, is_streaming=False):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        cursor.movePosition(QTextCursor.PreviousBlock)
        
        timestamp = datetime.now().strftime("%H:%M")
        icon = "🐸"
        
        html = f'''
        <div style="margin: 12px 0; padding: 12px; background-color: #2d3d4a; border-radius: 12px; border-left: 4px solid #569cd6;">
            <div style="color: #888; font-size: 11px; margin-bottom: 6px;">
                {icon} OpenToad · {timestamp}
            </div>
            <div style="color: #d4d4d4; font-size: 14px; line-height: 1.6;">
                {self._format_content(content)}{'<span style="color: #666;">▌</span>' if is_streaming else ''}
            </div>
        </div>
        '''
        
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        
        self.chat_display.append(html)
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def _format_content(self, content: str):
        content = content.replace("&", "&amp;")
        content = content.replace("<", "&lt;")
        content = content.replace(">", "&gt;")
        
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
        content = re.sub(r'`(.+?)`', r'<code style="background: #3c3c3c; padding: 2px 6px; border-radius: 3px; font-family: monospace;">\1</code>', content)
        
        code_block_pattern = r'```(\w+)?\n(.*?)```'
        def code_block_replace(match):
            lang = match.group(1) or ''
            code = match.group(2)
            return f'<pre style="background: #1e1e1e; padding: 12px; border-radius: 6px; overflow-x: auto;"><code>{code}</code></pre>'
        
        content = re.sub(code_block_pattern, code_block_replace, content, flags=re.DOTALL)
        
        content = content.replace("\n", "<br>")
        
        return content
    
    def clear(self):
        self.chat_display.clear()
