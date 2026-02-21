"""
[overview]
Qt 플랫폼 자동 설정 유틸리티

[description]
WSL/Linux 환경에서 Wayland 소켓이 없을 때 X11(xcb)로 자동 전환해
QApplication 초기화 실패를 방지합니다.
"""

from pathlib import Path
import os
import platform

ENV_QT_QPA_PLATFORM: str = "QT_QPA_PLATFORM"
ENV_WAYLAND_DISPLAY: str = "WAYLAND_DISPLAY"
ENV_XDG_RUNTIME_DIR: str = "XDG_RUNTIME_DIR"
ENV_DISPLAY: str = "DISPLAY"

QT_PLATFORM_XCB: str = "xcb"


def _has_valid_wayland_socket() -> bool:
    runtime_dir = os.environ.get(ENV_XDG_RUNTIME_DIR)
    wayland_display = os.environ.get(ENV_WAYLAND_DISPLAY)
    if runtime_dir is None or wayland_display is None:
        return False
    return Path(runtime_dir, wayland_display).exists()


def configure_qt_platform() -> None:
    if platform.system() != "Linux":
        return

    if os.environ.get(ENV_QT_QPA_PLATFORM):
        return

    has_x11_display = bool(os.environ.get(ENV_DISPLAY))
    has_wayland_env = bool(os.environ.get(ENV_WAYLAND_DISPLAY))

    if has_wayland_env and _has_valid_wayland_socket():
        return

    if has_x11_display:
        os.environ[ENV_QT_QPA_PLATFORM] = QT_PLATFORM_XCB
