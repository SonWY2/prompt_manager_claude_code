"""
[overview]
루트 실행 진입점

[description]
`python main.py` 실행 시 Prompt Manager GUI를 시작합니다.
"""

from src.gui.main import get_app_instance, main as create_main_window


def main() -> None:
    _window = create_main_window()
    app = get_app_instance()
    app.exec()


if __name__ == "__main__":
    main()
