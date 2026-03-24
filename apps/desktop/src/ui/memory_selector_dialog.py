from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QLineEdit, QFormLayout, QScrollArea, QComboBox, QGroupBox, QRadioButton)
from PySide6.QtCore import Qt, QThread, Signal
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from src.memory import MemoryStorage
    from src.crypto.cipher import CryptoManager
except ImportError:
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    from src.memory import MemoryStorage
    from src.crypto.cipher import CryptoManager


class MemorySelectorDialog(QDialog):
    memory_selected = Signal(str, str)
    
    def __init__(self, user_id, encryption_key, parent=None):
        super().__init__(parent)
        self.user_id = str(user_id)
        self.encryption_key = encryption_key
        self.crypto = CryptoManager(encryption_key) if encryption_key else None
        
        self.setWindowTitle("选择记忆体")
        self.setMinimumSize(500, 500)
        self.setModal(True)
        
        self.setup_ui()
        self.load_memories()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("请选择要使用的记忆体")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #4ec9b0; padding: 10px 0;")
        layout.addWidget(header)
        
        desc = QLabel("已登录账号后，您需要选择一个记忆体来存储对话记忆和数据。")
        desc.setStyleSheet("color: #888; font-size: 12px; padding-bottom: 15px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        options_group = QGroupBox("选择方式")
        options_layout = QVBoxLayout()
        
        self.pull_online_radio = QRadioButton("📥 拉取线上备份的记忆体")
        options_layout.addWidget(self.pull_online_radio)
        
        self.create_new_radio = QRadioButton("➕ 创建新的记忆体（绑定到当前账号）")
        self.create_new_radio.setChecked(True)
        options_layout.addWidget(self.create_new_radio)
        
        self.bind_local_radio = QRadioButton("🔗 绑定本地的未绑定记忆体")
        options_layout.addWidget(self.bind_local_radio)
        
        self.create_unbound_radio = QRadioButton("✨ 创建新的未绑定记忆体（不绑定任何账号）")
        options_layout.addWidget(self.create_unbound_radio)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        self.local_list = QListWidget()
        self.local_list.setStyleSheet("""
            QListWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                color: #d4d4d4;
            }
        """)
        self.local_list.itemDoubleClicked.connect(self._on_bind_local)
        layout.addWidget(QLabel("本地记忆体:"))
        layout.addWidget(self.local_list)
        
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("输入新记忆体名称...")
        self.new_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 8px;
                color: #d4d4d4;
            }
        """)
        self.new_name_input.setVisible(False)
        layout.addWidget(QLabel("新记忆体名称:"))
        layout.addWidget(self.new_name_input)
        
        self.pull_online_radio.toggled.connect(self._on_option_changed)
        self.create_new_radio.toggled.connect(self._on_option_changed)
        self.bind_local_radio.toggled.connect(self._on_option_changed)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #666; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        self.confirm_btn = QPushButton("确定")
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #1177bb; }
        """)
        self.confirm_btn.clicked.connect(self._on_confirm)
        btn_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_option_changed(self):
        self.local_list.setVisible(self.bind_local_radio.isChecked())
        self.new_name_input.setVisible(self.create_new_radio.isChecked() or self.create_unbound_radio.isChecked())
    
    def load_memories(self):
        self.local_list.clear()
        
        try:
            local_memories = MemoryStorage.list_user_memories(self.user_id, self.crypto)
            
            shared_memories = []
            try:
                shared = MemoryStorage.list_user_memories(None)
                for m in shared:
                    if not m.get("is_shared"):
                        continue
                    shared_memories.append(m)
            except Exception:
                pass
            
            for m in local_memories:
                item = QListWidgetItem(f"📁 {m.get('name', '未命名')} ({m.get('memory_id', 'unknown')[:8]}...)")
                item.setData(Qt.UserRole, m)
                self.local_list.addItem(item)
            
            for m in shared_memories:
                item = QListWidgetItem(f"📦 未绑定 - {m.get('name', '默认记忆体')} ({m.get('memory_id', 'unknown')[:8] if m.get('memory_id') else 'shared'}...)")
                item.setData(Qt.UserRole, m)
                item.setForeground(Qt.gray)
                self.local_list.addItem(item)
            
            self.bind_local_radio.setEnabled(self.local_list.count() > 0)
            if self.local_list.count() > 0:
                self.local_list.setCurrentRow(0)
        except Exception as e:
            print(f"Error loading memories: {e}")
    
    def _on_bind_local(self, item):
        self.bind_local_radio.setChecked(True)
        self._on_confirm()
    
    def _on_confirm(self):
        if self.pull_online_radio.isChecked():
            QMessageBox.information(self, "提示", "线上备份功能即将推出，请先创建新记忆体。")
            self.create_new_radio.setChecked(True)
            return
        
        elif self.create_new_radio.isChecked():
            name = self.new_name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "警告", "请输入新记忆体名称")
                return
            
            try:
                new_storage = MemoryStorage.create_memory(
                    self.user_id, 
                    crypto=self.crypto, 
                    name=name,
                    bind_immediately=True
                )
                memory_info = new_storage.get_memory_info()
                self.memory_selected.emit("create", memory_info.get("memory_id"))
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建记忆体失败: {str(e)}")
        
        elif self.create_unbound_radio.isChecked():
            name = self.new_name_input.text().strip() or "新记忆体"
            try:
                new_storage = MemoryStorage.create_unbound_memory(name=name)
                memory_info = new_storage.get_memory_info()
                self.memory_selected.emit("create_unbound", memory_info.get("memory_id"))
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建记忆体失败: {str(e)}")
        
        elif self.bind_local_radio.isChecked():
            current_item = self.local_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "警告", "请选择一个要绑定的记忆体")
                return
            
            memory_data = current_item.data(Qt.UserRole)
            memory_id = memory_data.get("memory_id")
            
            try:
                from src.memory import MemoryStorage as MS
                from pathlib import Path
                path = memory_data.get("path", "")
                storage = MS(db_path=path, crypto=self.crypto, user_id=self.user_id, memory_id=memory_id)
                storage.bind_to_user(self.user_id)
                
                self.memory_selected.emit("bind", memory_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"绑定记忆体失败: {str(e)}")
