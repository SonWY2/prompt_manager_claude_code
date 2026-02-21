"""
[overview]
main.py 모듈 테스트

[description]
QApplication 초기화 및 애플리케이션 진입점 테스트
"""

import gc
import weakref

from PySide6.QtWidgets import QApplication

# src.gui.main은 테스트 중에 import됨


class TestMain:
    """main.py 모듈 테스트"""

    def test_qapplication_instance_exists(self, qtbot):
        """QApplication 인스턴스가 생성되는지 확인"""
        from src.gui.main import get_app_instance

        app = get_app_instance()
        assert app is not None
        assert isinstance(app, QApplication)

    def test_get_app_instance_singleton(self, qtbot):
        """get_app_instance가 싱글톤인지 확인"""
        from src.gui.main import get_app_instance

        app1 = get_app_instance()
        app2 = get_app_instance()
        assert app1 is app2

    def test_main_window_creation(self, qtbot):
        """메인 윈도우가 생성되는지 확인"""
        from src.gui.main import main

        main_window = main()
        assert main_window is not None
        assert main_window.isVisible() or main_window.windowTitle() == "Prompt Manager"

    def test_application_closes_cleanly(self, qtbot):
        """애플리케이션이 정상적으로 종료되는지 확인"""
        from src.gui.main import main

        main_window = main()
        main_window.close()
        assert not main_window.isVisible()

    def test_qapplication_attributes(self, qtbot):
        """QApplication 속성이 올바르게 설정되는지 확인"""
        from src.gui.main import get_app_instance

        app = get_app_instance()
        # pytest-qt가 생성한 경우 applicationName은 "pytest-qt-qapp"
        assert app.applicationName() in ("Prompt Manager", "pytest-qt-qapp")

    def test_root_main_keeps_window_reference_until_exec(self, monkeypatch):
        import main as root_main

        window_ref_holder: dict[str, weakref.ReferenceType[object]] = {}

        class DummyWindow:
            pass

        class DummyApp:
            def exec(self) -> int:
                gc.collect()
                assert "window_ref" in window_ref_holder
                assert window_ref_holder["window_ref"]() is not None
                return 0

        def create_window() -> DummyWindow:
            window = DummyWindow()
            window_ref_holder["window_ref"] = weakref.ref(window)
            return window

        monkeypatch.setattr(root_main, "create_main_window", create_window)
        monkeypatch.setattr(root_main, "get_app_instance", lambda: DummyApp())

        root_main.main()
