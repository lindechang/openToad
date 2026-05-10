import sys
import os
from pathlib import Path

# 设置工作目录
os.chdir(Path(__file__).parent.parent.parent)

# 设置路径
root = Path.cwd()
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# 忽略警告
import warnings
warnings.filterwarnings('ignore')

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication([])
window = MainWindow()
window.show()
app.exec()