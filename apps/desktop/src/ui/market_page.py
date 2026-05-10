from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QGroupBox, QLineEdit, QSpinBox, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QFormLayout, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QFont
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.client.market_client import MarketApiClient


class MarketWorker(QThread):
    finished = Signal(object)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, action, data=None):
        super().__init__()
        self.action = action
        self.data = data
    
    def run(self):
        try:
            client = MarketApiClient()
            
            if self.action == 'balance':
                result = client.get_balance(self.data.get('user_id'))
                self.finished.emit(result)
            elif self.action == 'deposit':
                result = client.deposit(self.data.get('user_id'), self.data.get('api_key'))
                self.finished.emit(result)
            elif self.action == 'rates':
                result = client.get_rates()
                self.finished.emit(result)
            elif self.action == 'wallet':
                result = client.get_ai_wallet(
                    self.data.get('assistant_id'),
                    self.data.get('user_id')
                )
                self.finished.emit(result)
            elif self.action == 'transfer':
                result = client.transfer_to_ai(
                    self.data.get('user_id'),
                    self.data.get('assistant_id'),
                    self.data.get('amount')
                )
                self.finished.emit(result)
            elif self.action == 'products':
                result = client.list_products(self.data.get('platform'))
                self.finished.emit(result)
            elif self.action == 'buy':
                result = client.purchase(
                    self.data.get('wallet_id'),
                    self.data.get('product_id'),
                    self.data.get('amount')
                )
                self.finished.emit(result)
            elif self.action == 'my_products':
                result = client.list_my_products(self.data.get('seller_id'))
                self.finished.emit(result)
            elif self.action == 'add_product':
                result = client.add_product(
                    self.data.get('seller_id'),
                    self.data.get('platform'),
                    self.data.get('api_key'),
                    self.data.get('name'),
                    self.data.get('description'),
                    self.data.get('price')
                )
                self.finished.emit(result)
            elif self.action == 'remove_product':
                result = client.remove_product(self.data.get('product_id'))
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MarketPage(QWidget):
    def __init__(self, session=None):
        super().__init__()
        self.session = session
        self._worker = None
        self._setup_ui()
    
    def closeEvent(self, event):
        # 停止所有 worker 线程
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait()
        super().closeEvent(event)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background-color: #1e1e1e; }
            QTabBar::tab { background-color: #252526; color: #d4d4d4; padding: 10px 20px; border: none; }
            QTabBar::tab:selected { background-color: #4ec9b0; color: #1a1a1a; font-weight: 600; }
            QTabBar::tab:hover { background-color: #3c3c3c; }
        """)
        
        tabs.addTab(self._create_token_tab(), "Token")
        tabs.addTab(self._create_wallet_tab(), "钱包")
        tabs.addTab(self._create_market_tab(), "市场")
        tabs.addTab(self._create_sell_tab(), "售卖")
        
        layout.addWidget(tabs)
    
    def _create_token_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("Token 管理")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        deposit_group = QGroupBox("Token 充值")
        deposit_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        deposit_layout = QFormLayout(deposit_group)
        
        self.deposit_user_id = QLineEdit()
        self.deposit_user_id.setPlaceholderText("输入用户ID")
        deposit_layout.addRow("用户ID:", self.deposit_user_id)
        
        self.deposit_api_key = QLineEdit()
        self.deposit_api_key.setPlaceholderText("输入 API Key")
        self.deposit_api_key.setEchoMode(QLineEdit.Password)
        deposit_layout.addRow("API Key:", self.deposit_api_key)
        
        deposit_btn = QPushButton("充值")
        deposit_btn.clicked.connect(self._do_deposit)
        deposit_layout.addRow("", deposit_btn)
        
        layout.addWidget(deposit_group)
        
        rates_group = QGroupBox("汇率")
        rates_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        rates_layout = QVBoxLayout(rates_group)
        
        self.rates_label = QLabel("加载中...")
        self.rates_label.setStyleSheet("color: #d4d4d4; padding: 10px;")
        rates_layout.addWidget(self.rates_label)
        
        refresh_rates_btn = QPushButton("刷新汇率")
        refresh_rates_btn.clicked.connect(self._refresh_rates)
        rates_layout.addWidget(refresh_rates_btn)
        
        layout.addWidget(rates_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_wallet_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("AI 钱包")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        # 钱包查询
        wallet_group = QGroupBox("钱包信息")
        wallet_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        wallet_layout = QFormLayout(wallet_group)
        
        self.wallet_user_id = QLineEdit()
        self.wallet_user_id.setPlaceholderText("用户ID")
        wallet_layout.addRow("用户ID:", self.wallet_user_id)
        
        self.wallet_assistant_id = QLineEdit()
        self.wallet_assistant_id.setPlaceholderText("AI助手ID")
        wallet_layout.addRow("AI助手ID:", self.wallet_assistant_id)
        
        query_btn = QPushButton("查询钱包")
        query_btn.clicked.connect(self._query_wallet)
        wallet_layout.addRow("", query_btn)
        
        self.wallet_info_label = QLabel("请输入查询信息")
        self.wallet_info_label.setStyleSheet("color: #888; padding: 10px;")
        wallet_layout.addRow("钱包状态:", self.wallet_info_label)
        
        layout.addWidget(wallet_group)
        
        # 转账
        transfer_group = QGroupBox("转账")
        transfer_group.setStyleSheet(wallet_group.styleSheet())
        transfer_layout = QFormLayout(transfer_group)
        
        self.transfer_user_id = QLineEdit()
        self.transfer_user_id.setPlaceholderText("用户ID")
        transfer_layout.addRow("用户ID:", self.transfer_user_id)
        
        self.transfer_assistant_id = QLineEdit()
        self.transfer_assistant_id.setPlaceholderText("AI助手ID")
        transfer_layout.addRow("AI助手ID:", self.transfer_assistant_id)
        
        self.transfer_amount = QSpinBox()
        self.transfer_amount.setRange(1, 999999)
        self.transfer_amount.setSuffix(" Token")
        transfer_layout.addRow("数量:", self.transfer_amount)
        
        transfer_btn = QPushButton("转账到AI钱包")
        transfer_btn.clicked.connect(self._do_transfer)
        transfer_layout.addRow("", transfer_btn)
        
        layout.addWidget(transfer_group)
        
        layout.addStretch()
        return widget
    
    def _create_market_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("市场")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        label = QLabel("市场功能开发中...")
        label.setStyleSheet("color: #888; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def _create_sell_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        
        header = QLabel("售卖")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        label = QLabel("售卖功能开发中...")
        label.setStyleSheet("color: #888; padding: 20px;")
        layout.addWidget(label)
        
        return widget
        
        # 转账
        transfer_group = QGroupBox("转账")
        transfer_layout = QFormLayout(transfer_group)
        
        self.transfer_user_id = QLineEdit()
        self.transfer_user_id.setPlaceholderText("用户ID")
        transfer_layout.addRow("用户ID:", self.transfer_user_id)
        
        self.transfer_to = QLineEdit()
        self.transfer_to.setPlaceholderText("目标AI助手ID")
        transfer_layout.addRow("转至:", self.transfer_to)
        
        self.transfer_amount = QSpinBox()
        self.transfer_amount.setRange(1, 999999999)
        self.transfer_amount.setValue(1000)
        transfer_layout.addRow("数量:", self.transfer_amount)
        
        transfer_btn = QPushButton("发起转账")
        transfer_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        transfer_btn.clicked.connect(self._do_transfer)
        transfer_layout.addRow("", transfer_btn)
        
        layout.addWidget(transfer_group)
        
        layout.addStretch()
        return widget
    
    def _create_market_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("API 市场")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        # 产品筛选
        filter_layout = QHBoxLayout()
        
        self.platform_filter = QComboBox()
        self.platform_filter.addItems(["全部", "openai", "anthropic", "deepseek", "google"])
        filter_layout.addWidget(QLabel("平台:"))
        filter_layout.addWidget(self.platform_filter)
        
        refresh_products_btn = QPushButton("刷新")
        refresh_products_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        refresh_products_btn.clicked.connect(self._refresh_products)
        filter_layout.addWidget(refresh_products_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 产品表格
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["ID", "名称", "平台", "价格", "状态"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 8px;
                border: none;
            }
        """)
        layout.addWidget(self.products_table)
        
        # 购买
        buy_group = QGroupBox("购买")
        buy_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        buy_layout = QFormLayout(buy_group)
        
        self.buy_wallet_id = QLineEdit()
        self.buy_wallet_id.setPlaceholderText("钱包ID")
        buy_layout.addRow("钱包ID:", self.buy_wallet_id)
        
        self.buy_product_id = QSpinBox()
        self.buy_product_id.setRange(1, 999999)
        buy_layout.addRow("产品ID:", self.buy_product_id)
        
        self.buy_amount = QSpinBox()
        self.buy_amount.setRange(1, 999999999)
        self.buy_amount.setValue(1000000)
        buy_layout.addRow("数量:", self.buy_amount)
        
        buy_btn = QPushButton("购买")
        buy_btn.clicked.connect(self._do_buy)
        buy_layout.addRow("", buy_btn)
        
        layout.addWidget(buy_group)
        
        self._refresh_products()
        
        return widget
    
    def _create_sell_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        header = QLabel("API 售卖")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #4ec9b0;")
        layout.addWidget(header)
        
        # 上架
        add_group = QGroupBox("上架新 API")
        add_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        add_layout = QFormLayout(add_group)
        
        self.sell_platform = QComboBox()
        self.sell_platform.addItems(["openai", "anthropic", "deepseek", "google", "qianwen"])
        add_layout.addRow("平台:", self.sell_platform)
        
        self.sell_api_key = QLineEdit()
        self.sell_api_key.setPlaceholderText("API Key")
        self.sell_api_key.setEchoMode(QLineEdit.Password)
        add_layout.addRow("API Key:", self.sell_api_key)
        
        self.sell_name = QLineEdit()
        self.sell_name.setPlaceholderText("产品名称")
        add_layout.addRow("名称:", self.sell_name)
        
        self.sell_description = QLineEdit()
        self.sell_description.setPlaceholderText("产品描述")
        add_layout.addRow("描述:", self.sell_description)
        
        self.sell_price = QSpinBox()
        self.sell_price.setRange(1, 999999)
        self.sell_price.setValue(100)
        self.sell_price.setSuffix(" TOAD/1M")
        add_layout.addRow("价格:", self.sell_price)
        
        self.sell_seller_id = QLineEdit()
        self.sell_seller_id.setPlaceholderText("卖家ID")
        add_layout.addRow("卖家ID:", self.sell_seller_id)
        
        add_btn = QPushButton("上架")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        add_btn.clicked.connect(self._do_add_product)
        add_layout.addRow("", add_btn)
        
        layout.addWidget(add_group)
        
        # 我的产品
        my_products_group = QGroupBox("我的产品")
        my_products_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 12px;
                color: #4ec9b0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #4ec9b0;
                color: #1a1a1a;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5fd9be;
            }
        """)
        my_products_layout = QVBoxLayout(my_products_group)
        
        seller_layout = QHBoxLayout()
        self.my_seller_id = QLineEdit()
        self.my_seller_id.setPlaceholderText("卖家ID")
        seller_layout.addWidget(QLabel("卖家ID:"))
        seller_layout.addWidget(self.my_seller_id)
        
        refresh_my_btn = QPushButton("刷新")
        refresh_my_btn.clicked.connect(self._refresh_my_products)
        seller_layout.addWidget(refresh_my_btn)
        seller_layout.addStretch()
        my_products_layout.addLayout(seller_layout)
        
        self.my_products_table = QTableWidget()
        self.my_products_table.setColumnCount(4)
        self.my_products_table.setHorizontalHeaderLabels(["ID", "名称", "平台", "状态"])
        self.my_products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.my_products_table.setStyleSheet("""
            QTableWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 8px;
                border: none;
            }
        """)
        my_products_layout.addWidget(self.my_products_table)
        
        layout.addWidget(my_products_group)
        
        return widget
    
    # Token 操作
    def _refresh_balance(self):
        if not hasattr(self, 'deposit_user_id'):
            return
        user_id = self.deposit_user_id.text() or "default"
        self._worker = MarketWorker('balance', {'user_id': user_id})
        self._worker.finished.connect(self._on_balance_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_balance_loaded(self, result):
        if hasattr(self, 'balance_label') and hasattr(self, 'frozen_label'):
            balance = result.get('balance', 0)
            frozen = result.get('frozen', 0)
            self.balance_label.setText(f"余额: {balance} TOAD")
            self.frozen_label.setText(f"冻结: {frozen} TOAD")
    
    def _do_deposit(self):
        user_id = self.deposit_user_id.text()
        api_key = self.deposit_api_key.text()
        if not user_id or not api_key:
            QMessageBox.warning(self, "提示", "请填写用户ID和API Key")
            return
        self._worker = MarketWorker('deposit', {'user_id': user_id, 'api_key': api_key})
        self._worker.finished.connect(lambda r: self._on_deposit_done(r))
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_deposit_done(self, result):
        QMessageBox.information(self, "成功", f"充值成功! 余额: {result.get('balance', 0)}")
        self._refresh_balance()
    
    def _refresh_rates(self):
        self._worker = MarketWorker('rates', {})
        self._worker.finished.connect(self._on_rates_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_rates_loaded(self, result):
        if hasattr(self, 'rates_label'):
            text = ""
            for platform, rate in result.items():
                text += f"{platform}: 1 TOAD = {rate}\n"
            self.rates_label.setText(text)
    
    # Wallet 操作
    def _query_wallet(self):
        user_id = self.wallet_user_id.text()
        assistant_id = self.wallet_assistant_id.text()
        if not user_id or not assistant_id:
            QMessageBox.warning(self, "提示", "请填写用户ID和AI助手ID")
            return
        self._worker = MarketWorker('wallet', {'user_id': user_id, 'assistant_id': assistant_id})
        self._worker.finished.connect(self._on_wallet_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_wallet_loaded(self, result):
        address = result.get('address', 'N/A')
        balance = result.get('balance', 0)
        frozen = result.get('frozen', 0)
        self.wallet_info_label.setText(f"地址: {address}\n余额: {balance} TOAD\n冻结: {frozen} TOAD")
    
    def _do_transfer(self):
        user_id = self.transfer_user_id.text()
        assistant_id = self.transfer_to.text()
        amount = self.transfer_amount.value()
        if not user_id or not assistant_id:
            QMessageBox.warning(self, "提示", "请填写完整信息")
            return
        self._worker = MarketWorker('transfer', {'user_id': user_id, 'assistant_id': assistant_id, 'amount': amount})
        self._worker.finished.connect(lambda r: QMessageBox.information(self, "成功", "转账成功!"))
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    # Market 操作
    def _refresh_products(self):
        platform = self.platform_filter.currentText()
        if platform == "全部":
            platform = None
        self._worker = MarketWorker('products', {'platform': platform})
        self._worker.finished.connect(self._on_products_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_products_loaded(self, result):
        self.products_table.setRowCount(len(result))
        for i, p in enumerate(result):
            self.products_table.setItem(i, 0, QTableWidgetItem(str(p.get('id', ''))))
            self.products_table.setItem(i, 1, QTableWidgetItem(p.get('name', '')))
            self.products_table.setItem(i, 2, QTableWidgetItem(p.get('platform', '')))
            self.products_table.setItem(i, 3, QTableWidgetItem(str(p.get('pricePer1M', ''))))
            self.products_table.setItem(i, 4, QTableWidgetItem("在售" if p.get('isActive') else "已下架"))
    
    def _do_buy(self):
        wallet_id = self.buy_wallet_id.text()
        product_id = self.buy_product_id.value()
        amount = self.buy_amount.value()
        if not wallet_id:
            QMessageBox.warning(self, "提示", "请填写钱包ID")
            return
        self._worker = MarketWorker('buy', {'wallet_id': wallet_id, 'product_id': product_id, 'amount': amount})
        self._worker.finished.connect(lambda r: QMessageBox.information(self, "成功", f"购买成功! 交易ID: {r.get('id', '')}"))
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    # Sell 操作
    def _refresh_my_products(self):
        seller_id = self.my_seller_id.text()
        if not seller_id:
            QMessageBox.warning(self, "提示", "请填写卖家ID")
            return
        self._worker = MarketWorker('my_products', {'seller_id': seller_id})
        self._worker.finished.connect(self._on_my_products_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_my_products_loaded(self, result):
        self.my_products_table.setRowCount(len(result))
        for i, p in enumerate(result):
            self.my_products_table.setItem(i, 0, QTableWidgetItem(str(p.get('id', ''))))
            self.my_products_table.setItem(i, 1, QTableWidgetItem(p.get('name', '')))
            self.my_products_table.setItem(i, 2, QTableWidgetItem(p.get('platform', '')))
            self.my_products_table.setItem(i, 3, QTableWidgetItem("在售" if p.get('isActive') else "已下架"))
    
    def _do_add_product(self):
        platform = self.sell_platform.currentText()
        api_key = self.sell_api_key.text()
        name = self.sell_name.text()
        description = self.sell_description.text()
        price = self.sell_price.value()
        seller_id = self.sell_seller_id.text()
        
        if not all([api_key, name, seller_id]):
            QMessageBox.warning(self, "提示", "请填写完整信息")
            return
        
        self._worker = MarketWorker('add_product', {
            'platform': platform,
            'api_key': api_key,
            'name': name,
            'description': description,
            'price': price,
            'seller_id': seller_id
        })
        self._worker.finished.connect(lambda r: QMessageBox.information(self, "成功", f"上架成功! 产品ID: {r.get('id', '')}"))
        self._worker.error.connect(self._on_error)
        self._worker.start()
    
    def _on_error(self, error):
        QMessageBox.critical(self, "错误", f"操作失败: {error}")