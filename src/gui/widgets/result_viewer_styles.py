"""\
[overview]
ResultViewer 스타일

[description]
ResultViewer(QWidget)의 Qt 스타일시트/HTML 템플릿을 분리합니다.
위젯 로직 파일의 라인 수를 줄이되, UI 동작과 렌더링 결과는 동일하게 유지합니다.
"""

from __future__ import annotations

from html import escape

from src.gui.theme import (
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_PRESSED,
    COLOR_BACKGROUND,
    COLOR_BORDER,
    COLOR_BUTTON_BG,
    COLOR_ERROR,
    COLOR_ERROR_SOFT,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_SIDEBAR,
    COLOR_TEXT_ON_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)


def tab_widget_stylesheet() -> str:
    return f"""
            QTabWidget::pane {{ border: none; background-color: {COLOR_BACKGROUND}; }}
            QTabBar::tab {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                padding: 10px 16px;
                margin-right: 4px;
                font-size: 10pt;
                font-weight: 500;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLOR_ACCENT};
                border-bottom: 2px solid {COLOR_ACCENT};
            }}
            QTabBar::tab:hover {{ color: {COLOR_TEXT_PRIMARY}; }}
            """


def control_bar_stylesheet() -> str:
    return (
        f"background-color: {COLOR_SIDEBAR}; border-bottom: 1px solid {COLOR_BORDER};"
    )


def run_button_stylesheet() -> str:
    return f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_TEXT_ON_ACCENT};
                border: none;
                border-radius: 8px;
                padding: 10px 32px;
                font-size: 11pt;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COLOR_ACCENT_HOVER}; }}
            QPushButton:pressed {{ background-color: {COLOR_ACCENT_PRESSED}; }}
            QPushButton:disabled {{ background-color: {COLOR_BUTTON_BG}; color: {COLOR_TEXT_SECONDARY}; }}
            """


def result_browser_stylesheet() -> str:
    return f"""
            QTextBrowser {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                padding: 20px;
                font-size: 11pt;
                line-height: 1.6;
            }}
            """


def history_list_stylesheet() -> str:
    return (
        f"QListWidget {{ background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY}; border: 1px solid {COLOR_BORDER}; }}"
        f"\nQListWidget::item:selected {{ background-color: {COLOR_BORDER}; color: {COLOR_TEXT_PRIMARY}; }}"
    )


def history_preview_stylesheet() -> str:
    return f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY};"


def compare_browser_stylesheet() -> str:
    return f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_PRIMARY};"


def combo_box_stylesheet(min_width: int) -> str:
    return f"""
         QComboBox {{
             background-color: {COLOR_INPUT_BG};
             color: {COLOR_TEXT_PRIMARY};
             border: 1px solid {COLOR_INPUT_BORDER};
             border-radius: 10px;
             padding: 0px 12px;
             padding-right: 34px;
             font-size: 10pt;
             min-width: {min_width}px;
             min-height: 38px;
         }}
         QComboBox:hover {{
             border: 1px solid {COLOR_ACCENT};
         }}
         QComboBox:focus {{
             border: 1px solid {COLOR_ACCENT};
         }}
         QComboBox::drop-down {{
             border: none;
             subcontrol-origin: padding;
             subcontrol-position: top right;
             width: 28px;
         }}
         QComboBox::down-arrow {{
             image: none;
             width: 0px;
             height: 0px;
             border-left: 5px solid transparent;
             border-right: 5px solid transparent;
             border-top: 6px solid {COLOR_TEXT_SECONDARY};
             margin-right: 8px;
         }}
         QComboBox QAbstractItemView {{
             background-color: {COLOR_SIDEBAR};
             selection-background-color: {COLOR_ACCENT};
             color: {COLOR_TEXT_PRIMARY};
             border: 1px solid {COLOR_INPUT_BORDER};
             border-radius: 8px;
             padding: 4px;
         }}
         """


def metrics_bar_stylesheet() -> str:
    return f"QWidget {{ background-color: {COLOR_BORDER}; border-top: 1px solid {COLOR_BORDER}; }}"


def error_html(error: str) -> str:
    return """
            <div style="color: {error_color}; padding: 16px; border-left: 4px solid {error_color}; background-color: {error_background};">
                <strong>Error:</strong> {error}
            </div>
            """.format(
        error=escape(error),
        error_color=COLOR_ERROR,
        error_background=COLOR_ERROR_SOFT,
    )
