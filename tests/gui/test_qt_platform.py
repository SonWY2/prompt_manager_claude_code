"""
[overview]
qt_platform 모듈 테스트

[description]
Linux/WSL 환경에서 Qt 플랫폼 자동 선택 로직을 검증합니다.
"""

import os
from pathlib import Path

from src.gui.qt_platform import (
    ENV_DISPLAY,
    ENV_QT_QPA_PLATFORM,
    ENV_WAYLAND_DISPLAY,
    ENV_XDG_RUNTIME_DIR,
    QT_PLATFORM_XCB,
    configure_qt_platform,
)


class TestQtPlatform:
    def test_fallbacks_to_xcb_when_wayland_socket_missing(self, monkeypatch, tmp_path):
        monkeypatch.setattr("src.gui.qt_platform.platform.system", lambda: "Linux")
        monkeypatch.delenv(ENV_QT_QPA_PLATFORM, raising=False)
        monkeypatch.setenv(ENV_DISPLAY, ":0")
        monkeypatch.setenv(ENV_WAYLAND_DISPLAY, "wayland-0")
        monkeypatch.setenv(ENV_XDG_RUNTIME_DIR, str(tmp_path))

        configure_qt_platform()

        assert ENV_QT_QPA_PLATFORM in os.environ
        assert os.environ[ENV_QT_QPA_PLATFORM] == QT_PLATFORM_XCB

    def test_keeps_wayland_when_socket_exists(self, monkeypatch, tmp_path):
        monkeypatch.setattr("src.gui.qt_platform.platform.system", lambda: "Linux")
        monkeypatch.delenv(ENV_QT_QPA_PLATFORM, raising=False)
        monkeypatch.setenv(ENV_DISPLAY, ":0")
        monkeypatch.setenv(ENV_WAYLAND_DISPLAY, "wayland-0")
        monkeypatch.setenv(ENV_XDG_RUNTIME_DIR, str(tmp_path))
        Path(tmp_path, "wayland-0").touch()

        configure_qt_platform()

        assert ENV_QT_QPA_PLATFORM not in os.environ

    def test_respects_user_defined_qt_platform(self, monkeypatch):
        monkeypatch.setattr("src.gui.qt_platform.platform.system", lambda: "Linux")
        monkeypatch.setenv(ENV_QT_QPA_PLATFORM, "offscreen")
        monkeypatch.setenv(ENV_DISPLAY, ":0")
        monkeypatch.delenv(ENV_WAYLAND_DISPLAY, raising=False)
        monkeypatch.delenv(ENV_XDG_RUNTIME_DIR, raising=False)

        configure_qt_platform()

        assert os.environ[ENV_QT_QPA_PLATFORM] == "offscreen"
