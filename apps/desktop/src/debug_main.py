import sys
import os
import traceback

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Starting OpenToad Desktop...")

def exception_hook(exc_type, exc_value, exc_traceback):
    print(f"UNHANDLED EXCEPTION: {exc_type}: {exc_value}")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    input("Press Enter to exit...")

sys.excepthook = exception_hook

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    print("Qt imports OK")
    
    from ui.main_window import MainWindow
    print("MainWindow import OK")
    
    app = QApplication(sys.argv)
    print("QApplication created")
    
    app.setApplicationName("OpenToad")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    print("MainWindow created")
    
    window.show()
    print("Window shown, starting event loop...")
    
    exit_code = app.exec()
    print(f"Event loop exited with code: {exit_code}")
    sys.exit(exit_code)
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
    input("Press Enter to exit...")
