import sys
import os

print("Starting OpenToad Desktop...", flush=True)

sys.path.insert(0, os.getcwd())

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from ui.main_window import MainWindow

    print("Creating QApplication...", flush=True)
    app = QApplication(sys.argv)
    app.setApplicationName("OpenToad")
    app.setApplicationVersion("1.0.0")

    print("Creating MainWindow...", flush=True)
    window = MainWindow()

    print("Showing window...", flush=True)
    window.show()
    window.raise_()
    window.activateWindow()

    print("Entering event loop...", flush=True)
    sys.exit(app.exec())
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")