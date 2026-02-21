# Prompt Manager Notepad - Issues

## [2026-02-15] Task 6: 코어 로직 - LLM Service 및 Provider Manager
- **CRITICAL**: 파일 길이 500줄 초과 (llm_service.py: 252줄, provider_manager.py: 188줄, task_manager.py: 174줄, version_manager.py: 180줄)
- 해결 필요: 파일 모듈화 (단일 책임 원칙 준수)
- 현재 상태: 테스트는 통과했으나, 가드레일 위배됨

## [2026-02-22] Task 10: 기능 연동 및 완성(Task 10) 검토
- 발견 이슈: 없음. 현재 Task 10 연결 지점은 `MainWindow`와 위젯 간 signal/slot이 정상 동작.
- 조치: 추가 수정 없이 검증으로 종료.
- Ruff lint: E402 import at top and unused imports in tests identified; applied surgical fixes:
  - src/gui/main.py: moved configure_qt_platform() after imports to satisfy E402
  - tests/gui/test_prompt_runner.py: removed unused LLMService import
  - tests/gui/widgets/test_provider_management_widget.py: removed unused QMessageBox import

## [2026-02-22] mypy 최종 게이트 이슈 정리
- 이슈: `types-requests` 미설치로 `src/core/llm_service.py`, `src/core/provider_manager.py`, `src/gui/prompt_runner.py`에서 `import-untyped` 발생.
- 조치: 설치 변경 없이(환경 영향 최소화) import 라인에 한정된 ignore를 적용.
- 이슈: `main_window_ui.py`의 action 연결 lambda에서 mypy가 콜백 타입 추론 실패.
- 조치: `_ignore_checked` typed helper 추가로 람다 제거.
- 결과: `mypy src/` 통과, `ruff check src/ tests/` 통과.

## [2026-02-22] 최종 체크리스트 블로커(해결)
- 블로커: `src/gui/main_window.py`, `src/gui/widgets/result_viewer.py`가 500줄 초과.
- 조치: UI 스타일/헬퍼 로직을 별도 모듈로 추출해 라인 수 감소(동작 보존).
- 블로커: `src/__init__.py`에 `[overview]`/`[description]` 누락.
- 조치: 최상단 패키지 docstring 추가.
