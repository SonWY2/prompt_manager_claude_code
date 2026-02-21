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
