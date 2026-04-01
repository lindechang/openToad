from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QMessageBox, QScrollArea, QGroupBox, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal
import os
from pathlib import Path
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager
    from src.memory import MemoryStorage, MemoryCore
except ImportError:
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager
    from src.memory import MemoryStorage, MemoryCore


class MemoryBindWorker(QThread):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, action, data=None):
        super().__init__()
        self.action = action
        self.data = data
    
    def run(self):
        try:
            if self.action == 'check':
                result = self._check_memory_status()
                self.finished.emit(result)
            elif self.action == 'bind':
                self._do_bind()
                self.finished.emit("绑定成功")
            elif self.action == 'unlock':
                self._do_unlock()
                self.finished.emit("解锁成功")
            elif self.action == 'reset':
                self._do_reset()
                self.finished.emit("重置完成")
        except Exception as e:
            self.error.emit(str(e))
    
    def _get_memory_path(self):
        home = Path.home()
        return home / ".opentoad" / "memory.db"
    
    def _get_meta_path(self):
        home = Path.home()
        return home / ".opentoad" / "memory.meta"
    
    def _get_plain_path(self):
        return self._get_memory_path().with_suffix('.db.plain')
    
    def _check_memory_status(self):
        memory_path = self._get_memory_path()
        plain_path = self._get_plain_path()
        meta_path = self._get_meta_path()
        
        result = {
            'memory_path': str(memory_path),
            'exists': memory_path.exists() or plain_path.exists(),
            'size': memory_path.stat().st_size if memory_path.exists() else (plain_path.stat().st_size if plain_path.exists() else 0),
            'is_encrypted': False,
            'is_bound': False,
            'bound_user': None,
            'bound_email': None,
            'can_access': True,
            'hidden': False,
            'plain_exists': plain_path.exists(),
            'reason': ''
        }
        
        if memory_path.exists() and not plain_path.exists():
            result['is_encrypted'] = True
            if meta_path.exists():
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        result['bound_user'] = meta.get('user_id')
                        result['bound_email'] = meta.get('email')
                        result['is_bound'] = True
                except:
                    pass
            
            result['can_access'] = False
            result['hidden'] = True
            result['reason'] = '已被其他账号加密'
            result['exists'] = False
        elif plain_path.exists():
            result['is_bound'] = True
            result['is_encrypted'] = True
            if meta_path.exists():
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        result['bound_user'] = meta.get('user_id')
                        result['bound_email'] = meta.get('email')
                except:
                    pass
        elif memory_path.exists():
            result['is_encrypted'] = True
            result['can_access'] = False
            result['hidden'] = True
            result['reason'] = '已被其他账号加密'
            result['exists'] = False
        
        return result
    
    def _do_bind(self):
        if not self.data:
            return
        
        session = self.data
        memory_path = self._get_memory_path()
        plain_path = self._get_plain_path()
        meta_path = self._get_meta_path()
        
        crypto = CryptoManager(session.encryption_key)
        
        self.progress.emit("正在加密记忆体...")
        
        if plain_path.exists():
            crypto.encrypt_file(str(plain_path), str(memory_path))
        elif memory_path.exists():
            if meta_path.exists():
                with open(meta_path, 'r') as f:
                    meta = json.load(f)
                    bound_user = meta.get('user_id')
                    if bound_user and bound_user != session.user_id:
                        raise ValueError(f"该记忆体已被账号 {meta.get('email', '其他用户')} 绑定，无法重新绑定")
            
            temp_path = self._get_memory_path().parent / "temp_decrypt.db"
            try:
                crypto.decrypt_file(str(memory_path), str(temp_path))
                crypto.encrypt_file(str(temp_path), str(memory_path))
            finally:
                if temp_path.exists():
                    temp_path.unlink()
        
        meta = {
            'user_id': session.user_id,
            'email': session.email,
            'bound_at': str(Path(memory_path).stat().st_mtime)
        }
        with open(meta_path, 'w') as f:
            json.dump(meta, f)
    
    def _do_unlock(self):
        if not self.data:
            return
        
        session = self.data
        memory_path = self._get_memory_path()
        plain_path = self._get_plain_path()
        meta_path = self._get_meta_path()
        
        crypto = CryptoManager(session.encryption_key)
        
        self.progress.emit("正在解密...")
        
        crypto.decrypt_file(str(memory_path), str(plain_path))
        
        if meta_path.exists():
            meta_path.unlink()
    
    def _do_reset(self):
        self.progress.emit("正在重置...")
        
        memory_path = self._get_memory_path()
        plain_path = self._get_plain_path()
        meta_path = self._get_meta_path()
        
        if memory_path.exists():
            memory_path.unlink()
        if plain_path.exists():
            plain_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        
        self.progress.emit("正在创建新记忆体...")
        
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        storage = MemoryStorage()
        from src.memory.types import MemoryItem, MemoryCategory
        from datetime import datetime
        item = MemoryItem(
            id='init',
            content='记忆体重置完成，等待命名...',
            category=MemoryCategory.SYSTEM,
            weight=1.0,
            is_long_term=True,
            source='system',
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            metadata={}
        )
        storage.save_memory(item)


class MemoryBindPanel(QWidget):
    reset_complete = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session = None
        self.memory_status = None
        self.setup_ui()
    
    def set_session(self, session):
        self.session = session
        self._refresh_status()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("📦 记忆体管理")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4ec9b0; padding-bottom: 10px;")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        
        self._create_status_card(container_layout)
        self._create_action_card(container_layout)
        
        container_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
    
    def _create_status_card(self, parent_layout):
        self.status_card = QFrame()
        self.status_card.setStyleSheet("""
            QFrame {
                background-color: #2d3d4a;
                border: 1px solid #4ec9b0;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(self.status_card)
        card_layout.setSpacing(10)
        
        title = QLabel("📋 记忆体状态")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        card_layout.addWidget(title)
        
        self.status_icon = QLabel("⏳")
        self.status_icon.setStyleSheet("font-size: 48px;")
        
        self.status_text = QLabel("正在检查...")
        self.status_text.setStyleSheet("font-size: 14px; color: #ffffff;")
        
        self.status_detail = QLabel("")
        self.status_detail.setStyleSheet("font-size: 12px; color: #aaaaaa;")
        
        card_layout.addWidget(self.status_icon, 0, Qt.AlignCenter)
        card_layout.addWidget(self.status_text, 0, Qt.AlignCenter)
        card_layout.addWidget(self.status_detail, 0, Qt.AlignCenter)
        
        parent_layout.addWidget(self.status_card)
    
    def _create_action_card(self, parent_layout):
        self.action_card = QFrame()
        self.action_card.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(self.action_card)
        layout.setSpacing(12)
        
        title = QLabel("🔧 操作")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(title)
        
        self.action_desc = QLabel("")
        self.action_desc.setStyleSheet("color: #888; font-size: 13px;")
        layout.addWidget(self.action_desc)
        
        btn_layout = QHBoxLayout()
        self.action_btn = QPushButton()
        self.action_btn.clicked.connect(self._do_action)
        btn_layout.addWidget(self.action_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        self.reset_btn = QPushButton("🗑️ 重置记忆体")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.reset_btn.clicked.connect(self._do_reset)
        reset_layout = QHBoxLayout()
        reset_layout.addWidget(self.reset_btn)
        reset_layout.addStretch()
        layout.addLayout(reset_layout)
        
        self.reset_warning = QLabel("⚠️ 重置将清空所有记忆，且无法恢复！")
        self.reset_warning.setStyleSheet("color: #f14c4c; font-size: 11px;")
        layout.addWidget(self.reset_warning)
        
        self.action_status = QLabel("")
        self.action_status.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.action_status)
        
        parent_layout.addWidget(self.action_card)
    
    def _refresh_status(self):
        self.worker = MemoryBindWorker('check')
        self.worker.finished.connect(self._on_status_loaded)
        self.worker.error.connect(self._on_status_error)
        self.worker.start()
    
    def _on_status_loaded(self, status):
        self.memory_status = status
        self._update_ui()
    
    def _on_status_error(self, error):
        self.status_icon.setText("❌")
        self.status_text.setText("检查失败")
        self.status_detail.setText(error)
        self.status_detail.setStyleSheet("font-size: 12px; color: #f14c4c;")
    
    def _update_ui(self):
        if not self.memory_status:
            return
        
        s = self.memory_status
        
        if s.get('hidden', False):
            self.status_icon.setText("📭")
            self.status_text.setText("暂无记忆体")
            self.status_detail.setText("开始对话后将自动创建")
            self.action_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            return
        
        self.reset_btn.setEnabled(True)
        size_kb = s['size'] / 1024 if s['size'] > 0 else 0
        
        if not self.session:
            if s['exists']:
                self.status_icon.setText("📁")
                self.status_text.setText("未绑定记忆体")
                self.status_detail.setText(f"大小: {size_kb:.1f} KB | 未加密")
                self.status_detail.setStyleSheet("font-size: 12px; color: #aaaaaa;")
                self.action_desc.setText("登录账号后将记忆体加密绑定，保护隐私")
                self.action_btn.setText("请先登录账号")
                self.action_btn.setEnabled(False)
            else:
                self.status_icon.setText("📭")
                self.status_text.setText("暂无记忆体")
                self.status_detail.setText("开始对话后将自动创建")
                self.action_btn.setEnabled(False)
        else:
            if s['is_bound'] and s['bound_user'] == self.session.user_id:
                self.status_icon.setText("🔓")
                self.status_text.setText(f"已绑定: {self.session.email}")
                self.status_detail.setText(f"大小: {size_kb:.1f} KB | 已加密 | 属于当前账号")
                self.status_detail.setStyleSheet("font-size: 12px; color: #4ec9b0;")
                self.action_desc.setText("当前账号可以正常访问此记忆体")
                self.action_btn.setText("🔒 重新加密")
                self.action_btn.setEnabled(True)
                self.action_btn.setProperty("action", "rebind")
            elif s['exists']:
                self.status_icon.setText("📁")
                self.status_text.setText("未绑定")
                self.status_detail.setText(f"大小: {size_kb:.1f} KB | 未加密")
                self.action_desc.setText(f"绑定到账号 {self.session.email}，加密保护隐私")
                self.action_btn.setText("🔐 绑定到当前账号")
                self.action_btn.setEnabled(True)
                self.action_btn.setProperty("action", "bind")
            else:
                self.status_icon.setText("📭")
                self.status_text.setText("暂无记忆体")
                self.status_detail.setText("开始对话后将自动创建")
                self.action_btn.setEnabled(False)
    
    def _do_action(self):
        if not self.session or not self.memory_status:
            return
        
        action = self.action_btn.property("action")
        
        if action == "bind":
            self.action_btn.setEnabled(False)
            self.action_btn.setText("绑定中...")
            self.action_status.setText("正在加密...")
            
            self.worker = MemoryBindWorker('bind', self.session)
            self.worker.progress.connect(lambda msg: self.action_status.setText(msg))
            self.worker.finished.connect(self._on_bind_success)
            self.worker.error.connect(self._on_bind_error)
            self.worker.start()
        elif action == "rebind":
            self.action_btn.setEnabled(False)
            self.action_btn.setText("重新加密中...")
            
            self.worker = MemoryBindWorker('bind', self.session)
            self.worker.progress.connect(lambda msg: self.action_status.setText(msg))
            self.worker.finished.connect(self._on_bind_success)
            self.worker.error.connect(self._on_bind_error)
            self.worker.start()
    
    def _on_bind_success(self, msg):
        self.action_status.setText(msg)
        self.action_status.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        QMessageBox.information(self, "绑定成功", "记忆体已成功绑定并加密！")
        self._refresh_status()
    
    def _on_bind_error(self, error):
        self.action_btn.setEnabled(True)
        self.action_btn.setText("🔐 绑定到当前账号")
        self.action_status.setText(f"失败: {error}")
        self.action_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def _do_reset(self):
        if not self.memory_status or not self.memory_status.get('exists'):
            return
        
        if self.memory_status.get('hidden'):
            QMessageBox.warning(self, "无法重置", "该记忆体已被其他账号加密，无法重置")
            return
        
        reply = QMessageBox.question(
            self, "确认重置",
            "⚠️ 重置将清空所有记忆，且无法恢复！\n\n确定要重置记忆体吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.reset_btn.setEnabled(False)
            self.reset_btn.setText("重置中...")
            
            self.worker = MemoryBindWorker('reset')
            self.worker.finished.connect(self._on_reset_success)
            self.worker.error.connect(self._on_reset_error)
            self.worker.start()
    
    def _on_reset_success(self, msg):
        self.reset_btn.setEnabled(True)
        self.reset_btn.setText("🗑️ 重置记忆体")
        self.action_status.setText(msg)
        self.action_status.setStyleSheet("color: #4ec9b0; font-size: 12px;")
        QMessageBox.information(self, "重置成功", "记忆体已重置为初始状态！现在请到对话页面，让我为你命名。")
        self._refresh_status()
        
        self.reset_complete.emit()
    
    def _on_reset_error(self, error):
        self.reset_btn.setEnabled(True)
        self.reset_btn.setText("🗑️ 重置记忆体")
        self.action_status.setText(f"重置失败: {error}")
        self.action_status.setStyleSheet("color: #f14c4c; font-size: 12px;")
