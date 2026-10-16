import sys
from PySide6.QtWidgets import QApplication
from image_processor.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Лаб3 Куделко")
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1:
        window.open_path(sys.argv[1])
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
