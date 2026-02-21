"""
[overview]
Prompt Manager 공통 테마 토큰 및 전역 QSS 로더

[description]
Stitch 기반 모던/클린 데스크톱 스타일에 맞춘 색상 상수와,
메인 윈도우 전역 QSS 파일 로딩/토큰 치환 유틸리티를 제공합니다.
"""

from pathlib import Path

COLOR_BACKGROUND: str = "#101922"
COLOR_SIDEBAR: str = "#15202b"
COLOR_ACCENT: str = "#2b8cee"
COLOR_ACCENT_HOVER: str = "#2378cb"
COLOR_ACCENT_PRESSED: str = "#1d66ae"
COLOR_TEXT_PRIMARY: str = "#D4D4D4"
COLOR_TEXT_SECONDARY: str = "#8f9aa8"
COLOR_TEXT_ON_ACCENT: str = "#FFFFFF"
COLOR_HIGHLIGHT: str = "#ce9178"
COLOR_BORDER: str = "#1e2d3b"
COLOR_INPUT_BG: str = "#0f161f"
COLOR_INPUT_BORDER: str = "#2a3a4b"
COLOR_BUTTON_BG: str = "#203040"
COLOR_BUTTON_HOVER: str = "#2a3f53"
COLOR_SCROLLBAR: str = "#32475b"
COLOR_ACCENT_SOFT: str = "rgba(43, 140, 238, 0.15)"
COLOR_SURFACE_HOVER: str = "rgba(255, 255, 255, 0.05)"
COLOR_SURFACE_HOVER_STRONG: str = "rgba(255, 255, 255, 0.08)"
COLOR_ERROR: str = "#FF6B6B"
COLOR_ERROR_SOFT: str = "rgba(255, 107, 107, 0.1)"
COLOR_DIFF_REMOVED_BG: str = "#4a1f1f"
COLOR_DIFF_ADDED_BG: str = "#1f4a2a"
COLOR_STATUS_CONNECTED: str = "#4CAF50"
COLOR_STATUS_ERROR: str = "#F44336"
COLOR_STATUS_UNKNOWN: str = "#9E9E9E"

THEME_QSS_FILE_NAME: str = "modern_clean_theme.qss"

THEME_TOKEN_MAP: dict[str, str] = {
    "@COLOR_BACKGROUND@": COLOR_BACKGROUND,
    "@COLOR_SIDEBAR@": COLOR_SIDEBAR,
    "@COLOR_ACCENT@": COLOR_ACCENT,
    "@COLOR_TEXT_PRIMARY@": COLOR_TEXT_PRIMARY,
    "@COLOR_TEXT_ON_ACCENT@": COLOR_TEXT_ON_ACCENT,
    "@COLOR_BORDER@": COLOR_BORDER,
    "@COLOR_SCROLLBAR@": COLOR_SCROLLBAR,
    "@COLOR_SURFACE_HOVER_STRONG@": COLOR_SURFACE_HOVER_STRONG,
}


def _fallback_stylesheet() -> str:
    """QSS 파일 로드 실패 시 사용할 최소 스타일시트 반환"""
    return f"""
    QMainWindow {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QWidget {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QMenu::item:selected {{
        background-color: {COLOR_ACCENT};
        color: {COLOR_TEXT_ON_ACCENT};
    }}
    """


def get_main_window_stylesheet() -> str:
    """메인 윈도우 전역 스타일시트를 로드하고 토큰 치환 후 반환"""
    qss_path = Path(__file__).resolve().with_name(THEME_QSS_FILE_NAME)

    try:
        stylesheet = qss_path.read_text(encoding="utf-8")
    except OSError:
        return _fallback_stylesheet()

    for token, value in THEME_TOKEN_MAP.items():
        stylesheet = stylesheet.replace(token, value)

    return stylesheet
