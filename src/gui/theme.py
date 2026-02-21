"""
[overview]
Prompt Manager 공통 테마 토큰 및 전역 QSS 로더

[description]
Stitch 기반 모던/클린 데스크톱 스타일에 맞춘 색상 상수와,
메인 윈도우 전역 QSS 파일 로딩/토큰 치환 유틸리티를 제공합니다.
"""

from pathlib import Path

COLOR_BACKGROUND: str = "#F5F7FB"
COLOR_SIDEBAR: str = "#FFFFFF"
COLOR_ACCENT: str = "#0B74DE"
COLOR_ACCENT_HOVER: str = "#095FB5"
COLOR_ACCENT_PRESSED: str = "#074B8F"
COLOR_TEXT_PRIMARY: str = "#0F172A"
COLOR_TEXT_SECONDARY: str = "#64748B"
COLOR_TEXT_ON_ACCENT: str = "#FFFFFF"
COLOR_HIGHLIGHT: str = "#B45309"
COLOR_BORDER: str = "#D9E2EC"
COLOR_INPUT_BG: str = "#F8FAFC"
COLOR_INPUT_BORDER: str = "#CBD5E1"
COLOR_BUTTON_BG: str = "#E2E8F0"
COLOR_BUTTON_HOVER: str = "#CBD5E1"
COLOR_SCROLLBAR: str = "#C0CBD9"
COLOR_ACCENT_SOFT: str = "rgba(11, 116, 222, 0.14)"
COLOR_SURFACE_HOVER: str = "rgba(15, 23, 42, 0.06)"
COLOR_SURFACE_HOVER_STRONG: str = "rgba(15, 23, 42, 0.1)"
COLOR_ERROR: str = "#FF6B6B"
COLOR_ERROR_SOFT: str = "rgba(255, 107, 107, 0.1)"
COLOR_DIFF_REMOVED_BG: str = "#FEE2E2"
COLOR_DIFF_ADDED_BG: str = "#DCFCE7"
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
