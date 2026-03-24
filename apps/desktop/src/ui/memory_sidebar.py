from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFrame, QLineEdit, QScrollArea)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from src.memory import MemoryStorage
except ImportError:
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    from src.memory import MemoryStorage


class MemorySidebar(QWidget):
    memory_selected = Signal(str)
    memory_changed = Signal(str)
    new_chat_clicked = Signal()
    
    settings_clicked = Signal()
    account_clicked = Signal()
    about_clicked = Signal()
    llm_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._memory_id = None
        self._setup_ui()
    
    def _on_new_chat(self):
        self.new_chat_clicked.emit()
    
    def _setup_ui(self):
        self.setFixedWidth(80)
        self.setStyleSheet("background-color: #1a1a1a; border-right: 1px solid #333;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        top_section = QWidget()
        top_section.setStyleSheet("padding: 8px;")
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setFixedSize(40, 40)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                color: #d4d4d4;
            }
            QPushButton:hover { 
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        top_layout.addWidget(self.search_btn, 0, Qt.AlignCenter)
        
        self.new_chat_btn = QPushButton("+")
        self.new_chat_btn.setFixedSize(40, 40)
        self.new_chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        self.new_chat_btn.clicked.connect(self._on_new_chat)
        top_layout.addWidget(self.new_chat_btn, 0, Qt.AlignCenter)
        
        layout.addWidget(top_section)
        
        layout.addSpacing(20)
        
        nav_section = QWidget()
        nav_layout = QVBoxLayout(nav_section)
        nav_layout.setContentsMargins(8, 0, 8, 0)
        nav_layout.setSpacing(4)
        
        self.llm_btn = QPushButton("🤖")
        self.llm_btn.setFixedSize(40, 40)
        self.llm_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                color: #d4d4d4;
            }
            QPushButton:hover { 
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        self.llm_btn.clicked.connect(self.llm_clicked.emit)
        nav_layout.addWidget(self.llm_btn, 0, Qt.AlignCenter)
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                color: #d4d4d4;
            }
            QPushButton:hover { 
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        nav_layout.addWidget(self.settings_btn, 0, Qt.AlignCenter)
        
        self.account_btn = QPushButton("🔐")
        self.account_btn.setFixedSize(40, 40)
        self.account_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                color: #d4d4d4;
            }
            QPushButton:hover { 
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        self.account_btn.clicked.connect(self.account_clicked.emit)
        nav_layout.addWidget(self.account_btn, 0, Qt.AlignCenter)
        
        self.about_btn = QPushButton("ℹ️")
        self.about_btn.setFixedSize(40, 40)
        self.about_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                color: #d4d4d4;
            }
            QPushButton:hover { 
                background-color: #2a2a2a;
                color: #ffffff;
            }
        """)
        self.about_btn.clicked.connect(self.about_clicked.emit)
        nav_layout.addWidget(self.about_btn, 0, Qt.AlignCenter)
        
        layout.addWidget(nav_section)
        
        layout.addStretch()
        
        self.account_label = QLabel("未登录")
        self.account_label.setStyleSheet("color: #888; font-size: 10px; padding: 4px;")
        self.account_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.account_label)
    
    def set_account(self, email, logged_in=True):
        if logged_in and email:
            self.account_label.setText(email[:12])
        else:
            self.account_label.setText("未登录")


class SessionSidebar(QWidget):
    session_selected = Signal(int)
    session_deleted = Signal(int)
    new_session_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_index = 0
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFixedWidth(180)
        self.setStyleSheet("background-color: #1e1e1e; border-right: 1px solid #333;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet("background-color: #252526; padding: 12px; border-bottom: 1px solid #333;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 12, 8)
        
        self.memory_label = QLabel("🌰 记忆体1")
        self.memory_label.setStyleSheet("color: #fff; font-size: 12px; font-weight: bold;")
        header_layout.addWidget(self.memory_label)
        
        self.memory_btn = QPushButton("▼")
        self.memory_btn.setFixedSize(20, 20)
        self.memory_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 10px;
            }
            QPushButton:hover { color: #fff; }
        """)
        header_layout.addWidget(self.memory_btn)
        
        layout.addWidget(header)
        
        new_session_btn = QPushButton("+ 新建会话")
        new_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 8px 12px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        new_session_btn.clicked.connect(self.new_session_clicked.emit)
        layout.addWidget(new_session_btn)
        
        sessions_label = QLabel("会话")
        sessions_label.setStyleSheet("color: #888; font-size: 11px; padding: 8px 12px;")
        layout.addWidget(sessions_label)
        
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                padding: 0 8px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-radius: 6px;
                margin: 2px 4px;
                color: #d4d4d4;
                font-size: 12px;
            }
            QListWidget::item:selected {
                background-color: #2a4a6a;
            }
            QListWidget::item:hover {
                background-color: #252525;
            }
        """)
        self.session_list.itemClicked.connect(self._on_session_selected)
        self.session_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.session_list, 1)
    
    def _show_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu
        item = self.session_list.itemAt(pos)
        if item is None:
            return
        
        menu = QMenu(self)
        delete_action = menu.addAction("删除会话")
        delete_action.triggered.connect(lambda: self._delete_session(item))
        menu.exec(self.session_list.mapToGlobal(pos))
    
    def _delete_session(self, item):
        row = self.session_list.row(item)
        self.session_list.takeItem(row)
        self.session_deleted.emit(row)
    
    def add_session(self, name="新会话"):
        item = QListWidgetItem(name)
        row = self.session_list.count()
        item.setData(Qt.UserRole, row)
        self.session_list.addItem(item)
        self.session_list.setCurrentItem(item)
        return row
    
    def _on_new_chat(self):
        self.new_chat_clicked.emit()
    
    def _on_session_selected(self, item):
        index = item.data(Qt.UserRole)
        self.session_selected.emit(index)
    
    def set_memory_name(self, name):
        self.memory_label.setText(f"🌰 {name}")


class ChatTabs(QWidget):
    tab_selected = Signal(int)
    new_tab_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = []
        self._current_index = -1
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.tab_bar = QWidget()
        self.tab_bar.setStyleSheet("background-color: #252526; border-bottom: 1px solid #333;")
        self.tab_bar_layout = QHBoxLayout(self.tab_bar)
        self.tab_bar_layout.setContentsMargins(8, 4, 8, 0)
        self.tab_bar_layout.setSpacing(4)
        
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(28, 28)
        self.new_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888;
                border: 1px dashed #444;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover { 
                background-color: #333; 
                color: #fff;
                border: 1px solid #555;
            }
        """)
        self.new_tab_btn.clicked.connect(self.new_tab_requested.emit)
        self.tab_bar_layout.addWidget(self.new_tab_btn)
        self.tab_bar_layout.addStretch()
        
        layout.addWidget(self.tab_bar)
    
    def add_tab(self, title, chat_widget):
        index = len(self._tabs)
        
        tab_btn = QPushButton(f"  {title}  ×")
        tab_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                border-radius: 4px 4px 0 0;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #2e2e2e; }
        """)
        tab_btn.clicked.connect(lambda: self._select_tab(index))
        tab_btn._index = index
        
        self.tab_bar_layout.insertWidget(index, tab_btn)
        self._tabs.append({
            'title': title,
            'widget': chat_widget,
            'button': tab_btn
        })
        
        if self._current_index == -1:
            self._select_tab(index)
        
        return index
    
    def _select_tab(self, index):
        for i, tab in enumerate(self._tabs):
            if i == index:
                tab['button'].setStyleSheet("""
                    QPushButton {
                        background-color: #1a1a1a;
                        color: #fff;
                        border: none;
                        border-radius: 4px 4px 0 0;
                        padding: 6px 12px;
                        font-size: 12px;
                        border-bottom: 2px solid #0e639c;
                    }
                """)
            else:
                tab['button'].setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        color: #888;
                        border: none;
                        border-radius: 4px 4px 0 0;
                        padding: 6px 12px;
                        font-size: 12px;
                    }
                    QPushButton:hover { background-color: #2e2e2e; color: #d4d4d4; }
                """)
        
        self._current_index = index
        self.tab_selected.emit(index)
    
    def get_current_widget(self):
        if 0 <= self._current_index < len(self._tabs):
            return self._tabs[self._current_index]['widget']
        return None
    
    def get_current_index(self):
        return self._current_index
    
    def set_current_title(self, title):
        if 0 <= self._current_index < len(self._tabs):
            self._tabs[self._current_index]['title'] = title
            self._tabs[self._current_index]['button'].setText(f"  {title}  ×")
