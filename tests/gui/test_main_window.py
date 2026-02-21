"""
[overview]
main_window.py 모듈 테스트

[description]
MainWindow 클래스의 3단 QSplitter 레이아웃과 Modern Dark Mode 테마 테스트
"""

from PySide6.QtWidgets import QSplitter, QWidget
from PySide6.QtCore import Qt


class TestMainWindowLayout:
    """MainWindow 레이아웃 테스트"""

    def test_main_window_creation(self, qtbot):
        """MainWindow가 생성되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        assert window is not None
        assert window.windowTitle() == "Prompt Manager"

    def test_main_splitter_exists(self, qtbot):
        """메인 QSplitter가 존재하는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        central_widget = window.centralWidget()
        assert central_widget is not None
        assert isinstance(central_widget, QSplitter)

    def test_three_column_layout(self, qtbot):
        """3단 컬럼 레이아웃이 구성되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = window.centralWidget()
        assert isinstance(main_splitter, QSplitter)
        assert main_splitter.count() == 3

        # 각 패널 확인
        for i in range(3):
            widget = main_splitter.widget(i)
            assert widget is not None
            assert isinstance(widget, QWidget)

    def test_splitter_orientation_horizontal(self, qtbot):
        """QSplitter가 가로 방향인지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = window.centralWidget()
        assert main_splitter.orientation() == Qt.Orientation.Horizontal

    def test_window_minimum_size(self, qtbot):
        """윈도우 최소 크기가 설정되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        assert window.minimumWidth() > 0
        assert window.minimumHeight() > 0


class TestMainWindowTheme:
    """MainWindow Modern Dark Mode 테마 테스트"""

    def test_main_window_background_color(self, qtbot):
        """메인 윈도우 배경색이 Modern Dark Mode인지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        # 스타일시트에서 배경색 확인
        stylesheet = window.styleSheet()
        assert "background-color" in stylesheet or "#1E1E1E" in stylesheet

    def test_accent_color_applied(self, qtbot):
        """Accent 색상이 적용되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        stylesheet = window.styleSheet()
        # 포인트 블루(#007ACC)가 있는지 확인 (버튼 등에 적용됨)
        assert "#007ACC" in stylesheet or "#2b8cee" in stylesheet

    def test_text_colors_set(self, qtbot):
        """텍스트 색상이 설정되는지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        stylesheet = window.styleSheet()
        # Primary Text(#D4D4D4)와 Secondary Text(#858585)
        assert "#D4D4D4" in stylesheet or "#d4d4d4" in stylesheet


class TestMainWindowPanels:
    """MainWindow 패널 구성 테스트"""

    def test_left_panel_attributes(self, qtbot):
        """좌측 패널(Task Navigator) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = window.centralWidget()
        left_panel = main_splitter.widget(0)

        assert left_panel is not None
        assert isinstance(left_panel, QWidget)

    def test_center_panel_attributes(self, qtbot):
        """중앙 패널(Prompt Editor) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = window.centralWidget()
        center_panel = main_splitter.widget(1)

        assert center_panel is not None
        assert isinstance(center_panel, QWidget)

    def test_right_panel_attributes(self, qtbot):
        """우측 패널(Result Viewer) 속성 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)

        main_splitter = window.centralWidget()
        right_panel = main_splitter.widget(2)

        assert right_panel is not None
        assert isinstance(right_panel, QWidget)

    def test_panels_are_resizable(self, qtbot):
        """패널 크기 조절이 가능한지 확인"""
        from src.gui.main_window import MainWindow

        window = MainWindow()
        qtbot.addWidget(window)
        window.show()

        main_splitter = window.centralWidget()

        # QSplitter의 크기 조절 기능 확인
        assert main_splitter.handle(1).isEnabled()
        assert main_splitter.handle(2).isEnabled()
