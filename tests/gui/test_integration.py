"""
[overview]
메인 윈도우 통합 테스트

[description]
MainWindow의 기능 연동을 테스트합니다.
- Task Navigator → Prompt Editor → Result Viewer 시그널/슬롯 연동
- 메뉴바/툴바 액션 연결
- 버전 타임라인 드롭다운
- RUN 버튼 기능
- 접기/펴기 기능
"""

from unittest.mock import Mock

import pytest

from PySide6.QtWidgets import QMenu, QToolBar

from src.gui.main_window import MainWindow
from src.data.models import Provider


class TestMainWindowIntegration:
    """MainWindow 통합 테스트"""

    @pytest.fixture
    def main_window(self, qtbot):
        """MainWindow fixture"""
        window = MainWindow()
        qtbot.addWidget(window)
        return window

    def test_main_window_initialization(self, main_window):
        """MainWindow 초기화 테스트"""
        assert main_window.windowTitle() == "Prompt Manager[*]"
        assert main_window.minimumWidth() == 1200
        assert main_window.minimumHeight() == 800

    def test_menu_bar_exists(self, main_window):
        """메뉴바 존재 테스트"""
        menubar = main_window.menuBar()
        assert menubar is not None

        # File 메뉴 확인
        menus = menubar.findChildren(QMenu)
        menu_titles = {menu.title() for menu in menus}
        assert "&File" in menu_titles
        assert "&Edit" in menu_titles
        assert "&View" in menu_titles

    def test_tool_bar_exists(self, main_window):
        """툴바 존재 테스트"""
        toolbar = main_window.findChild(QToolBar)
        assert toolbar is not None

    def test_task_navigator_exists(self, main_window):
        """TaskNavigator 위젯 존재 테스트"""
        from src.gui.widgets.task_navigator import TaskNavigator

        task_navigator = main_window.findChild(TaskNavigator)
        assert task_navigator is not None

    def test_prompt_editor_exists(self, main_window):
        """PromptEditor 위젯 존재 테스트"""
        from src.gui.widgets.prompt_editor import PromptEditor

        prompt_editor = main_window.findChild(PromptEditor)
        assert prompt_editor is not None

    def test_result_viewer_exists(self, main_window):
        """ResultViewer 위젯 존재 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

    def test_task_selection_signal_flow(self, main_window, qtbot):
        """태스크 선택 시그널 플로우 테스트"""
        from src.gui.widgets.task_navigator import TaskNavigator

        task_navigator = main_window.findChild(TaskNavigator)
        assert task_navigator is not None

        # 태스크 추가
        task_id = task_navigator.add_task("Test Task", "1.0", "Test Description")
        assert task_id is not None

        # 태스크 선택
        assert task_navigator.select_task(task_id) is True
        assert task_navigator.get_selected_task_id() == task_id

    def test_run_button_signal(self, main_window, qtbot):
        """RUN 버튼 시그널 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # run_clicked 시그널 스파이
        run_clicked_spy = Mock()
        result_viewer.run_clicked.connect(run_clicked_spy)

        # RUN 버튼 클릭 시뮬레이션
        result_viewer._run_button.click()
        qtbot.wait(100)

        # 시그널 발생 확인
        run_clicked_spy.assert_called_once()

    def test_result_display(self, main_window, qtbot):
        """결과 표시 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 결과 표시
        test_result = "# Test Result\n\nThis is a test result."
        result_viewer.display_result(test_result)
        qtbot.wait(100)

        # 결과 확인
        assert result_viewer._result_browser.toMarkdown().strip() == test_result

    def test_prompt_change_signal(self, main_window, qtbot):
        """프롬프트 변경 시그널 테스트"""
        from src.gui.widgets.prompt_editor import PromptEditor

        prompt_editor = main_window.findChild(PromptEditor)
        assert prompt_editor is not None

        # prompt_changed 시그널 스파이
        prompt_changed_spy = Mock()
        prompt_editor.prompt_changed.connect(prompt_changed_spy)

        # 프롬프트 변경
        prompt_editor.set_system_prompt("Test System Prompt")
        qtbot.wait(100)

        # 시그널 발생 확인
        assert prompt_changed_spy.call_count > 0

    def test_variable_detection(self, main_window):
        """변수 감지 테스트"""
        from src.gui.widgets.prompt_editor import PromptEditor

        prompt_editor = main_window.findChild(PromptEditor)
        assert prompt_editor is not None

        # 변수가 포함된 프롬프트 설정
        prompt_editor.set_user_prompt("Hello {{name}}, today is {{date}}.")
        variables = prompt_editor.detect_variables()

        assert "name" in variables
        assert "date" in variables
        assert len(variables) == 2

    def test_version_management(self, main_window):
        """버전 관리 테스트"""
        from src.gui.widgets.prompt_editor import PromptEditor

        prompt_editor = main_window.findChild(PromptEditor)
        assert prompt_editor is not None

        # 프롬프트 설정
        prompt_editor.set_system_prompt("System v1")
        prompt_editor.set_user_prompt("User v1")

        # 버전 추가
        prompt_editor.add_version("1.0", "Initial version")
        versions = prompt_editor.get_versions()

        assert len(versions) == 1
        assert versions[0]["version"] == "1.0"
        assert versions[0]["system_prompt"] == "System v1"
        assert versions[0]["user_prompt"] == "User v1"

        # 버전 로드
        prompt_editor.set_system_prompt("System v2")
        prompt_editor.set_user_prompt("User v2")
        assert prompt_editor.get_system_prompt() == "System v2"

        prompt_editor.load_version("1.0")
        assert prompt_editor.get_system_prompt() == "System v1"
        assert prompt_editor.get_user_prompt() == "User v1"

    def test_metrics_display(self, main_window):
        """메트릭 표시 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 메트릭 설정
        result_viewer.set_metrics(
            latency=1.5, input_tokens=100, output_tokens=200, cost=0.01
        )

        assert "1.5s" in result_viewer._latency_label.text()
        assert "100" in result_viewer._input_tokens_label.text()
        assert "200" in result_viewer._output_tokens_label.text()
        assert "$0.0100" in result_viewer._cost_label.text()

    def test_loading_state(self, main_window, qtbot):
        """로딩 상태 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 로딩 상태 설정
        result_viewer.set_loading(True)
        assert result_viewer._run_button.text() == "Running..."
        assert result_viewer._run_button.isEnabled() is False

        # 로딩 상태 해제
        result_viewer.set_loading(False)
        assert result_viewer._run_button.text() == "RUN"
        assert result_viewer._run_button.isEnabled() is True

    def test_error_display(self, main_window, qtbot):
        """에러 표시 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 에러 표시
        test_error = "Test error message"
        result_viewer.display_error(test_error)
        qtbot.wait(100)

        # 에러 확인
        html_content = result_viewer._result_browser.toHtml()
        assert "Error:" in html_content
        assert test_error in html_content

    def test_history_management(self, main_window):
        """이력 관리 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 이력 추가
        result_viewer.add_to_history("Result 1")
        result_viewer.add_to_history("Result 2")

        history = result_viewer.get_history()
        assert len(history) == 2
        assert history[0] == "Result 1"
        assert history[1] == "Result 2"

        # 이력 초기화
        result_viewer.clear_history()
        assert len(result_viewer.get_history()) == 0

    def test_task_search(self, main_window):
        """태스크 검색 테스트"""
        from src.gui.widgets.task_navigator import TaskNavigator

        task_navigator = main_window.findChild(TaskNavigator)
        assert task_navigator is not None

        # 태스크 추가
        task_navigator.add_task("Python Task", "1.0")
        task_navigator.add_task("JavaScript Task", "1.0")
        task_navigator.add_task("Task Manager", "1.0")

        # 검색어 설정
        task_navigator._search_bar.setText("Python")

        # 검색 결과 확인 (숨겨진 항목 확인 필요)
        # 실제 검색 로직은 _on_search_changed 메서드에서 처리

    def test_model_selector(self, main_window):
        """모델 선택기 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 모델 개수 확인
        model_count = result_viewer._model_selector.count()
        assert model_count > 0

        # 모델 선택
        initial_model = result_viewer._model_selector.currentText()
        assert initial_model is not None

    def test_streaming_functionality(self, main_window):
        """스트리밍 기능 테스트"""
        from src.gui.widgets.result_viewer import ResultViewer

        result_viewer = main_window.findChild(ResultViewer)
        assert result_viewer is not None

        # 스트리밍 시작
        result_viewer.start_streaming()
        assert result_viewer._is_streaming is True

        # 스트리밍 청크 추가
        result_viewer.append_streaming_chunk("Hello ")
        result_viewer.append_streaming_chunk("World!")
        result_viewer.end_streaming()

        # 스트리밍 종료 확인
        assert result_viewer._is_streaming is False
        assert "Hello World!" in result_viewer._result_browser.toPlainText()

    def test_clear_functionality(self, main_window):
        """초기화 기능 테스트"""
        from src.gui.widgets.prompt_editor import PromptEditor
        from src.gui.widgets.result_viewer import ResultViewer

        prompt_editor = main_window.findChild(PromptEditor)
        result_viewer = main_window.findChild(ResultViewer)

        assert prompt_editor is not None
        assert result_viewer is not None

        # 프롬프트 설정 및 초기화
        prompt_editor.set_system_prompt("Test")
        prompt_editor.set_user_prompt("Test")
        assert prompt_editor.get_system_prompt() == "Test"

        prompt_editor.clear_prompts()
        assert prompt_editor.get_system_prompt() == ""
        assert prompt_editor.get_user_prompt() == ""

        # 결과 설정 및 초기화
        result_viewer.display_result("Test Result")
        assert len(result_viewer._result_browser.toMarkdown()) > 0

        result_viewer.clear_result()
        assert len(result_viewer._result_browser.toMarkdown()) == 0

    def test_run_uses_variable_rendering(self, main_window, monkeypatch):
        """RUN 시 변수 치환 후 LLM 호출되는지 테스트"""

        captured_prompt = {"value": ""}

        class FakeLLMService:
            def __init__(self, provider):
                self.provider = provider

            def call_llm(self, prompt: str):
                captured_prompt["value"] = prompt
                return {
                    "output": "ok",
                    "execution_time_ms": 120,
                    "tokens_used": 12,
                }

        provider = Provider(
            id="provider_1",
            name="Mock Provider",
            description="",
            api_url="https://example.com/v1",
            api_key="",
            model="mock-model",
        )

        monkeypatch.setattr("src.gui.prompt_runner.LLMService", FakeLLMService)
        monkeypatch.setattr(
            main_window._provider_manager, "get_provider", lambda _: provider
        )

        main_window._current_task_id = "task_test"
        main_window._result_viewer._model_selector.clear()
        main_window._result_viewer._model_selector.addItem(
            "Mock Provider: mock-model", "provider_1"
        )

        main_window._prompt_editor.set_system_prompt("System {{name}}")
        main_window._prompt_editor.set_user_prompt("User from {{city}}")

        table = main_window._prompt_editor._variables_table
        for row in range(table.rowCount()):
            key_item = table.item(row, 0)
            if key_item is None:
                continue
            if key_item.text() == "name":
                value_item = table.item(row, 1)
                if value_item is not None:
                    value_item.setText("Alice")
            if key_item.text() == "city":
                value_item = table.item(row, 1)
                if value_item is not None:
                    value_item.setText("Seoul")

        main_window._on_run_clicked("Mock Provider: mock-model")

        assert "System Alice" in captured_prompt["value"]
        assert "User from Seoul" in captured_prompt["value"]
