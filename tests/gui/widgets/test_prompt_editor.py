"""
[overview]
PromptEditor 위젯 테스트

[description]
프롬프트 에디터 위젯의 기능을 테스트합니다.
- System Prompt 표시
- User Prompt 표시
- 변수 감지 ({{variable}})
- 버전 타임라인
"""

from PySide6.QtWidgets import QPlainTextEdit, QTabWidget
from PySide6.QtTest import QTest

from src.gui.widgets.prompt_editor import PromptEditor
from src.gui.widgets.prompt_highlighter import VariableSyntaxHighlighter


class TestPromptEditor:
    """PromptEditor 위젯 테스트"""

    def test_initialization(self, qtbot):
        """위젯 초기화 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # System Prompt 존재 확인
        assert widget._system_prompt_edit is not None
        assert isinstance(widget._system_prompt_edit, QPlainTextEdit)

        # User Prompt 존재 확인
        assert widget._user_prompt_edit is not None
        assert isinstance(widget._user_prompt_edit, QPlainTextEdit)

        # 탭 위젯 존재 확인
        assert widget._tab_widget is not None
        assert isinstance(widget._tab_widget, QTabWidget)

    def test_system_prompt_editing(self, qtbot):
        """System Prompt 편집 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # System Prompt 입력
        test_text = "You are a helpful assistant."
        widget._system_prompt_edit.setPlainText(test_text)

        # 입력 확인
        assert widget.get_system_prompt() == test_text

    def test_user_prompt_editing(self, qtbot):
        """User Prompt 편집 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # User Prompt 입력
        test_text = "Analyze the following text: {{text}}"
        widget._user_prompt_edit.setPlainText(test_text)

        # 입력 확인
        assert widget.get_user_prompt() == test_text

    def test_variable_detection(self, qtbot):
        """변수 감지 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 변수가 포함된 텍스트 입력
        widget._user_prompt_edit.setPlainText("{{name}} is {{age}} years old.")

        # 변수 감지
        variables = widget.detect_variables()

        # 변수 확인
        assert "name" in variables
        assert "age" in variables
        assert len(variables) == 2

    def test_no_variables(self, qtbot):
        """변수가 없는 경우 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 변수가 없는 텍스트 입력
        widget._user_prompt_edit.setPlainText("This is a simple prompt.")

        # 변수 감지
        variables = widget.detect_variables()

        # 변수 없음 확인
        assert len(variables) == 0

    def test_nested_variables(self, qtbot):
        """중첩된 변수 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 중첩된 변수 입력 (중첩은 지원하지 않음)
        widget._user_prompt_edit.setPlainText("{{outer}} and {{another}}")

        # 변수 감지
        variables = widget.detect_variables()

        # 변수 확인
        assert "outer" in variables
        assert "another" in variables

    def test_special_characters_in_variables(self, qtbot):
        """변수 이름의 특수 문자 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 특수 문자가 포함된 변수
        widget._user_prompt_edit.setPlainText("{{user_name}} and {{test-id}}")

        # 변수 감지
        variables = widget.detect_variables()

        # 변수 확인
        assert "user_name" in variables
        assert "test-id" in variables

    def test_set_system_prompt(self, qtbot):
        """System Prompt 설정 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # System Prompt 설정
        test_text = "Test system prompt"
        widget.set_system_prompt(test_text)

        # 설정 확인
        assert widget._system_prompt_edit.toPlainText() == test_text

    def test_set_user_prompt(self, qtbot):
        """User Prompt 설정 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # User Prompt 설정
        test_text = "Test user prompt with {{variable}}"
        widget.set_user_prompt(test_text)

        # 설정 확인
        assert widget._user_prompt_edit.toPlainText() == test_text

    def test_clear_prompts(self, qtbot):
        """프롬프트 초기화 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 프롬프트 입력
        widget._system_prompt_edit.setPlainText("System")
        widget._user_prompt_edit.setPlainText("User {{var}}")

        # 초기화
        widget.clear_prompts()

        # 초기화 확인
        assert widget._system_prompt_edit.toPlainText() == ""
        assert widget._user_prompt_edit.toPlainText() == ""

    def test_prompt_changed_signal(self, qtbot):
        """프롬프트 변경 시그널 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 시그널 캡처 준비
        signal_emitted = False
        signal_type = None

        def on_prompt_changed(prompt_type: str):
            nonlocal signal_emitted, signal_type
            signal_emitted = True
            signal_type = prompt_type

        widget.prompt_changed.connect(on_prompt_changed)

        # System Prompt 변경
        widget._system_prompt_edit.setPlainText("Test")
        QTest.qWait(100)

        # 시그널 발생 확인
        assert signal_emitted
        assert signal_type == "system"

    def test_version_timeline(self, qtbot):
        """버전 타임라인 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 버전 목록 확인 (초기에는 비어있음)
        versions = widget.get_versions()
        assert len(versions) == 0

        # 버전 추가
        widget.add_version("1.0", "Initial version")

        # 버전 확인
        versions = widget.get_versions()
        assert len(versions) == 1
        assert versions[0]["version"] == "1.0"
        assert versions[0]["description"] == "Initial version"

    def test_switch_version(self, qtbot):
        """버전 전환 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 초기 프롬프트
        widget._user_prompt_edit.setPlainText("Version 1.0")
        widget.add_version("1.0", "Initial")

        # 버전 변경
        widget._user_prompt_edit.setPlainText("Version 2.0")
        widget.add_version("2.0", "Updated")

        # 버전 목록 확인
        versions = widget.get_versions()
        assert len(versions) == 2

    def test_empty_variable_detection(self, qtbot):
        """빈 변수 이름 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 빈 변수 ({{}})
        widget._user_prompt_edit.setPlainText("Test with {{}}")

        # 변수 감지
        variables = widget.detect_variables()

        # 빈 변수는 무시되어야 함
        assert len(variables) == 0

    def test_malformed_variables(self, qtbot):
        """비정상적인 변수 형식 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        # 닫히지 않은 변수
        widget._user_prompt_edit.setPlainText("Test with {{open")

        # 변수 감지
        variables = widget.detect_variables()

        # 비정상적인 변수는 무시
        assert len(variables) == 0

    def test_variables_tab_updates_with_prompt(self, qtbot):
        """Variables 탭 동기화 테스트"""
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        widget.set_user_prompt("Hello {{name}} from {{city}}")
        qtbot.wait(50)

        assert widget._variables_table.rowCount() == 2
        detected_keys = set()
        for row in range(widget._variables_table.rowCount()):
            key_item = widget._variables_table.item(row, 0)
            assert key_item is not None
            detected_keys.add(key_item.text())
        assert detected_keys == {"name", "city"}

    def test_variable_highlighters_attached(self, qtbot):
        widget = PromptEditor()
        qtbot.addWidget(widget)
        widget.show()

        assert len(widget._highlighters) == 2
        for highlighter in widget._highlighters:
            assert isinstance(highlighter, VariableSyntaxHighlighter)
