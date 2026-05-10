import sys
import os

# 设置路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# 启动应用
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication(sys.argv)
app.setApplicationName("OpenToad")
app.setApplicationVersion("1.0.0")

window = MainWindow()
window.show()

sys.exit(app.exec())