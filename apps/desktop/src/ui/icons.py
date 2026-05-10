"""
OpenToad Icon System - Simple text-based icons
"""
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

def get_icon(name: str, size: int = 24) -> QIcon:
    """Get icon by name - simple text based"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 简单的文本图标
    color = QColor("#4ec9b0")
    font = QFont("Arial")
    font.setPixelSize(size * 0.6)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(color)
    
    # 根据名称返回不同的符号
    symbols = {
        "settings": "⚙",
        "market": "🛒",
        "user": "👤",
        "send": "➤",
        "plus": "+",
        "frog": "🐸",
        "llm": "✨",
        "chat": "💬",
        "memory": "🧠",
        "close": "✕",
        "minimize": "─",
        "maximize": "□",
        "restore": "❐",
    }
    
    symbol = symbols.get(name, "●")
    painter.drawText(pixmap.rect(), Qt.AlignCenter, symbol)
    
    painter.end()
    return QIcon(pixmap)

class IconCache:
    """Simple cache for icons"""
    _cache = {}
    
    @classmethod
    def get(cls, name: str, size: int = 24) -> QIcon:
        key = f"{name}_{size}"
        if key not in cls._cache:
            cls._cache[key] = get_icon(name, size)
        return cls._cache[key]