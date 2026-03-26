from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QMessageBox, QLineEdit, QFormLayout, QScrollArea, QTextEdit)
from PySide6.QtCore import Qt, Signal
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.memory import MemoryStorage
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
    from src.memory import MemoryStorage


class MemoryConfigPanel(QWidget):
    back_clicked = Signal()
    memory_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_memory_id = None
        self._session = None
        self.setup_ui()
    
    def set_session(self, session):
        self._session = session
        self._load_current_memory()
    
    def set_current_memory_id(self, memory_id):
        self._current_memory_id = memory_id
        self._load_current_memory()
    
    def _get_storage(self, memory_id):
        from pathlib import Path
        
        if self._session and hasattr(self._session, 'user_id') and self._session.user_id:
            user_id = str(self._session.user_id)
            
            from src.crypto.cipher import CryptoManager
            if self._session and hasattr(self._session, 'encryption_key') and self._session.encryption_key:
                crypto = CryptoManager(self._session.encryption_key)
                storage = MemoryStorage(user_id=user_id, memory_id=memory_id, crypto=crypto)
            else:
                storage = MemoryStorage(user_id=user_id, memory_id=memory_id)
            
            if storage.db_path.exists():
                return storage
            
            shared_db = Path.home() / ".opentoad" / "memory.db"
            if shared_db.exists():
                return MemoryStorage(db_path=str(shared_db))
            
            return storage
        else:
            shared_db = Path.home() / ".opentoad" / "memory.db"
            if shared_db.exists():
                return MemoryStorage(db_path=str(shared_db))
            return MemoryStorage()
    
    def _load_current_memory(self):
        try:
            storage = None
            info = None
            
            if self._current_memory_id:
                storage = self._get_storage(self._current_memory_id)
                info = storage.get_memory_info()
            elif self._session and hasattr(self._session, 'memory_id') and self._session.memory_id:
                self._current_memory_id = self._session.memory_id
                storage = self._get_storage(self._current_memory_id)
                info = storage.get_memory_info()
            
            if info and storage:
                self.name_input.setText(info.get("name", ""))
                self.desc_input.setText(info.get("description", ""))
                
                is_bound = info.get("bound_user_id") is not None
                created = info.get("created_at", "")
                memory_size = storage.db_path.stat().st_size if storage.db_path.exists() else 0
                size_str = self._format_size(memory_size)
                
                status = f"已绑定 · {size_str} · 创建于 {created[:10]}" if is_bound else f"未绑定 · {size_str} · 创建于 {created[:10]}"
                self.info_label.setText(status)
                self.status_label.setText(f"正在编辑: {info.get('name', '未命名')}")
                self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
                return
            
            self._load_unbound_memory()
        except Exception as e:
            print(f"Error loading memory: {e}")
            import traceback
            traceback.print_exc()
            self._load_unbound_memory()
    
    def _format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _load_unbound_memory(self):
        try:
            from pathlib import Path
            memories_dir = Path.home() / ".opentoad"
            memory_db = memories_dir / "memory.db"
            
            storage = None
            if memory_db.exists():
                storage = MemoryStorage(db_path=str(memory_db))
                info = storage.get_memory_info()
                if info:
                    self._current_memory_id = info.get("memory_id")
                    self.name_input.setText(info.get("name", ""))
                    self.desc_input.setText(info.get("description", ""))
                    
                    created = info.get("created_at", "")
                    memory_size = memory_db.stat().st_size
                    size_str = self._format_size(memory_size)
                    self.info_label.setText(f"本地记忆体 · {size_str} · 创建于 {created[:10]}")
                    self.status_label.setText(f"正在编辑: {info.get('name', '未命名')}")
                    self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
            else:
                storage = MemoryStorage.create_unbound_memory("我的记忆体")
                info = storage.get_memory_info()
                if info:
                    self._current_memory_id = info.get("memory_id")
                    self.name_input.setText(info.get("name", ""))
                    self.desc_input.setText("")
                    self.info_label.setText("本地记忆体")
                    self.status_label.setText("正在编辑: 我的记忆体")
                    self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
        except Exception as e:
            print(f"Error loading unbound memory: {e}")
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("🧠 记忆体设置")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 10px;")
        layout.addWidget(header)
        
        back_btn = QPushButton("← 返回对话")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: #d4d4d4;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
        """)
        back_btn.clicked.connect(self._on_back_clicked)
        layout.addWidget(back_btn)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        form_label = QLabel("记忆体设置")
        form_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        container_layout.addWidget(form_label)
        
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("记忆体名称")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #d4d4d4;
                font-size: 14px;
            }
        """)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("记忆体描述（可选）")
        self.desc_input.setStyleSheet("""
            QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                color: #d4d4d4;
                font-size: 13px;
                min-height: 100px;
            }
        """)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #888; font-size: 12px;")
        
        form_layout.addRow("名称:", self.name_input)
        form_layout.addRow("描述:", self.desc_input)
        form_layout.addRow("状态:", self.info_label)
        
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        self.save_btn.clicked.connect(self._save_memory)
        
        btn_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除记忆体")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
        """)
        self.delete_btn.clicked.connect(self._delete_memory)
        btn_layout.addWidget(self.delete_btn)
        
        btn_layout.addStretch()
        
        form_layout.addRow("", btn_layout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888; font-size: 12px; padding-top: 10px;")
        form_layout.addRow("", self.status_label)
        
        container_layout.addWidget(form_frame)
        
        container_layout.addStretch()
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
    
    def _save_memory(self):
        if not self._current_memory_id:
            self.status_label.setText("请先选择一个记忆体")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
            return
        
        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("请输入记忆体名称")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
            return
        
        try:
            user_id = str(self._session.user_id) if self._session and hasattr(self._session, 'user_id') and self._session.user_id else None
            memory_id = self._current_memory_id
            
            from src.crypto.cipher import CryptoManager
            if self._session and hasattr(self._session, 'encryption_key') and self._session.encryption_key:
                crypto = CryptoManager(self._session.encryption_key)
                storage = MemoryStorage(user_id=user_id, memory_id=memory_id, crypto=crypto)
            else:
                storage = MemoryStorage(user_id=user_id, memory_id=memory_id)
            
            storage.update_memory_info(name, self.desc_input.toPlainText().strip())
            
            self.status_label.setText("✓ 已保存")
            self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
            
            self.memory_changed.emit(self._current_memory_id)
        except Exception as e:
            self.status_label.setText(f"保存失败: {e}")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
    
    def _on_back_clicked(self):
        self.back_clicked.emit()
    
    def _delete_memory(self):
        if not self._current_memory_id:
            self.status_label.setText("没有选中的记忆体")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
            return
        
        memory_name = self.name_input.text().strip() or "未命名"
        
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除记忆体「{memory_name}」吗？\n\n此操作不可恢复，所有记忆数据将被永久删除。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                user_id = str(self._session.user_id) if self._session and hasattr(self._session, 'user_id') and self._session.user_id else None
                memory_id = self._current_memory_id
                
                MemoryStorage.delete_memory(user_id, memory_id)
                
                self.status_label.setText("✓ 记忆体已删除")
                self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px; padding-top: 10px;")
                
                self.memory_changed.emit(None)
                
                from PySide6.QtCore import QTimer
                QTimer.singleShot(1500, self.back_clicked.emit)
                
            except Exception as e:
                self.status_label.setText(f"删除失败: {e}")
                self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px; padding-top: 10px;")
