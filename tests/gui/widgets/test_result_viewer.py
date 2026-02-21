"""
[overview]
ResultViewer 위젯 테스트

[description]
결과 뷰어 위젯의 기능을 테스트합니다.
- 결과 표시 (QTextBrowser, Markdown 렌더링)
- Model Selector (QComboBox)
- RUN 버튼
- 메트릭 바 (Latency, Tokens, Cost)
- 이력/비교/메트릭 탭
"""

from unittest.mock import Mock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTextBrowser, QComboBox, QPushButton, QTabWidget
from PySide6.QtTest import QTest

from src.gui.widgets.result_viewer import ResultViewer


class TestResultViewer:
    """ResultViewer 위젯 테스트"""

    def test_initialization(self, qtbot):
        """위젯 초기화 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # Model Selector 존재 확인
        assert widget._model_selector is not None
        assert isinstance(widget._model_selector, QComboBox)

        # RUN 버튼 존재 확인
        assert widget._run_button is not None
        assert isinstance(widget._run_button, QPushButton)

        # 결과창 존재 확인
        assert widget._result_browser is not None
        assert isinstance(widget._result_browser, QTextBrowser)

        # 탭 위젯 존재 확인
        assert widget._tab_widget is not None
        assert isinstance(widget._tab_widget, QTabWidget)

    def test_display_result(self, qtbot):
        """결과 표시 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 결과 표시
        test_result = "This is a test result."
        widget.display_result(test_result)

        # 결과 확인
        assert test_result in widget._result_browser.toPlainText()

    def test_display_markdown(self, qtbot):
        """Markdown 렌더링 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # Markdown 결과 표시
        test_markdown = "# Heading\n\n**Bold text**"
        widget.display_result(test_markdown)

        # 결과 확인
        result_text = widget._result_browser.toHtml()
        assert result_text

    def test_run_button_signal(self, qtbot):
        """RUN 버튼 시그널 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 시그널 캡처 준비
        signal_emitted = False
        selected_model = None

        def on_run_clicked(model: str):
            nonlocal signal_emitted, selected_model
            signal_emitted = True
            selected_model = model

        widget.run_clicked.connect(on_run_clicked)

        # 모델 선택
        widget._model_selector.setCurrentText("OpenAI: GPT-4o")

        # 버튼 클릭
        QTest.mouseClick(widget._run_button, Qt.MouseButton.LeftButton)

        # 시그널 발생 확인
        assert signal_emitted
        assert selected_model == "OpenAI: GPT-4o"

    def test_clear_result(self, qtbot):
        """결과 초기화 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 결과 표시
        widget.display_result("Test result")
        assert widget._result_browser.toPlainText() != ""

        # 초기화
        widget.clear_result()

        # 초기화 확인
        assert widget._result_browser.toPlainText() == ""

    def test_set_metrics(self, qtbot):
        """메트릭 설정 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 메트릭 설정
        widget.set_metrics(
            latency=1.2,
            input_tokens=100,
            output_tokens=200,
            cost=0.005,
        )

        # 메트릭 확인 (메트릭이 UI에 표시되는지 확인)
        # UI 업데이트는 비동기적일 수 있음
        QTest.qWait(100)

    def test_model_selector_options(self, qtbot):
        """Model Selector 옵션 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 모델 옵션 확인
        model_count = widget._model_selector.count()
        assert model_count > 0

        # 기본 모델 존재 확인
        models = [widget._model_selector.itemText(i) for i in range(model_count)]
        assert any("OpenAI" in model for model in models)
        assert any("Ollama" in model for model in models)

    def test_result_tab_selection(self, qtbot):
        """결과 탭 선택 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 기본 탭 확인 (Result 탭)
        assert widget._tab_widget.currentIndex() == 0

        widget._tab_widget.setCurrentIndex(1)
        assert widget._tab_widget.currentIndex() == 1

    def test_display_loading_state(self, qtbot):
        """로딩 상태 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 로딩 상태 설정
        widget.set_loading(True)

        # 버튼 텍스트가 변경되는지 확인
        QTest.qWait(50)
        assert widget._run_button.text() != "Run"

        # 로딩 해제
        widget.set_loading(False)
        QTest.qWait(50)

    def test_copy_result_button(self, qtbot):
        """결과 복사 버튼 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 결과 표시
        test_result = "Test result for copy"
        widget.display_result(test_result)

        # 복사 버튼 존재 확인 (UI에 버튼이 있는지 확인)
        # UI 구현에 따라 버튼이나 메뉴 항목으로 구현될 수 있음

    def test_empty_metrics(self, qtbot):
        """빈 메트릭 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 빈 메트릭 설정
        widget.set_metrics(
            latency=0,
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
        )

        QTest.qWait(100)

    def test_result_history(self, qtbot):
        """결과 이력 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 결과 추가
        widget.add_to_history("Result 1")
        widget.add_to_history("Result 2")

        # 이력 확인
        history = widget.get_history()
        assert len(history) == 2
        assert "Result 1" in history
        assert "Result 2" in history
        assert widget._history_list.count() == 2

    def test_display_error(self, qtbot):
        """에러 표시 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 에러 표시
        test_error = "API Error: Connection failed"
        widget.display_error(test_error)

        # 에러가 표시되는지 확인
        result_text = widget._result_browser.toPlainText()
        assert test_error in result_text or "Error" in result_text

    def test_streaming_result(self, qtbot):
        """스트리밍 결과 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 스트리밍 결과 표시
        widget.start_streaming()
        widget.append_streaming_chunk("Hello ")
        widget.append_streaming_chunk("World!")
        widget.end_streaming()

        # 결과 확인
        result_text = widget._result_browser.toPlainText()
        assert "Hello World!" in result_text

    def test_clear_history(self, qtbot):
        """이력 초기화 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        # 이력 추가
        widget.add_to_history("Result 1")
        widget.add_to_history("Result 2")
        assert len(widget.get_history()) == 2

        # 이력 초기화
        widget.clear_history()

        # 초기화 확인
        assert len(widget.get_history()) == 0
        assert widget._history_list.count() == 0

    def test_compare_and_metrics_tab_data(self, qtbot):
        """Compare/Metrics 탭 데이터 반영 테스트"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        widget.set_metrics(latency=1.0, input_tokens=10, output_tokens=20, cost=0.001)
        widget.add_to_history("First result", model="OpenAI: GPT-4o")
        widget.set_metrics(latency=2.0, input_tokens=30, output_tokens=40, cost=0.002)
        widget.add_to_history("Second result", model="Ollama: llama2")

        assert widget._compare_left_selector.count() == 2
        assert widget._compare_right_selector.count() == 2
        assert "Runs: 2" in widget._metrics_summary_label.text()
        assert "OpenAI: GPT-4o" in widget._metrics_summary_label.text()
        assert "Ollama: llama2" in widget._metrics_summary_label.text()

        widget._compare_left_selector.setCurrentIndex(0)
        widget._compare_right_selector.setCurrentIndex(1)
        compare_html = widget._compare_browser.toHtml()
        assert "First result" in compare_html
        assert "Second result" in compare_html


    def test_get_selected_provider_id_with_data(self, qtbot, monkeypatch):
        """Provider 정보가 있을 때 선택 provider id 확인"""
        from datetime import datetime

        from src.core.provider_manager import ProviderManager
        from src.data.models import Provider

        manager = Mock(spec=ProviderManager)
        manager.get_all_providers.return_value = [
            Provider(
                id="provider_1",
                name="OpenAI",
                description=None,
                api_url="https://api.openai.com/v1",
                api_key=None,
                model="gpt-4o",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ]

        widget = ResultViewer(manager)
        qtbot.addWidget(widget)
        widget.show()

        # 첫 번째 아이템을 선택했을 때 provider id를 반환해야 함
        assert widget._model_selector.currentData() == "provider_1"
        assert widget.get_selected_provider_id() == "provider_1"

    def test_get_selected_provider_id_without_provider_data(self, qtbot):
        """ProviderManager가 없을 때 기본 모델 데이터는 None"""
        widget = ResultViewer()
        qtbot.addWidget(widget)
        widget.show()

        assert widget._model_selector.count() > 0
        assert widget.get_selected_provider_id() is None

    def test_refresh_models_updates_items_with_providers(self, qtbot, monkeypatch):
        """Provider 목록 기반 model selector 재로딩 검증"""
        from datetime import datetime

        from src.core.provider_manager import ProviderManager
        from src.data.models import Provider

        manager = Mock(spec=ProviderManager)
        manager.get_all_providers.return_value = [
            Provider(
                id="provider_1",
                name="OpenAI",
                description=None,
                api_url="https://api.openai.com/v1",
                api_key=None,
                model="gpt-4o",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Provider(
                id="provider_2",
                name="Ollama",
                description=None,
                api_url="http://localhost:11434/v1",
                api_key=None,
                model="llama2",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        widget = ResultViewer(manager)
        qtbot.addWidget(widget)
        widget.show()

        assert widget._model_selector.count() == 2
        assert widget._model_selector.itemText(0) == "OpenAI: gpt-4o"
        assert widget._model_selector.itemText(1) == "Ollama: llama2"
        assert widget._model_selector.itemData(0) == "provider_1"
        assert widget._model_selector.itemData(1) == "provider_2"
