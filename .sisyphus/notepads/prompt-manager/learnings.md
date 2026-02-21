# Prompt Manager Notepad - Learnings

## [2026-02-15] Task 0: 테스트 인프라 설정
- pytest.ini 설정: testpaths = tests, python_files = test_*.py
- tests/ 디렉토리 구조 생성
- pytest 설치 확인: help 출력 가능
- 테스트 실행: 2 passed in 0.13s
- 파일 길이: pytest.ini (11줄), __init__.py (8줄), test_example.py (19줄)

## [2026-02-15] Task 1: 프로젝트 설정
- requirements.txt 생성
- pytest.ini 업데이트
- run.py 생성
- requirements.txt 길이: 13줄
- run.py 길이: 26줄

## [2026-02-15] Task 3: 데이터 계층
- tests/data/test_models.py: 16개 테스트 (Task, Prompt, Version, ExecutionRecord, Provider 모델)
- tests/data/test_repository.py: 20개 테스트 (CRUD)
- src/data/models.py: pydantic BaseModel, 143줄
- src/data/database.py: TinyDB 초기화, lazy initialization, 105줄
- src/data/repository.py: BaseRepository ABC + 구현, 316줄
- src/data/__init__.py: 패키지 내보내기
- pytest tests/data/ -v → 36 passed in 0.33s
- pytest.ini 수정: pythonpath = . 추가 (import 에러 해결)

## [2026-02-15] Issue: pytest import 에러 해결
- 문제: pytest 실행 시 `from src.data.models import` 에러 발생
- 원인: 프로젝트 루트가 Python path에 없음
- 해결: pytest.ini에 `pythonpath = .` 설정 추가

## [2026-02-15] Task 4: 코어 로직 - Plugin Interface 및 Task Manager
- src/core/plugin_interface.py: TaskPlugin ABC, 46줄
- src/core/task_manager.py: TaskManager (Repository 사용, plugin 실행), 175줄
- pytest tests/core/ -v → 18 passed in 3.92s

## [2026-02-15] Task 3: 데이터 계층
- src/utils/ 디렉토리 생성
- string_utils.py 생성 ({{변수명}} 형식 파싱)
- id_generator.py 생성 (UUID 기반 ID 생성)
- config.py 생성 (상수 및 설정 값, Magic Number 방지)
- pytest tests/utils/ -v → 16 passed in 0.14s
- 파일 길이: string_utils.py (45줄), id_generator.py (21줄), config.py (36줄), __init__.py (40줄)

## [2026-02-15] Task 8: GUI 위젯
- task_navigator.py: Task Navigator (좌측 250px)
- prompt_editor.py: Prompt Editor (중앙 가변)
- result_viewer.py: Result Viewer (우측 350px)
- widgets/__init__.py: GUI widgets 패키지 초기화
- pytest-qt tests/gui/widgets/ -v → 38 passed in 0.95s

## [2026-02-15] Task 9: LLM Provider Management UI
- provider_list_panel.py: 176줄, 좌측 Provider List Panel
- provider_config_panel.py: 269줄, 우측 Configuration Detail Panel
- provider_dialog.py: 218줄, 추가/편집 다이얼로그
- widgets/__init__.py 업데이트: ProviderManagement UI 모듈 노출
- pytest-qt tests/gui/widgets/test_provider_*.py -v → 227 passed in 1.81s
- 파일 길이 준수: 모두 500줄 이내
- 디자인 스펙 엄격 준수 (llm_provider_management_design_specification.md)
- QThread 활용 비동기 통신 구현
- src/core/version_manager.py: 단순 스냅샷 방식, 첫 번째 버전 자동 생성
- src/core/template_engine.py: Python string.Template 확장 ({{변수명}} 형식)
- template_engine.py 수정: typing 모듈에서 Dict, List import 누락 해결
- pytest tests/core/ -v → 51 passed in 0.53s

## [2026-02-15] Task 6: 코어 로직 - LLM Service 및 Provider Manager
- TDD 방식: 테스트 작성 → 실패 → 구현 → 통과
- src/utils/id_generator.py 업데이트: generate_execution_record_id(), generate_provider_id() 추가
- src/core/llm_service.py: OpenAI Compatible API 호출, 메트릭 수집 (응답 시간, 토큰 사용량), LLMPlugin ABC, plugin hook 제공
- src/core/provider_manager.py: Provider CRUD, 연결 테스트 (mock API 사용)
- src/core/__init__.py 업데이트: LLMService, LLMPlugin, ProviderManager 노출
- tests/core/test_llm_service.py: 15개 테스트 (plugin interface, init, plugin management, API call, plugin execution, execution record)
- tests/core/test_provider_manager.py: 23개 테스트 (init, create, read, update, delete, connection test)
- pytest tests/core/test_llm_service.py tests/core/test_provider_manager.py -v → 38 passed in 0.50s
- 파일 길이: llm_service.py (206줄), provider_manager.py (197줄), test_llm_service.py (516줄), test_provider_manager.py (417줄)

## [2026-02-22] Task 6: LLM 플러그인 before_call 회귀 수정
- 원인: `LLMService`의 플러그인 훅 경로를 단일 `execute`에서 사후 처리까지 공유하도록 변경하면서, 기존 `TestMockPlugin`이 마지막으로 받는 컨텍스트가 `after_call`로 바뀌어 `before_call` 단언이 깨짐.
- 해결: 플러그인 처리 흐름을 전/후 분리해 `before_call`은 기존 `execute` 훅으로 유지하고, 사후 처리 훅은 기본 구현 `after_call`으로 분리 처리.
- 결과: `tests/core/test_llm_service_api.py -v`와 관련 핵심 스모크(`tests/core/test_llm_service_init.py`, `tests/core/test_llm_service_metrics.py`, `tests/core/test_provider_manager.py`)에서 회귀 제거 확인.

## [2026-02-22] Task 10: 기능 연동 및 완성(Task 10) 상태 점검
- `src/gui/main_window.py`, `main_window_ui.py`, `prompt_runner.py`, widget 모듈( `task_navigator`, `prompt_editor`, `result_viewer` ) 및 테스트를 검토.
- `pytest tests/gui/test_integration.py -v` 실행: 21 passed
- `pytest tests/gui/test_main_window.py -v` 실행: 20 passed
- Task 10 요구 항목(작업 선택→프롬프트/버전 반영→RUN 실행 결과 표시, 버전 선택 동작, 패널 토글, 메뉴/툴바 액션 연결)은 기존 구현에서 이미 충족되어 추가 코드 수정 불필요.
[FIX] Ruff lint: moved top-level private import usage in src/gui/main.py to satisfy E402 and removed unused imports in tests to eliminate linting errors. Changes were kept minimal to preserve runtime behavior.

## [2026-02-22] mypy 품질 게이트 마무리(단일 태스크)
- `requests` stub 미설치 환경에서 `import-untyped`는 각 사용 파일의 import 라인에 `# type: ignore[import-untyped]`를 국소 적용하는 방식이 가장 좁은 범위로 안전하게 해결됨.
- PySide delegate override는 `QModelIndex | QPersistentModelIndex` 시그니처를 부모와 동일하게 맞춰야 LSP 위반 오류가 사라짐.
- Qt signal 연결에서 `lambda` 추론 실패는 `Callable[[], None] -> Callable[[bool], None]` 어댑터 헬퍼로 치환하면 동작 유지 + 타입 안정성을 동시에 확보할 수 있음.
- `str | None` 할당 경고는 raw 값 변수와 최종 타입 변수(`str | None`)를 분리해 명시하면 불필요한 broad ignore 없이 해결 가능.

## [2026-02-22] 최종 체크리스트: 파일 길이/패키지 태그 정리
- 500줄 초과 파일은 “로직 유지 + 스타일/헬퍼 추출”이 가장 안전한 축소 전략.
- `src/gui/main_window.py`: 상수/다이얼로그/버전 셀렉터 로직을 `src/gui/main_window_constants.py`, `src/gui/main_window_helpers.py`로 분리.
- `src/gui/widgets/result_viewer.py`: Qt 스타일시트/에러 HTML 템플릿을 `src/gui/widgets/result_viewer_styles.py`로 분리.
- `src/__init__.py`: 최상단 docstring에 `[overview]`, `[description]` 태그 추가.

- 태스크 1: 최근 라인 카운트 리팩터로 인한 회귀 수정 및 모듈 태그 보강 완료
- 2026-02-22: Reduced src/gui/main_window.py from 509 to 500 lines without behavioral changes; tests pass (pytest) and mypy OK.
 - [Note] Appended a one-line note documenting the docstring fix for src/gui/main_window.py in this file.
