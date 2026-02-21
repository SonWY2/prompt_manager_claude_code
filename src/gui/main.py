"""
[overview]
애플리케이션 진입점

[description]
QApplication 초기화 및 MainWindow 생성을 담당하는 메인 모듈
"""

from src.gui.qt_platform import configure_qt_platform

configure_qt_platform()

from typing import Optional, cast
from PySide6.QtWidgets import QApplication

from src.gui.main_window import MainWindow

# QApplication 인스턴스 관리 (circular dependency 방지)
_app_instance: Optional[QApplication] = None

# 최소 윈도우 크기 상수
MIN_WINDOW_WIDTH: int = 1200
MIN_WINDOW_HEIGHT: int = 800


def get_app_instance() -> QApplication:
    """QApplication 싱글톤 인스턴스 반환"""
    global _app_instance
    if _app_instance is None:
        # 기존 인스턴스 확인 (pytest-qt 등에서 생성된 경우)
        existing_app = QApplication.instance()
        if existing_app is not None:
            _app_instance = cast(QApplication, existing_app)
        else:
            _app_instance = QApplication([])
    return _app_instance


def main() -> MainWindow:
    """메인 함수: 애플리케이션 초기화 및 메인 윈도우 생성

    Returns:
        MainWindow: 생성된 메인 윈도우 인스턴스
    """
    _ = get_app_instance()

    main_window = MainWindow()
    main_window.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    main_window.resize(1400, 900)
    main_window.show()

    return main_window


if __name__ == "__main__":
    window = main()
    app = QApplication.instance()
    if app is not None:
        app.exec()
