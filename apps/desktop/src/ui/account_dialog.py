from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QFrame, QMessageBox, QFormLayout, QRadioButton)
from PySide6.QtCore import Qt
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))

try:
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager
except ImportError:
    import sys
    sys.path.insert(0, PROJECT_ROOT)
    from src.auth.service import AuthService
    from src.crypto.cipher import CryptoManager


class AccountDialog(QDialog):
    login_success = None
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings or {}
        self.auth_service = AuthService(self.settings.get("server_url", "http://api.opentoad.cn"))
        self.session = None
        
        self.setWindowTitle("账号管理")
        self.setMinimumSize(400, 350)
        self.setModal(True)
        
        self.setup_ui()
        self.check_status()
    
    def check_status(self):
        if self.auth_service.is_logged_in:
            self.session = self.auth_service.session
            self.show_logged_in()
        else:
            self.show_login()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                color: #d4d4d4;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #d4d4d4;
            }
            QLineEdit:focus {
                border: 2px solid #0e639c;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QRadioButton {
                color: #d4d4d4;
                font-size: 14px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        layout.addWidget(self.content_frame)
    
    def show_login(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                item.layout().deleteLater()
        
        title = QLabel("🔐 登录 / 注册")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        self.content_layout.addWidget(title)
        
        desc = QLabel("登录后可加密保护您的记忆体数据")
        desc.setStyleSheet("color: #888; font-size: 12px;")
        self.content_layout.addWidget(desc)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("邮箱地址")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("邮箱:", self.email_input)
        form_layout.addRow("密码:", self.password_input)
        self.content_layout.addLayout(form_layout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #f1c40f; font-size: 12px;")
        self.content_layout.addWidget(self.status_label)
        
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.do_login)
        btn_layout.addWidget(login_btn)
        
        register_btn = QPushButton("注册新账号")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        register_btn.clicked.connect(self.do_register)
        btn_layout.addWidget(register_btn)
        
        self.content_layout.addLayout(btn_layout)
        self.content_layout.addStretch()
        
        self.adjustSize()
    
    def show_logged_in(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                item.layout().deleteLater()
        
        title = QLabel("✅ 已登录")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        self.content_layout.addWidget(title)
        
        email_label = QLabel(f"邮箱: {self.session.email}")
        email_label.setStyleSheet("color: #d4d4d4; font-size: 14px;")
        self.content_layout.addWidget(email_label)
        
        user_id_label = QLabel(f"用户ID: {self.session.user_id}")
        user_id_label.setStyleSheet("color: #888; font-size: 12px;")
        self.content_layout.addWidget(user_id_label)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #f1c40f; font-size: 12px;")
        self.content_layout.addWidget(self.status_label)
        
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        logout_btn = QPushButton("退出登录")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b3a3a;
            }
            QPushButton:hover {
                background-color: #a04545;
            }
        """)
        logout_btn.clicked.connect(self.do_logout)
        btn_layout.addWidget(logout_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        self.content_layout.addLayout(btn_layout)
        self.content_layout.addStretch()
        
        self.adjustSize()
    
    def do_login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            self.status_label.setText("请输入邮箱和密码")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.status_label.setText("登录中...")
        self.status_label.setStyleSheet("color: #f1c40f; font-size: 12px;")
        
        try:
            result = self.auth_service.login(email, password)
            if result:
                self.session = self.auth_service.session
                self.login_success = self.session
                self.status_label.setText("登录成功！")
                self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
                self.accept()
            else:
                self.status_label.setText("登录失败，请检查邮箱和密码")
                self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
        except Exception as e:
            self.status_label.setText(f"登录失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def do_register(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            self.status_label.setText("请输入邮箱和密码")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
            return
        
        self.status_label.setText("注册中...")
        self.status_label.setStyleSheet("color: #f1c40f; font-size: 12px;")
        
        try:
            result = self.auth_service.register(email, password)
            if result:
                self.session = self.auth_service.session
                self.login_success = self.session
                self.status_label.setText("注册成功并已登录！")
                self.status_label.setStyleSheet("color: #4ec9b0; font-size: 12px;")
                self.accept()
            else:
                self.status_label.setText("注册失败，请重试")
                self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
        except Exception as e:
            self.status_label.setText(f"注册失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f14c4c; font-size: 12px;")
    
    def do_logout(self):
        self.auth_service.logout()
        self.session = None
        self.login_success = None
        self.show_login()
        # 通知主窗口登出完成
        self.done(QDialog.DialogCode.Rejected)
