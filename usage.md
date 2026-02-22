# Prompt Manager 사용 가이드

[overview]
Prompt Manager 프로젝트의 모듈 사용법, API, 다이어그램을 설명합니다.

[description]
개발자가 프로젝트의 구조와 동작을 빠르게 이해할 수 있도록 각 모듈의 사용법을 문서화합니다.
프로젝트 핵심 기능을 빠르게 활용할 수 있도록 API 및 아키텍처 기준을 제공합니다.

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [아키텍처](#아키텍처)
3. [모듈 가이드](#모듈-가이드)
4. [개발 팁](#개발-팁)

---

## 1. 프로젝트 개요

**기술 스택**:
- GUI: PySide6 (Qt for Python)
- 백엔드: Python 3.12+
- 데이터베이스: TinyDB (JSON 파일 기반)
- API 통신: requests (OpenAI Compatible API)

**프로젝트 구조**:
```
prompt_manager/
├── data/                      # TinyDB 데이터 파일
│   └── prompts.json
├── main.py                    # 루트 실행 진입점
├── run.py                     # 대체 실행 진입점
├── src/
│   ├── core/                  # Main business logic + extension hooks
│   │   ├── task_manager.py
│   │   ├── version_manager.py
│   │   ├── provider_manager.py
│   │   ├── llm_service.py
│   │   ├── template_engine.py
│   │   ├── prompt_snapshot.py
│   │   └── plugin_interface.py
│   ├── data/                  # Pydantic models + repository + TinyDB lifecycle
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── database.py
│   ├── gui/                   # UI orchestration and widgets
│   │   ├── main.py
│   │   ├── main_window.py
│   │   ├── main_window_ui.py
│   │   ├── main_window_helpers.py
│   │   ├── main_window_constants.py
│   │   ├── prompt_runner.py
│   │   ├── qt_platform.py
│   │   ├── theme.py
│   │   └── widgets/
│   └── utils/                 # Shared utilities and constants
│       ├── config.py
│       ├── id_generator.py
│       ├── string_utils.py
│       └── logger.py
├── requirements.txt           # Python 의존성
└── tests/                     # 테스트 파일 (pytest, pytest-qt)
```

**개발 원칙**:
- **Modularity**: 모든 기능은 별도 모듈로 구현
- **Independence**: 모듈은 독립적으로 동작
- **Main Logic + Plugin**: 코어 로직 + 플러그인 패턴
- **TDD**: 테스트 우선 개발 (테스트 → 구현 → 검증)

---

## 2. 아키텍처

Prompt Manager는 **Layered Architecture**와 **Main Logic + Plugin Pattern**을 따릅니다.

기준 문서 우선순위:
- 모듈 경계/의존성 기준: `AGENTS.md`의 `## 9. Repository Module Map (Authoritative)`
- 본 문서는 위 기준을 설명/사용 예시 중심으로 보조합니다.

### 📊 전체 아키텍처

```
Entrypoint
  -> GUI
     -> Core
        -> Data
           -> Utils

Additional allowed path:
  GUI -> Data models (UI representation 목적)
```

### 📐 계층별 상세

**GUI Layer**:
- **main_window.py**: task/version/provider 흐름 오케스트레이션
- **main_window_ui.py**: 메뉴/툴바/레이아웃 조립
- **prompt_runner.py**: PromptEditor -> TemplateEngine -> LLMService -> ResultViewer 실행 경계
- **widgets/**: 태스크/프롬프트/결과/프로바이더 관리 UI
- **main_window_helpers.py / main_window_constants.py / theme.py / qt_platform.py**: UI 보조 계층

**Core Layer**:
- **task_manager.py / version_manager.py / provider_manager.py / llm_service.py**: 도메인 매니저 및 훅 실행
- **template_engine.py**: 변수 템플릿 렌더링
- **prompt_snapshot.py**: `Version.content` 직렬화/역직렬화 경계
- **plugin_interface.py**: `TaskPlugin` 인터페이스

**Data Layer**:
- **models.py**: Pydantic 모델
- **repository.py**: CRUD 추상화 + 도메인별 Repository
- **database.py**: TinyDB 라이프사이클

**Utils Layer**:
- **config.py**: 중앙 상수 설정
- **id_generator.py**: ID 생성
- **string_utils.py**: 문자열 파싱
- **logger.py**: 공통 로깅

**Plugin 경계**:
- `TaskPlugin`: `src/core/plugin_interface.py`, `TaskManager` 훅에서 실행
- `LLMPlugin`: `src/core/llm_service.py`, before/after call 훅에서 실행
- `ProviderPlugin`: `src/core/provider_manager.py`, provider lifecycle 훅에서 실행
- 현재 상태: 인터페이스/훅은 존재, concrete `plugins/` 구현은 아직 없음

---

## 3. 모듈 가이드

### 🧰 Utils Layer

#### string_utils.py

**개요**: 템플릿 변수 파싱 유틸리티

**주요 함수**:
```python
from src.utils.string_utils import extract_variables

# 변수 추출
variables = extract_variables("Hello {{name}}, your age is {{age}}")
# 결과: ['name', 'age']

# 템플릿 렌더링
template = "Translate {{text}} to {{target_language}}"
result = template_engine.render(template, {"text": "Hello World", "target_language": "Korean"})
```

**상수 사용**:
- `TEMPLATE_START_DELIMITER`: "{{"
- `TEMPLATE_END_DELIMITER`: "}}"
- `VARIABLE_PATTERN`: 정규식 패턴

---

#### id_generator.py

**개요**: UUID 기반 고유 ID 생성

**주요 함수**:
```python
from src.utils.id_generator import generate_id

# 고유 ID 생성
task_id = generate_id()
# 결과: '70edddd3-dbae-476d-a380-9c06d5d29b97'

# 태스크 ID 생성 (wrapper)
from src.utils.id_generator import generate_id as generate_task_id
task_id = generate_task_id()
```

**상수 사용**:
- `UUID_LENGTH`: 36

---

#### config.py

**개요**: 프로젝트 전반에서 사용하는 상수 및 설정 값 중앙 관리

**주요 상수**:
```python
# 템플릿 변수 구분자
from src.utils.config import TEMPLATE_START_DELIMITER, TEMPLATE_END_DELIMITER

# 태스크 관련 상수
from src.utils.config import MAX_TASK_NAME_LENGTH, MAX_TASK_DESCRIPTION_LENGTH

# 버전 관련 상수
from src.utils.config import MAX_VERSION_NUMBER, MAX_PROMPT_LENGTH

# API 관련 상수
from src.utils.config import API_TIMEOUT_SECONDS, MAX_RETRY_COUNT

# 파일 경로 상수
from src.utils.config import DATABASE_FILENAME, DATA_DIR_NAME
```

**Magic Number 방지**: 모든 매직수는 명시적 상수로 정의됨

---

### 📊 Data Layer

#### models.py

**개요**: Pydantic 기반 데이터 모델 정의

**데이터 모델**:
```python
# Task 모델
from src.data.models import Task

task = Task(
    name="Test Task",
    description="Test Description"
)

task.id  # 자동 생성된 UUID
task.created_at  # 자동 생성된 timestamp
```

**Validator 사용**:
- `max_length`: 최대 길이 제한
- `Field validator`: 데이터 유효성 검사

---

#### database.py

**개요**: TinyDB 데이터베이스 초기화 및 관리

**주요 기능**:
```python
from src.data.database import Database, get_db

# 데이터베이스 인스턴스 가져오기
db = get_db()

# 테이블에 데이터 저장
from src.data.models import Task
from src.data.repository import TaskRepository
repo = TaskRepository()
task = repo.create(Task(name="New Task"))
```

**Lazy Initialization**: 데이터베이스 인스턴스는 첫 접근 시에 생성됨

---

#### repository.py

**개요**: Repository 패턴 (BaseRepository ABC + 구현체들)

**Repository 인터페이스**:
```python
# BaseRepository (추상 인터페이스)
from src.data.repository import BaseRepository

# 구현체
from src.data.repository import TaskRepository, PromptRepository, VersionRepository, ExecutionRecordRepository, ProviderRepository

# 사용 예시
repo = TaskRepository()
task = repo.create(Task(name="Test Task"))
task = repo.get(task_id)
```

**CRUD 연산**:
- `create(entity)`: 엔티티 생성
- `read(entity_id)`: ID로 엔티티 조회
- `update(entity)`: 엔티티 수정
- `delete(entity_id)`: 엔티티 삭제
- `get_all()`: 전체 목록 조회
```

**독립성 보장**:
- Repository 패턴을 통해 데이터베이스 접근 추상화
- 다른 Repository로 쉽게 교체 가능

---

### 🎛 Core Layer

#### plugin_interface.py

**개요**: 플러그인 인터페이스 정의 (TaskPlugin ABC)

**인터페이스**:
```python
# TaskPlugin 인터페이스
from src.core.plugin_interface import TaskPlugin

class MyPlugin(TaskPlugin):
    def execute(self, task_id: str, context: dict) -> dict:
        # 플러그인 로직 구현
        context["plugin_result"] = "executed"
        return context

    def get_name(self) -> str:
        return "MyPlugin"
```

**확장 포인트**:
- `execute()`: 태스크 실행 후 훅
- `get_name()`: 플러그인 이름

---

#### task_manager.py

**개요**: 태스크 CRUD 관리, Task-Prompt 연결 관계

**주요 함수**:
```python
from src.core.task_manager import TaskManager

# TaskManager 초기화
tm = TaskManager()

# 태스크 생성
task = tm.create_task(
    name="My Task",
    description="Task description"
)

# 모든 태스크 조회
tasks = tm.get_all_tasks()

# 태스크 수정
task = tm.update_task(
    task_id=task.id,
    name="Updated Task"
)

# 태스크 삭제
success = tm.delete_task(task.id)

# 프롬프트 조회
from src.data.models import Prompt
prompts = tm.get_task_prompts(task.id)
```

**플러그인 기능**:
- `register_plugin(plugin)`: 플러그인 등록
- 플러그인은 태스크 관련 훅에서 실행됨

---

#### version_manager.py

**개요**: 버전 관리 (단순 스냅샷 방식)

**주요 함수**:
```python
from src.core.version_manager import VersionManager

# VersionManager 초기화
vm = VersionManager()

# 버전 생성
from src.data.models import Prompt, Version
prompt_id = generate_task_id()
version = vm.create_version(
    prompt_id=prompt_id,
    content="Updated prompt content"
)

# 타임라인 조회
timeline = vm.get_version_timeline(prompt_id)

# 버전 복구
old_version = vm.get_version(prompt_id, version_id)
new_version = vm.restore_version(old_version.id)
```

**단순 스냅샷**: 각 버전은 독립적으로 저장됨

**첫 번째 버전 자동 생성**: `ensure_first_version()` 메서드

---

#### template_engine.py

**개요**: {{변수명}} 형식의 템플릿 엔진

**주요 함수**:
```python
from src.core.template_engine import TemplateEngine

# TemplateEngine 초기화
te = TemplateEngine("Hello {{name}}, your age is {{age}}")

# 변수 파싱
variables = te.parse_variables()
# 결과: ['name', 'age']

# 템플릿 렌더링
result = te.render({"name": "John", "age": 30})
# 결과: "Hello John, your age is 30"
```

**문법 확장**:
- `$variable` 및 `${variable}` 형식도 지원

**안전한 렌더링**: `safe_substitute()` 사용 (누락된 변수 처리)

---

#### llm_service.py

**개요**: OpenAI Compatible API 통합, 메트릭 수집

**주요 함수**:
```python
from src.core.llm_service import LLMService, LLMPlugin

# LLMService 초기화
llm = LLMService(api_url="https://api.openai.com/v1/chat/completions")

# API 호출 (비동기 처리를 위해 인터페이스 제공)
result = llm.call_llm_with_metrics(
    prompt="Test prompt",
    model="gpt-4",
    provider_id=provider.id
)

# 플러그인 사용 예시
from src.core.llm_service import LLMPlugin

class MetricsPlugin(LLMPlugin):
    def execute(self, task_id: str, context: dict) -> dict:
        context["metrics"] = {"response_time": 1.5}
        return context
```

**메트릭 수집**:
- `response_time`: 응답 시간 (초 단위)
- `prompt_tokens`: 입력 토큰
- `completion_tokens`: 완성 토큰
- `total_tokens`: 총 토큰

---

#### provider_manager.py

**개요**: LLM Provider CRUD 관리, 연결 테스트

**주요 함수**:
```python
from src.core.provider_manager import ProviderManager

# ProviderManager 초기화
pm = ProviderManager()

# Provider 생성
provider = pm.create_provider(
    name="OpenAI",
    api_url="https://api.openai.com",
    api_key="sk-..."
)

# 연결 테스트
success = pm.test_connection(provider.id)
```

---

## 4. 개발 팁

### ✅ TDD 방식 준수
- 테스트를 먼저 작성 → 실패 확인 → 코드 구현 → 통과 확인
- `pytest tests/ -v`: 전체 테스트 실행

### 🔤 파일 길이 제한
- 모든 Python 파일은 500줄을 초과할 수 없음
- 초과 시 파일 모듈화 필요

### 🎨 Main Logic + Plugin 패턴
- 코어 로직은 확장 가능한 플러그인 시스템 제공
- `TaskPlugin` 인터페이스를 상속받아 커스텀 플러그인 구현

### 📝 독립성 보장
- Repository 패턴을 통해 데이터베이스 접근 추상화
- GUI 계층은 Core 및 Data 모델(표현 목적)에 의존 가능
- 각 모듈은 독립적으로 테스트 가능

---

## 🔧 빠른 시작하기

### 설치
```bash
# 가상 환경 활성화
python3.12 -m venv venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python run.py
```

### 테스트 실행
```bash
# 전체 테스트
pytest tests/ -v

# 특정 모듈 테스트
pytest tests/core/test_task_manager.py -v

# 커버리지 확인
pytest tests/ --cov=src --cov-report=html
```

---

## 📚 참조 문서

- **README.md**: 프로젝트 개요 및 설치 가이드
- **AGENTS.md**: AI Agent 개발 가이드
- **architectral_standard.md**: Main Logic + Plugin Architecture 상세

---

**마지막 문서**: 2026-02-22

**버전**: v1.0.0

---

**문의사항이나 계시면 프로젝트 이슈에 등록해주세요!**
