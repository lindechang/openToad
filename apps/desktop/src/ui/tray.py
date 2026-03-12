from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon

class TrayIcon:
    def __init__(self, parent):
        self.tray = QSystemTrayIcon(parent)
        self.tray.setToolTip("OpenToad")
        self.tray.activated.connect(parent.show)
