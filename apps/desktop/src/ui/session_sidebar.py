from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
    QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, Signal
import os


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
    
    def update_session_name(self, row, name):
        if 0 <= row < self.session_list.count():
            item = self.session_list.item(row)
            if item:
                item.setText(name)
                item.setData(Qt.UserRole, row)
    
    def _on_session_selected(self, item):
        index = item.data(Qt.UserRole)
        self.session_selected.emit(index)
    
    def select_session(self, index):
        if 0 <= index < self.session_list.count():
            self.session_list.setCurrentRow(index)
