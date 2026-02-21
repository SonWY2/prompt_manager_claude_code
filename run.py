"""
[overview]
Prompt Manager 애플리케이션 진입점

[description]
PySide6 기반 애플리케이션을 시작하는 메인 진입점입니다.
"""

import sys

from PySide6.QtWidgets import QApplication


def main() -> None:
    """애플리케이션 메인 함수"""
    app = QApplication(sys.argv)
    from src.gui.main_window import MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
