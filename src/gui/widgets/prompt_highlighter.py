"""
[overview]
프롬프트 변수 구문 하이라이터

[description]
QPlainTextEdit 문서에서 {{variable}} 패턴을 강조 표시하는 QSyntaxHighlighter 구현입니다.
"""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)

from src.gui.theme import COLOR_ACCENT

VARIABLE_TOKEN_PATTERN: QRegularExpression = QRegularExpression(
    r"\{\{[a-zA-Z0-9_-]+\}\}"
)


class VariableSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)

        self._variable_format = QTextCharFormat()
        self._variable_format.setForeground(QColor(COLOR_ACCENT))
        self._variable_format.setFontWeight(QFont.Weight.DemiBold)

    def highlightBlock(self, text: str) -> None:
        match_iterator = VARIABLE_TOKEN_PATTERN.globalMatch(text)
        while match_iterator.hasNext():
            match = match_iterator.next()
            self.setFormat(
                match.capturedStart(),
                match.capturedLength(),
                self._variable_format,
            )
