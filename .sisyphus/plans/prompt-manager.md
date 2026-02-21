# Prompt Manager 구현 계획

## TL;DR

> **Quick Summary**: README.md에 기재된 LLM 프롬프트 관리 데스크톱 GUI 애플리케이션을 처음부터 구축합니다. PySide6 기반의 3단 레이아웃(태스크 네비게이터, 프롬프트 에디터, 결과 뷰어)을 TDD 방식으로 개발하며, Main Logic + Plugin 패턴을 적용합니다.
>
> **Deliverables**:
> - 프로젝트 설정 (requirements.txt, pytest.ini, run.py)
> - 유틸리티 모듈 (string_utils.py, id_generator.py, config.py)
> - 데이터 계층 (models.py, database.py, repository.py)
> - 코어 로직 (task_manager.py, version_manager.py, template_engine.py, llm_service.py, provider_manager.py)
> - GUI 계층 (main.py, main_window.py, widgets/)
> - 테스트 파일 (pytest 기반 TDD)
>
> **Estimated Effort**: Large (15시간)
> **Parallel Execution**: NO - Layer-first 순차 개발 (데이터 → 코어 → GUI)
> **Critical Path**: 프로젝트 설정 → 유틸리티 → 데이터 계층 → 코어 로직 → GUI 프레임워크 → 기능 연동

---

## Context

### Original Request
README.md에 기재된 LLM 프롬프트 관리 데스크톱 GUI 애플리케이션을 개발하고자 합니다.

### Interview Summary
**Key Discussions**:
- **템플릿 엔진**: Python `string.Template` 확장 (사용자 선택: 옵션 A)
- **버전 관리**: 단순 스냅샷 방식 (사용자 선택: 옵션 A)
- **테스트 전략**: TDD (pytest) (사용자 선택)

**Research Findings**:
- 프로젝트는 빈 상태 (requirements.txt, run.py, src/ 없음)
- 문서 파일만 존재 (README, AGENTS, 디자인 스펙들)
- 디자인 스펙 존재: Main Dashboard, LLM Provider Management

### Metis Review
**Identified Gaps** (addressed):
- **Guardrails**: 디자인 스펙 엄격 준수, 파일 길이 500줄 제한, Magic Number 금지, TDD 강제 준수
- **Edge Cases**: 데이터베이스 파일 없는 경우, 잘못된 API 설정, 버전 관리 복잡성, 비동기 작업 동시성
- **Test Strategy**: 단위 테스트, 통합 테스트, GUI 테스트 (pytest-qt)의 구체적 명령어 정의

---

## Work Objectives

### Core Objective
빈 프로젝트에서 Prompt Manager 애플리케이션을 TDD 방식으로 구축하여 LLM 프롬프트 관리 및 테스트 환경 제공

### Concrete Deliverables
- `requirements.txt` - Python 의존성 (PySide6, TinyDB, requests, pytest)
- `pytest.ini` - pytest 설정
- `run.py` - 애플리케이션 실행 스크립트
- `src/utils/` - 유틸리티 모듈 (string_utils.py, id_generator.py, config.py)
- `src/data/` - 데이터 계층 (models.py, database.py, repository.py)
- `src/core/` - 코어 로직 (task_manager.py, version_manager.py, template_engine.py, llm_service.py, provider_manager.py)
- `src/gui/` - GUI 계층 (main.py, main_window.py, widgets/)
- `tests/` - 테스트 파일 (pytest 기반 TDD)

### Definition of Done
- [ ] 모든 테스트 통과 (`pytest tests/ -v`)
- [ ] 커버리지 80% 이상 (`pytest tests/ --cov=src --cov-report=html`)
- [ ] Linting 통과 (`ruff check src/ tests/`)
- [ ] 타입 검사 통과 (`mypy src/`)
- [ ] 애플리케이션 실행 가능 (`python run.py`)
- [ ] 모든 파일 500줄 이내 (`wc -l src/**/*.py`)

### Must Have
- README.md에 명시된 모든 주요 기능
- 디자인 스펙에 명시된 UI 구현 (Main Dashboard, LLM Provider Management)
- Main Logic + Plugin 패턴 적용
- TDD 방식 테스트
- AGENTS.md 아키텍처 원칙 준수

### Must NOT Have (Guardrails)
- README.md "향후 개선 사항" (LLM 프로바이더 다양화, A/B 테스트, SQLite 마이그레이션 등)
- 실제 LLM API 테스트 (사용자 환경에서만 수행, 개발 중에는 mock 사용)
- 디자인 스펙에 없는 요소 추가
- Magic Number 사용 (모든 상수 명시적 정의)
- 파일 길이 500줄 초과
- 테스트를 건너뛰거나 구현 후 테스트 작성

---

## Verification Strategy (MANDATORY)

> **UNIVERSAL RULE: ZERO HUMAN INTERVENTION**
>
> ALL tasks in this plan MUST be verifiable WITHOUT any human action.
> This is NOT conditional — it applies to EVERY task, regardless of test strategy.
>
> **FORBIDDEN** — acceptance criteria that require:
> - "User manually tests..." / "사용자가 직접 테스트..."
> - "User visually confirms..." / "사용자가 눈으로 확인..."
> - "User interacts with..." / "사용자가 직접 조작..."
> - "Ask user to verify..." / "사용자에게 확인 요청..."
> - ANY step where a human must perform an action
>
> **ALL verification is executed by the agent** using tools (Playwright, interactive_bash, curl, etc.). No exceptions.

### Test Decision
- **Infrastructure exists**: NO (빈 프로젝트)
- **Automated tests**: TDD (pytest)
- **Framework**: pytest, pytest-cov, pytest-qt

### If TDD Enabled

Each TODO follows RED-GREEN-REFACTOR:

**Task Structure**:
1. **RED**: Write failing test first
   - Test file: `tests/path/to/test_module.py`
   - Test command: `pytest tests/path/to/test_module.py -v`
   - Expected: FAIL (test exists, implementation doesn't)
2. **GREEN**: Implement minimum code to pass
   - Command: `pytest tests/path/to/test_module.py -v`
   - Expected: PASS
3. **REFACTOR**: Clean up while keeping green
   - Command: `pytest tests/path/to/test_module.py -v`
   - Expected: PASS (still)

**Test Setup Task (infrastructure doesn't exist)**:
- [ ] 0. Setup Test Infrastructure
  - Install: `pip install pytest pytest-cov pytest-qt ruff mypy`
  - Config: Create `pytest.ini`
  - Verify: `pytest --help` → shows help
  - Example: Create `tests/__init__.py`
  - Verify: `pytest tests/` → 0 tests collected (infrastructure ready)

### Agent-Executed QA Scenarios (MANDATORY — ALL tasks)

> Whether TDD is enabled or not, EVERY task MUST include Agent-Executed QA Scenarios.
> - **With TDD**: QA scenarios complement unit tests at integration/E2E level
> - **Without TDD**: QA scenarios are the PRIMARY verification method
>
> These describe how the executing agent DIRECTLY verifies the deliverable
> by running it — opening browsers, executing commands, sending API requests.
> The agent performs what a human tester would do, but automated via tools.

**Verification Tool by Deliverable Type:**

| Type | Tool | How Agent Verifies |
|------|------|-------------------|
| **Frontend/UI** | interactive_bash (tmux) | Run GUI, check window creation, take screenshots |
| **CLI/Utility** | Bash (python -c) | Import module, call functions, compare output |
| **Library/Module** | Bash (python -c) | Import, call functions, verify behavior |
| **Config/Infra** | Bash (shell commands) | Apply config, run state checks, validate |

**Each Scenario MUST Follow This Format:**

```
Scenario: [Descriptive name — what user action/flow is being verified]
  Tool: [interactive_bash / Bash]
  Preconditions: [What must be true before this scenario runs]
  Steps:
    1. [Exact action with specific command/file]
    2. [Next action with expected intermediate state]
    3. [Assertion with exact expected value]
  Expected Result: [Concrete, observable outcome]
  Failure Indicators: [What would indicate failure]
  Evidence: [Output capture / file path]
```

**Scenario Detail Requirements:**
- **Commands**: Specific command lines with exact paths (`pytest tests/core/test_task_manager.py -v`)
- **Data**: Concrete test data (UUID patterns, JSON structures)
- **Assertions**: Exact values (exit code 0, "PASSED" in output, specific file existence)
- **Timing**: Include wait conditions where relevant (`sleep 3`)
- **Negative Scenarios**: At least ONE failure/error scenario per task
- **Evidence Paths**: Specific file paths (`.sisyphus/evidence/task-N-scenario-name.txt`)

**Anti-patterns (NEVER write scenarios like this):**
- ❌ "Verify the test passes"
- ❌ "Check that the module works correctly"
- ❌ "Test the functionality"
- ❌ "User runs the command and confirms..."

**Write scenarios like this instead:**
- ✅ `pytest tests/core/test_task_manager.py -v → Assert exit code 0 → Assert "PASSED" in output → Assert 5 tests passed`
- ✅ `python -c "from src.utils.string_utils import extract_variables; print(extract_variables('{{name}} is {{age}}'))" → Assert "['name', 'age']" in output`

**Evidence Requirements:**
- Test outputs: Captured for all verification scenarios
- Exit codes: Verified explicitly
- All evidence referenced by specific file path in acceptance criteria

---

## Execution Strategy

### Parallel Execution Waves

> This is a **sequential** development approach following Layer-first pattern.
> No parallel execution — each layer must complete before the next begins.

```
Wave 0 (Setup - Before Wave 1):
└── Task 0: 테스트 인프라 설정

Wave 1 (Start Immediately):
├── Task 1: 프로젝트 설정 (requirements.txt, pytest.ini, run.py)
├── Task 2: 유틸리티 모듈 (string_utils.py, id_generator.py, config.py)
└── Task 3: 데이터 계층 (models.py, database.py, repository.py)

Wave 2 (After Wave 1):
├── Task 4: 코어 로직 - plugin_interface.py, task_manager.py
├── Task 5: 코어 로직 - version_manager.py, template_engine.py
├── Task 6: 코어 로직 - llm_service.py, provider_manager.py

Wave 3 (After Wave 2):
├── Task 7: GUI 프레임워크 (main.py, main_window.py)
└── Task 8: GUI 위젯 (task_navigator.py, prompt_editor.py, result_viewer.py)

Wave 4 (After Wave 3):
├── Task 9: LLM Provider Management UI (provider_list_panel.py, provider_config_panel.py)
└── Task 10: 기능 연동 및 완성

Wave 5 (After Wave 4):
└── Task 11: 최종 검증 및 품질 보증

Critical Path: Task 1 → Task 3 → Task 4 → Task 7 → Task 11
Parallel Speedup: None (sequential development)
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 0 | None | 1 | None |
| 1 | 0 | 2, 3 | None |
| 2 | 1 | 4 | 3 |
| 3 | 1, 2 | 4 | 2 |
| 4 | 2, 3 | 5, 6 | None |
| 5 | 4 | 6 | None |
| 6 | 4, 5 | 7 | None |
| 7 | 6 | 8 | None |
| 8 | 7 | 9 | None |
| 9 | 8 | 10 | None |
| 10 | 9 | 11 | None |
| 11 | 10 | None | None (final) |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 0 | 0 | Test infrastructure setup |
| 1 | 1, 2, 3 | Sequential execution - data and utility layers |
| 2 | 4, 5, 6 | Sequential execution - core logic layer |
| 3 | 7, 8 | Sequential execution - GUI framework |
| 4 | 9, 10 | Sequential execution - feature implementation |
| 5 | 11 | Final verification and quality assurance |

---

## TODOs

> Implementation + Test = ONE Task. Never separate.
> EVERY task MUST have: Recommended Agent Profile + Parallelization info.

- [x] 0. 테스트 인프라 설정

  **What to do**:
  - [ ] pytest 설치 확인 및 설정
  - [ ] pytest.ini 생성 (pytest 설정: test discovery, cov, etc.)
  - [ ] tests/ 디렉토리 생성
  - [ ] tests/__init__.py 생성
  - [ ] 예제 테스트 파일 생성

  **Must NOT do**:
  - [ ] 테스트 프레임워크 설치 (사용자 환경에 이미 존재)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Simple configuration setup, no implementation
  - **Skills**: []
    - No special skills needed - pytest configuration

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (setup)
  - **Blocks**: Task 1
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - None (empty project)

  **API/Type References** (contracts to implement against):
  - pytest docs: https://docs.pytest.org/

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Build, Lint, Test Commands" 섹션 (pytest 설치 및 설정)

  **Documentation References** (specs and requirements):
  - AGENTS.md: "Build, Lint, Test Commands" 섹션

  **External References** (libraries and frameworks):
  - pytest: https://docs.pytest.org/

  **WHY Each Reference Matters** (explain the relevance):
  - AGENTS.md의 "Build, Lint, Test Commands" 섹션을 참조하여 pytest 설정

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] pytest --help → shows help text
  - [ ] pytest.ini contains: testpaths = tests, python_files = test_*.py
  - [ ] tests/__init__.py exists
  - [ ] tests/core/__init__.py exists
  - [ ] Example test file exists

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Test Infrastructure (Bash):**

  \`\`\`
  Scenario: pytest is installed and configured
    Tool: Bash (pytest)
    Preconditions: pytest.ini exists
    Steps:
      1. pytest --help
      2. Assert exit code 0
      3. Assert "pytest" in output
    Expected Result: pytest help shows correctly
    Evidence: Help output captured

  Scenario: pytest configuration is valid
    Tool: Bash (cat)
    Preconditions: pytest.ini exists
    Steps:
      1. cat pytest.ini
      2. Assert "testpaths = tests" in output
      3. Assert "python_files = test_*.py" in output
    Expected Result: pytest.ini contains valid configuration
    Evidence: pytest.ini content captured

  Scenario: test directories exist
    Tool: Bash (test -d)
    Preconditions: pytest.ini exists
    Steps:
      1. test -d tests
      2. Assert exit code 0
      3. test -f tests/__init__.py
      4. Assert exit code 0
    Expected Result: test directories and __init__.py exist
    Evidence: Directory structure verified
  \`\`\`

  **Evidence to Capture:**
  - [ ] pytest help output
  - [ ] pytest.ini content
  - [ ] Directory structure verification

  **Commit**: NO (setup only, no implementation)
- [x] 1. 프로젝트 설정

  **What to do**:
  - [ ] requirements.txt 생성 (PySide6, TinyDB, requests, pytest, pytest-cov, pytest-qt, ruff, mypy)
  - [ ] pytest.ini 생성 (pytest 설정: test discovery, cov, etc.)
  - [ ] run.py 생성 (애플리케이션 진입점)

  **Must NOT do**:
  - [ ] venv 디렉토리 생성 (이미 존재)
  - [ ] requirements.txt에 향후 개선 사항 관련 패키지 추가

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Simple configuration file creation, no complex logic
  - **Skills**: []
    - No special skills needed - basic file creation

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (first task)
  - **Blocks**: Task 2, Task 3
  - **Blocked By**: None (can start immediately)

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - None (empty project)

  **API/Type References** (contracts to implement against):
  - None (configuration files)

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Build, Lint, Test Commands" 섹션 (pytest 설치 및 설정)

  **Documentation References** (specs and requirements):
  - README.md: "기술 스택" 섹션 (PySide6, TinyDB, requests)
  - README.md: "설치 및 실행" 섹션 (requirements.txt, run.py)

  **External References** (libraries and frameworks):
  - PySide6 docs: https://doc.qt.io/qtforpython/
  - pytest docs: https://docs.pytest.org/

  **WHY Each Reference Matters** (explain the relevance):
  - README.md의 "기술 스택" 섹션을 참조하여 필요한 패키지 정의
  - AGENTS.md의 "Build, Lint, Test Commands" 섹션을 참조하여 pytest 설정

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test infrastructure setup: pytest 설치 확인
  - [ ] pytest --help → shows help text
  - [ ] requirements.txt contains: PySide6, TinyDB, requests, pytest, pytest-cov, pytest-qt, ruff, mypy
  - [ ] pytest.ini contains: testpaths = tests, python_files = test_*.py
  - [ ] run.py contains: QApplication entry point

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Configuration (Bash):**

  \`\`\`
  Scenario: requirements.txt contains all required packages
    Tool: Bash (cat)
    Preconditions: requirements.txt exists
    Steps:
      1. cat requirements.txt
      2. Assert "PySide6" in output
      3. Assert "TinyDB" in output
      4. Assert "requests" in output
      5. Assert "pytest" in output
      6. Assert "pytest-cov" in output
      7. Assert "pytest-qt" in output
      8. Assert "ruff" in output
      9. Assert "mypy" in output
    Expected Result: All required packages listed
    Evidence: Output captured

  Scenario: pytest configuration is valid
    Tool: Bash (pytest)
    Preconditions: pytest.ini exists, pytest installed
    Steps:
      1. pytest --help
      2. Assert exit code 0
      3. Assert "pytest" in output
    Expected Result: pytest help shows correctly
    Evidence: Help output captured

  Scenario: run.py is a valid entry point
    Tool: Bash (python -c)
    Preconditions: run.py exists, PySide6 installed
    Steps:
      1. python -c "import sys; sys.path.insert(0, '.'); from run import main"
      2. Assert exit code 0
    Expected Result: run.py can be imported
    Evidence: Import successful
  \`\`\`

  **Evidence to Capture:**
  - [ ] requirements.txt content
  - [ ] pytest.ini content
  - [ ] pytest help output
  - [ ] run.py import test output

  **Commit**: YES
  - Message: `feat: 프로젝트 설정 (requirements.txt, pytest.ini, run.py)`
  - Files: requirements.txt, pytest.ini, run.py
  - Pre-commit: pytest --help

- [x] 2. 유틸리티 모듈

  **What to do**:
  - [ ] src/utils/string_utils.py 생성 (템플릿 변수 파싱: `{{변수명}}` 형식)
  - [ ] src/utils/id_generator.py 생성 (UUID 기반 ID 생성)
  - [ ] src/utils/config.py 생성 (상수 및 설정 값, Magic Number 방지)
  - [ ] src/utils/__init__.py 생성

  **Must NOT do**:
  - [ ] Jinja2 또는 다른 템플릿 엔진 사용 (Python string.Template만 사용)
  - [ ] Magic Number 사용 (모든 상수 config.py에 정의)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Utility modules are pure functions, no complex dependencies
  - **Skills**: []
    - No special skills needed - standard Python

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4
  - **Blocked By**: Task 1

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - None (empty project)

  **API/Type References** (contracts to implement against):
  - Python uuid module: https://docs.python.org/3/library/uuid.html
  - Python string module: https://docs.python.org/3/library/string.html#template-strings

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Code Style Guidelines" 섹션 (Type Hints, Naming Conventions)

  **Documentation References** (specs and requirements):
  - README.md: "템플릿 변수" 섹션 ({{변수명}} 형식)
  - AGENTS.md: "Magic Number 금지" 규칙
  - AGENTS.md: "Utility Functions" 섹션 (utils/ 디렉토리 구조)

  **External References** (libraries and frameworks):
  - Python Template: https://docs.python.org/3/library/string.html#template-strings
  - Python UUID: https://docs.python.org/3/library/uuid.html

  **WHY Each Reference Matters** (explain the relevance):
  - README.md의 "템플릿 변수" 섹션을 참조하여 {{변수명}} 형식 파싱 구현
  - AGENTS.md의 "Magic Number 금지" 규칙을 참조하여 config.py에 상수 정의
  - Python Template 문서를 참조하여 string.Template 확장

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/utils/test_string_utils.py
  - [ ] Test covers: extract_variables() returns ['name', 'age'] from '{{name}} is {{age}}'
  - [ ] Test file created: tests/utils/test_id_generator.py
  - [ ] Test covers: generate_id() returns UUID format
  - [ ] Test file created: tests/utils/test_config.py
  - [ ] Test covers: constants are defined in UPPER_CASE
  - [ ] pytest tests/utils/ -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Utility Functions (Bash):**

  \`\`\`
  Scenario: string_utils.extract_variables() parses {{var}} format
    Tool: Bash (python -c)
    Preconditions: src/utils/string_utils.py exists
    Steps:
      1. python -c "from src.utils.string_utils import extract_variables; print(extract_variables('{{name}} is {{age}}'))"
      2. Assert "['name', 'age']" in output
    Expected Result: Variable names extracted correctly
    Evidence: Output captured

  Scenario: id_generator.generate_id() returns UUID
    Tool: Bash (python -c)
    Preconditions: src/utils/id_generator.py exists
    Steps:
      1. python -c "from src.utils.id_generator import generate_id; uid = generate_id(); print(uid)"
      2. Assert regex pattern [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} matches output
    Expected Result: Valid UUID format returned
    Evidence: UUID output captured

  Scenario: config.py defines constants in UPPER_CASE
    Tool: Bash (grep)
    Preconditions: src/utils/config.py exists
    Steps:
      1. grep "^[A-Z_]* = " src/utils/config.py
      2. Assert output contains multiple constant definitions
    Expected Result: Constants defined with UPPER_CASE naming
    Evidence: grep output captured

  Scenario: No Magic Numbers in code
    Tool: Bash (ruff)
    Preconditions: src/utils/ directory exists
    Steps:
      1. ruff check src/utils/ --select SIM113
      2. Assert exit code 0 (no magic numbers detected)
    Expected Result: No magic numbers in utility modules
    Evidence: ruff output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] string_utils.extract_variables() output
  - [ ] id_generator.generate_id() output
  - [ ] config.py constant definitions
  - [ ] ruff check output

  **Commit**: YES
  - Message: `feat: 유틸리티 모듈 (string_utils, id_generator, config)`
  - Files: src/utils/string_utils.py, src/utils/id_generator.py, src/utils/config.py, src/utils/__init__.py
  - Pre-commit: pytest tests/utils/ -v

---

- [x] 3. 데이터 계층

  **What to do**:
  - [ ] src/data/models.py 생성 (Task, Prompt, Version, ExecutionRecord, Provider 모델)
  - [ ] src/data/database.py 생성 (TinyDB 초기화 및 설정)
  - [ ] src/data/repository.py 생성 (CRUD 레포지토리 인터페이스 및 구현)
  - [ ] src/data/__init__.py 생성
  - [ ] data/ 디렉토리 생성

  **Must NOT do**:
  - [ ] 다른 데이터베이스 사용 (TinyDB만 사용)
  - [ ] 복잡한 쿼리 로직 (단순 TinyDB 쿼리만 사용)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-low`
    - Reason: Data layer with TinyDB, moderate complexity
  - **Skills**: []
    - No special skills needed - standard Python and TinyDB

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 4
  - **Blocked By**: Task 1, Task 2

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - None (empty project)

  **API/Type References** (contracts to implement against):
  - TinyDB docs: https://tinydb.readthedocs.io/

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Modularity", "Independence" 원칙 (레포지토리 인터페이스 정의)

  **Documentation References** (specs and requirements):
  - README.md: "프로젝트 구조" 섹션 (src/data/ 디렉토리)
  - README.md: "코어 API" 섹션 (데이터 모델 사용 예시)

  **External References** (libraries and frameworks):
  - TinyDB: https://tinydb.readthedocs.io/

  **WHY Each Reference Matters** (explain the relevance):
  - README.md의 "코어 API" 섹션을 참조하여 Task, Prompt, Version 모델 정의
  - TinyDB 문서를 참조하여 쿼리 래퍼 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/data/test_models.py
  - [ ] Test covers: Task, Prompt, Version, ExecutionRecord, Provider models have required fields
  - [ ] Test file created: tests/data/test_repository.py
  - [ ] Test covers: CRUD operations (create, read, update, delete)
  - [ ] pytest tests/data/ -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Data Layer (Bash):**

  \`\`\`
  Scenario: database.py initializes TinyDB correctly
    Tool: Bash (python -c)
    Preconditions: src/data/database.py exists, data/ directory exists
    Steps:
      1. python -c "from src.data.database import get_db; db = get_db(); print(type(db))"
      2. Assert "tinydb.database.TinyDB" in output
    Expected Result: TinyDB instance created
    Evidence: Output captured

  Scenario: repository creates task successfully
    Tool: Bash (python -c)
    Preconditions: src/data/repository.py exists, data/prompts.json exists
    Steps:
      1. python -c "from src.data.repository import TaskRepository; from src.data.models import Task; repo = TaskRepository(); task = repo.create(Task(name='Test Task', description='Test Description')); print(task.id)"
      2. Assert regex pattern [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} matches output
    Expected Result: Task created with valid UUID
    Evidence: UUID output captured

  Scenario: database file is created
    Tool: Bash (test -f)
    Preconditions: database.py executed at least once
    Steps:
      1. test -f data/prompts.json
      2. Assert exit code 0
    Expected Result: data/prompts.json exists
    Evidence: File existence verified
  \`\`\`

  **Evidence to Capture:**
  - [ ] database.py initialization output
  - [ ] repository task creation output
  - [ ] data/prompts.json file existence

  **Commit**: YES
  - Message: `feat: 데이터 계층 (models, database, repository)`
  - Files: src/data/models.py, src/data/database.py, src/data/repository.py, src/data/__init__.py
  - Pre-commit: pytest tests/data/ -v

- [x] 4. 코어 로직 - Plugin Interface 및 Task Manager

  **What to do**:
  - [ ] src/core/plugin_interface.py 생성 (플러그인 인터페이스 정의 - ABC)
  - [ ] src/core/task_manager.py 생성 (태스크 CRUD, Task-Prompt 연결 관계)
  - [ ] src/core/__init__.py 생성

  **Must NOT do**:
  - [ ] Task Manager에서 직접 데이터베이스 접근 (Repository 사용)
  - [ ] 플러그인 패턴 적용하지 않음 (확장 포인트 제공)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-low`
    - Reason: Core logic with plugin pattern, moderate complexity
  - **Skills**: []
    - No special skills needed - standard Python with ABC

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 5
  - **Blocked By**: Task 2, Task 3

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - architectral_standard.md: "Main Logic + Plugin Architecture" 섹션 (패턴 예시)

  **API/Type References** (contracts to implement against):
  - src/data/models.py: Task, Prompt 모델
  - src/data/repository.py: TaskRepository 인터페이스

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Modularity", "Independence" 원칙 (Main Logic + Plugin 패턴)

  **Documentation References** (specs and requirements):
  - architectral_standard.md: "Main Logic + Plugin Architecture" 섹션
  - README.md: "코어 API - 태스크 관리" 섹션

  **External References** (libraries and frameworks):
  - Python ABC: https://docs.python.org/3/library/abc.html

  **WHY Each Reference Matters** (explain the relevance):
  - architectral_standard.md의 "Main Logic + Plugin Architecture" 섹션을 참조하여 패턴 구현
  - README.md의 "코어 API" 섹션을 참조하여 Task Manager 인터페이스 정의

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/core/test_task_manager.py
  - [ ] Test covers: create_task() returns Task with valid UUID
  - [ ] Test covers: get_all_tasks() returns list of tasks
  - [ ] Test covers: plugin execution on task creation
  - [ ] pytest tests/core/test_task_manager.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Core Logic (Bash):**

  \`\`\`
  Scenario: TaskManager creates task successfully
    Tool: Bash (python -c)
    Preconditions: src/core/task_manager.py exists, data layer ready
    Steps:
      1. python -c "from src.core.task_manager import TaskManager; tm = TaskManager(); task = tm.create_task('New Task', 'Description'); print(task.id)"
      2. Assert regex pattern [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} matches output
    Expected Result: Task created with valid UUID
    Evidence: UUID output captured

  Scenario: TaskManager lists all tasks
    Tool: Bash (python -c)
    Preconditions: Multiple tasks exist in database
    Steps:
      1. python -c "from src.core.task_manager import TaskManager; tm = TaskManager(); tasks = tm.get_all_tasks(); print(len(tasks))"
      2. Assert output contains numeric value > 0
    Expected Result: Tasks returned successfully
    Evidence: Count output captured

  Scenario: Plugin execution hook is called
    Tool: Bash (python -c)
    Preconditions: plugin interface defined, test plugin registered
    Steps:
      1. python -c "from src.core.task_manager import TaskManager; tm = TaskManager(); tm.register_plugin(TestPlugin()); task = tm.create_task('Test', 'Desc'); print('plugin_called' if hasattr(TestPlugin, 'last_result') else 'not_called')"
      2. Assert "plugin_called" in output
    Expected Result: Plugin hook executed
    Evidence: Plugin execution status captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] Task creation UUID output
  - [ ] Task list count output
  - [ ] Plugin execution status

  **Commit**: YES
  - Message: `feat: 코어 로직 - Plugin Interface 및 Task Manager`
  - Files: src/core/plugin_interface.py, src/core/task_manager.py, src/core/__init__.py
  - Pre-commit: pytest tests/core/test_task_manager.py -v

- [x] 5. 코어 로직 - Version Manager 및 Template Engine

  **What to do**:
  - [ ] src/core/version_manager.py 생성 (버전 생성, 타임라인 조회, 복구 - 단순 스냅샷)
  - [ ] src/core/template_engine.py 생성 ({{변수명}} 형식 파싱 및 렌더링 - Python string.Template 확장)
  - [ ] 첫 번째 버전 자동 생성 로직 구현

  **Must NOT do**:
  - [ ] 델타 저장 방식 (단순 스냅샷만 사용)
  - [ ] Jinja2 사용 (Python string.Template만 사용)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-low`
    - Reason: Core logic with template engine, moderate complexity
  - **Skills**: []
    - No special skills needed - standard Python with string.Template

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - src/core/plugin_interface.py: 플러그인 인터페이스
  - src/utils/string_utils.py: 템플릿 변수 파싱 유틸리티

  **API/Type References** (contracts to implement against):
  - src/data/models.py: Version 모델
  - src/data/repository.py: VersionRepository 인터페이스

  **Test References** (testing patterns to follow):
  - architectral_standard.md: "Main Logic + Plugin Architecture" 섹션 (확장 포인트)

  **Documentation References** (specs and requirements):
  - README.md: "버전 관리" 섹션 (단순 스냅샷)
  - README.md: "템플릿 변수" 섹션 ({{변수명}} 형식)

  **External References** (libraries and frameworks):
  - Python string.Template: https://docs.python.org/3/library/string.html#template-strings

  **WHY Each Reference Matters** (explain the relevance):
  - README.md의 "버전 관리" 섹션을 참조하여 단순 스냅샷 방식 구현
  - README.md의 "템플릿 변수" 섹션을 참조하여 {{변수명}} 형식 파싱
  - Python string.Template 문서를 참조하여 템플릿 엔진 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/core/test_version_manager.py
  - [ ] Test covers: create_version() returns Version with version_number
  - [ ] Test covers: get_version_timeline() returns list of versions
  - [ ] Test file created: tests/core/test_template_engine.py
  - [ ] Test covers: render_template('{{name}} is {{age}}', {'name': 'John', 'age': '30'}) returns 'John is 30'
  - [ ] pytest tests/core/test_version_manager.py tests/core/test_template_engine.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Version Manager (Bash):**

  \`\`\`
  Scenario: VersionManager creates version successfully
    Tool: Bash (python -c)
    Preconditions: src/core/version_manager.py exists, task exists
    Steps:
      1. python -c "from src.core.version_manager import VersionManager; vm = VersionManager(); version = vm.create_version('task-id', 'Prompt content'); print(version.version_number)"
      2. Assert output equals "1" (first version)
    Expected Result: Version created with version_number = 1
    Evidence: Version number output captured

  Scenario: VersionManager returns version timeline
    Tool: Bash (python -c)
    Preconditions: Multiple versions exist for a prompt
    Steps:
      1. python -c "from src.core.version_manager import VersionManager; vm = VersionManager(); timeline = vm.get_version_timeline('prompt-id'); print(len(timeline))"
      2. Assert output contains numeric value >= 1
    Expected Result: Timeline returned with at least one version
    Evidence: Timeline length output captured

  Scenario: TemplateEngine renders {{var}} format
    Tool: Bash (python -c)
    Preconditions: src/core/template_engine.py exists
    Steps:
      1. python -c "from src.core.template_engine import TemplateEngine; te = TemplateEngine(); result = te.render('{{name}} is {{age}}', {'name': 'John', 'age': '30'}); print(result)"
      2. Assert "John is 30" in output
    Expected Result: Template rendered with variable substitution
    Evidence: Rendered output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] Version creation output
  - [ ] Version timeline output
  - [ ] Template rendering output

  **Commit**: YES
  - Message: `feat: 코어 로직 - Version Manager 및 Template Engine`
  - Files: src/core/version_manager.py, src/core/template_engine.py
  - Pre-commit: pytest tests/core/test_version_manager.py tests/core/test_template_engine.py -v

- [ ] 6. 코어 로직 - LLM Service 및 Provider Manager

  **What to do**:
  - [ ] src/core/llm_service.py 생성 (OpenAI Compatible API 호출, 메트릭 수집, 플러그인 확장 포인트)
  - [ ] src/core/provider_manager.py 생성 (Provider CRUD, 연결 테스트, 플러그인 확장 포인트)
  - [ ] 비동기 API 호출 준비 (GUI 비동기 처리를 위한 인터페이스)

  **Must NOT do**:
  - [ ] 실제 LLM API 테스트 (mock 사용)
  - [ ] Provider 다양화 (README.md "향후 개선 사항" 제외)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-low`
    - Reason: Core logic with API integration, moderate complexity
  - **Skills**: []
    - No special skills needed - standard Python with requests

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 7
  - **Blocked By**: Task 4

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - src/core/plugin_interface.py: 플러그인 인터페이스
  - src/data/models.py: Provider, ExecutionRecord 모델

  **API/Type References** (contracts to implement against):
  - src/data/models.py: Provider, ExecutionRecord 모델
  - src/data/repository.py: ProviderRepository, ExecutionRecordRepository 인터페이스

  **Test References** (testing patterns to follow):
  - README.md: "LLM 설정" 섹션 (OpenAI Compatible API)

  **Documentation References** (specs and requirements):
  - README.md: "LLM 통합" 섹션 (OpenAI Compatible API)
  - README.md: "성능 메트릭" 섹션 (응답 시간, 토큰 사용량)

  **External References** (libraries and frameworks):
  - requests docs: https://docs.python-requests.org/

  **WHY Each Reference Matters** (explain the relevance):
  - README.md의 "LLM 통합" 섹션을 참조하여 OpenAI Compatible API 구현
  - README.md의 "성능 메트릭" 섹션을 참조하여 메트릭 수집 구현
  - requests 문서를 참조하여 API 호출 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/core/test_llm_service.py
  - [ ] Test covers: call_llm() returns mock response (using unittest.mock)
  - [ ] Test covers: metrics collection (response_time, tokens)
  - [ ] Test file created: tests/core/test_provider_manager.py
  - [ ] Test covers: create_provider() returns Provider with valid UUID
  - [ ] Test covers: test_connection() returns success/failure (mock API)
  - [ ] pytest tests/core/test_llm_service.py tests/core/test_provider_manager.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — LLM Service (Bash):**

  \`\`\`
  Scenario: LLMService calls API with mock
    Tool: Bash (python -c)
    Preconditions: src/core/llm_service.py exists, unittest.mock imported
    Steps:
      1. python -c "from unittest.mock import patch; from src.core.llm_service import LLMService; with patch('requests.post') as mock_post: mock_post.return_value.json.return_value = {'choices': [{'message': {'content': 'Test response'}}]}; ls = LLMService('http://test.api'); resp = ls.call_llm('Test prompt', model='test-model'); print(resp)"
      2. Assert "Test response" in output
    Expected Result: Mock API call returns response
    Evidence: Response output captured

  Scenario: LLMService collects metrics
    Tool: Bash (python -c)
    Preconditions: src/core/llm_service.py exists, mock API set up
    Steps:
      1. python -c "from unittest.mock import patch; from src.core.llm_service import LLMService; with patch('requests.post') as mock_post: mock_post.return_value.json.return_value = {'choices': [{'message': {'content': 'Test'}}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 20}}; ls = LLMService('http://test.api'); resp, metrics = ls.call_llm_with_metrics('Test'); print(f'Tokens: {metrics[\"total_tokens\"]}')"
      2. Assert "Tokens: 30" in output
    Expected Result: Metrics collected correctly
    Evidence: Metrics output captured

  Scenario: ProviderManager creates provider
    Tool: Bash (python -c)
    Preconditions: src/core/provider_manager.py exists
    Steps:
      1. python -c "from src.core.provider_manager import ProviderManager; pm = ProviderManager(); provider = pm.create_provider('Test Provider', 'http://test.api', 'test-key'); print(provider.id)"
      2. Assert regex pattern [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12} matches output
    Expected Result: Provider created with valid UUID
    Evidence: UUID output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] LLM service mock response output
  - [ ] LLM service metrics output
  - [ ] Provider creation UUID output

  **Commit**: YES
  - Message: `feat: 코어 로직 - LLM Service 및 Provider Manager`
  - Files: src/core/llm_service.py, src/core/provider_manager.py
  - Pre-commit: pytest tests/core/test_llm_service.py tests/core/test_provider_manager.py -v

- [x] 7. GUI 프레임워크

  **What to do**:
  - [ ] src/gui/main.py 생성 (애플리케이션 진입점, QApplication 설정)
  - [ ] src/gui/main_window.py 생성 (메인 윈도우 프레임, 3단 레이아웃 QSplitter)
  - [ ] Modern Dark Mode 테마 적용 (디자인 스펙 색상)
  - [ ] src/gui/__init__.py 생성

  **Must NOT do**:
  - [ ] 디자인 스펙과 다른 색상/레이아웃 사용
  - [ ] QSplitter 대신 다른 레이아웃 사용

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `visual-engineering`
    - Reason: GUI framework with PySide6, UI/UX design
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Modern Dark Mode 테마 적용, 3단 레이아웃 디자인

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 8
  - **Blocked By**: Task 6

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - None (empty project)

  **API/Type References** (contracts to implement against):
  - PySide6 docs: https://doc.qt.io/qtforpython/
  - QSplitter: https://doc.qt.io/qtforpython/PySide6.QtWidgets/QSplitter.html

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Code Style Guidelines" 섹션 (Imports, Type Hints)
  - prompt_manager_main_dashboard.ui: "1. 디자인 철학 및 테마" 섹션 (색상, 폰트)

  **Documentation References** (specs and requirements):
  - prompt_manager_main_dashboard.ui: "1. 디자인 철학 및 테마" 섹션 (Modern Dark Mode, 색상)
  - prompt_manager_main_dashboard.ui: "2. 레이아웃 구조" 섹션 (3-Column Architecture)

  **External References** (libraries and frameworks):
  - PySide6: https://doc.qt.io/qtforpython/
  - pytest-qt: https://pytest-qt.readthedocs.io/

  **WHY Each Reference Matters** (explain the relevance):
  - prompt_manager_main_dashboard.ui의 "디자인 철학 및 테마" 섹션을 참조하여 Modern Dark Mode 적용
  - prompt_manager_main_dashboard.ui의 "레이아웃 구조" 섹션을 참조하여 3단 레이아웃 구현
  - PySide6 문서를 참조하여 QSplitter 사용법 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/gui/test_main_window.py
  - [ ] Test covers: MainWindow creates successfully
  - [ ] Test covers: QSplitter layout has 3 panels
  - [ ] pytest-qt tests/gui/test_main_window.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — GUI Framework (interactive_bash):**

  \`\`\`
  Scenario: MainWindow creates successfully
    Tool: interactive_bash (tmux)
    Preconditions: src/gui/main.py exists, PySide6 installed
    Steps:
      1. tmux new-session: python src/gui/main.py
      2. Wait 3 seconds for window to open
      3. ps aux | grep "python src/gui/main.py" | grep -v grep
      4. Assert process exists (exit code 0)
      5. Send "Ctrl+C" to kill
    Expected Result: GUI window opens
    Evidence: Process existence verified

  Scenario: MainWindow has QSplitter with 3 panels
    Tool: Bash (python -c)
    Preconditions: src/gui/main_window.py exists
    Steps:
      1. python -c "from PySide6.QtWidgets import QApplication; from src.gui.main_window import MainWindow; app = QApplication([]); mw = MainWindow(); splitter = mw.findChild(type(mw).__bases__[0], 'mainSplitter'); print(f'Panel count: {len(splitter)}')"
      2. Assert "Panel count: 3" in output
    Expected Result: QSplitter has 3 panels
    Evidence: Panel count output captured

  Scenario: Dark Mode theme colors applied
    Tool: Bash (python -c)
    Preconditions: src/gui/main_window.py exists
    Steps:
      1. python -c "from PySide6.QtWidgets import QApplication; from src.gui.main_window import MainWindow; app = QApplication([]); mw = MainWindow(); palette = mw.palette(); bg = palette.color(mw.backgroundRole()); print(f'Background: #{bg.red():02x}{bg.green():02x}{bg.blue():02x}')"
      2. Assert "Background: #1e1e1e" in output (or similar dark hex)
    Expected Result: Dark Mode background color applied
    Evidence: Background color output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] GUI window process existence
  - [ ] QSplitter panel count
  - [ ] Dark Mode background color

  **Commit**: YES
  - Message: `feat: GUI 프레임워크 (main.py, main_window.py)`
  - Files: src/gui/main.py, src/gui/main_window.py, src/gui/__init__.py
  - Pre-commit: pytest-qt tests/gui/test_main_window.py -v

- [x] 8. GUI 위젯 (Task Navigator, Prompt Editor, Result Viewer)

  **What to do**:
  - [ ] src/gui/widgets/task_navigator.py 생성 (태스크 리스트, 검색, New Task 버튼)
  - [ ] src/gui/widgets/prompt_editor.py 생성 (System/User Prompt, 변수 Quick-Panel, 버전 타임라인)
  - [ ] src/gui/widgets/result_viewer.py 생성 (결과 표시, 이력/비교/메트릭 탭)
  - [ ] src/gui/widgets/__init__.py 생성
  - [ ] 변수 자동 감지 및 동기화 구현

  **Must NOT do**:
  - [ ] 디자인 스펙과 다른 레이아웃/기능 구현
  - [ ] 접기/펴기 기능 구현 안 함 (디자인 스펙에 포함)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `visual-engineering`
    - Reason: GUI widgets with complex UI components
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Widget design, variable detection UI, version timeline UI

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 9
  - **Blocked By**: Task 7

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - src/gui/main_window.py: 메인 윈도우 프레임
  - src/core/task_manager.py: Task Manager 인터페이스
  - src/core/version_manager.py: Version Manager 인터페이스
  - src/core/template_engine.py: Template Engine 인터페이스

  **API/Type References** (contracts to implement against):
  - PySide6 QListWidget, QPlainTextEdit, QTabWidget, QDockWidget
  - prompt_manager_main_dashboard.ui: 위젯별 세부 스펙

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Modularity", "Independence" 원칙 (위젯 독립성)
  - prompt_manager_main_dashboard.ui: "3. 핵심 사용자 경험 (UX) 디테일" 섹션

  **Documentation References** (specs and requirements):
  - prompt_manager_main_dashboard.ui: "좌측 패널: Task Navigator" 섹션
  - prompt_manager_main_dashboard.ui: "중앙 패널: Prompt Editor" 섹션
  - prompt_manager_main_dashboard.ui: "우측 패널: Result Viewer" 섹션

  **External References** (libraries and frameworks):
  - PySide6 Widgets: https://doc.qt.io/qtforpython/PySide6.QtWidgets/

  **WHY Each Reference Matters** (explain the relevance):
  - prompt_manager_main_dashboard.ui의 각 패널 섹션을 참조하여 위젯 구현
  - src/core/*_manager.py의 인터페이스를 참조하여 위젯이 코어 로직 통신

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/gui/widgets/test_task_navigator.py
  - [ ] Test covers: task list displays tasks
  - [ ] Test file created: tests/gui/widgets/test_prompt_editor.py
  - [ ] Test covers: variable detection extracts {{var}}
  - [ ] Test file created: tests/gui/widgets/test_result_viewer.py
  - [ ] Test covers: result displays text
  - [ ] pytest-qt tests/gui/widgets/ -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — GUI Widgets (interactive_bash):**

  \`\`\`
  Scenario: TaskNavigator displays tasks
    Tool: interactive_bash (tmux)
    Preconditions: GUI running, tasks exist
    Steps:
      1. tmux send-keys: "python src/gui/main.py" Enter
      2. Wait 3 seconds for window to open
      3. Send: "Ctrl+Shift+F1" (debug hotkey to log task count)
      4. Read from log file: .sisyphus/evidence/task-navigator.log
      5. Assert "Task count: X" in log (X > 0)
    Expected Result: Task list shows tasks
    Evidence: Task count log captured

  Scenario: PromptEditor detects {{var}} variables
    Tool: Bash (python -c)
    Preconditions: src/gui/widgets/prompt_editor.py exists
    Steps:
      1. python -c "from src.gui.widgets.prompt_editor import PromptEditor; pe = PromptEditor(); vars = pe.extract_variables('Hello {{name}}, you are {{age}}'); print(vars)"
      2. Assert "['name', 'age']" in output
    Expected Result: Variables extracted from template
    Evidence: Variable list output captured

  Scenario: ResultViewer displays result
    Tool: Bash (python -c)
    Preconditions: src/gui/widgets/result_viewer.py exists
    Steps:
      1. python -c "from src.gui.widgets.result_viewer import ResultViewer; rv = ResultViewer(); rv.set_result('Test LLM response'); print(rv.get_result())"
      2. Assert "Test LLM response" in output
    Expected Result: Result displayed correctly
    Evidence: Result text output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] Task navigator task count log
  - [ ] Prompt editor variable extraction output
  - [ ] Result viewer display output

  **Commit**: YES
  - Message: `feat: GUI 위젯 (Task Navigator, Prompt Editor, Result Viewer)`
  - Files: src/gui/widgets/task_navigator.py, src/gui/widgets/prompt_editor.py, src/gui/widgets/result_viewer.py, src/gui/widgets/__init__.py
  - Pre-commit: pytest-qt tests/gui/widgets/ -v

- [x] 9. LLM Provider Management UI

  **What to do**:
  - [ ] src/gui/widgets/provider_list_panel.py 생성 (좌측 Provider List Panel, 상태 표시등)
  - [ ] src/gui/widgets/provider_config_panel.py 생성 (우측 Config Detail Panel, General Info/Connection Settings/Default Model Parameters)
  - [ ] src/gui/widgets/provider_dialog.py 생성 (추가/편집 다이얼로그)
  - [ ] Test Connection 비동기 통신 구현

  **Must NOT do**:
  - [ ] 디자인 스펙과 다른 레이아웃/기능 구현
  - [ ] Test Connection 동기 통신 (비동기로 구현)

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `visual-engineering`
    - Reason: GUI widgets with async API communication
  - **Skills**: [`frontend-ui-ux`]
    - `frontend-ui-ux`: Split-View 레이아웃, 비동기 UI 업데이트

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 10
  - **Blocked By**: Task 8

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - src/core/provider_manager.py: Provider Manager 인터페이스
  - src/gui/widgets/task_navigator.py: 리스트 위젯 패턴

  **API/Type References** (contracts to implement against):
  - llm_provider_management_design_specification.md: 세부 UI 스펙

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Code Style Guidelines" 섹션 (Type Hints, Error Handling)
  - llm_provider_management_design_specification.md: "4. PySide6 구현 가이드라인" 섹션

  **Documentation References** (specs and requirements):
  - llm_provider_management_design_specification.md: "2. 레이아웃 구조" 섹션
  - llm_provider_management_design_specification.md: "3. 인터렉션 디테일 (UX)" 섹션

  **External References** (libraries and frameworks):
  - PySide6 QThread, QNetworkAccessManager: https://doc.qt.io/qtforpython/

  **WHY Each Reference Matters** (explain the relevance):
  - llm_provider_management_design_specification.md의 "레이아웃 구조" 섹션을 참조하여 Split-View 구현
  - "PySide6 구현 가이드라인" 섹션을 참조하여 비동기 통신 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/gui/widgets/test_provider_list_panel.py
  - [ ] Test covers: provider list displays providers
  - [ ] Test file created: tests/gui/widgets/test_provider_config_panel.py
  - [ ] Test covers: config panel shows provider details
  - [ ] pytest-qt tests/gui/widgets/test_provider_*.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Provider Management UI (interactive_bash):**

  \`\`\`
  Scenario: ProviderListPanel displays providers
    Tool: interactive_bash (tmux)
    Preconditions: GUI running, providers exist
    Steps:
      1. tmux send-keys: "python src/gui/main.py" Enter
      2. Wait 3 seconds for window to open
      3. Send: "Ctrl+Shift+F2" (debug hotkey to log provider count)
      4. Read from log file: .sisyphus/evidence/provider-list.log
      5. Assert "Provider count: X" in log (X > 0)
    Expected Result: Provider list shows providers
    Evidence: Provider count log captured

  Scenario: ProviderConfigPanel shows details
    Tool: Bash (python -c)
    Preconditions: src/gui/widgets/provider_config_panel.py exists, provider selected
    Steps:
      1. python -c "from src.gui.widgets.provider_config_panel import ProviderConfigPanel; pcp = ProviderConfigPanel(); pcp.set_provider({'name': 'Test Provider', 'api_url': 'http://test.api'}); print(pcp.get_provider_name())"
      2. Assert "Test Provider" in output
    Expected Result: Config panel shows provider name
    Evidence: Provider name output captured

  Scenario: Test Connection is async (mock)
    Tool: Bash (python -c)
    Preconditions: src/gui/widgets/provider_config_panel.py exists
    Steps:
      1. python -c "from unittest.mock import patch; from src.gui.widgets.provider_config_panel import ProviderConfigPanel; pcp = ProviderConfigPanel(); with patch('src.core.provider_manager.ProviderManager.test_connection', return_value=True): print(pcp.test_connection())"
      2. Assert "True" in output
    Expected Result: Test connection returns success (async ready)
    Evidence: Connection test output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] Provider list count log
  - [ ] Config panel provider name output
  - [ ] Connection test output

  **Commit**: YES
  - Message: `feat: LLM Provider Management UI`
  - Files: src/gui/widgets/provider_list_panel.py, src/gui/widgets/provider_config_panel.py, src/gui/widgets/provider_dialog.py
  - Pre-commit: pytest-qt tests/gui/widgets/test_provider_*.py -v

- [ ] 10. 기능 연동 및 완성

  **What to do**:
  - [ ] 메인 윈도우 시그널/슬롯 연결 (Task Navigator → Prompt Editor → Result Viewer)
  - [ ] 메뉴바, 툴바 액션 연결
  - [ ] 버전 타임라인 드롭다운 구현
  - [ ] RUN 버튼 기능 구현 (프롬프트 전송, 결과 표시)
  - [ ] 접기/펴기 기능 구현

  **Must NOT do**:
  - [ ] 디자인 스펙과 다른 기능 구현
  - [ ] README.md "향후 개선 사항" 기능 추가

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `unspecified-low`
    - Reason: Feature integration and completion, moderate complexity
  - **Skills**: []
    - No special skills needed - signal/slot wiring

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 11
  - **Blocked By**: Task 9

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - src/gui/main_window.py: 메인 윈도우 프레임
  - src/gui/widgets/task_navigator.py: Task Navigator 위젯
  - src/gui/widgets/prompt_editor.py: Prompt Editor 위젯
  - src/gui/widgets/result_viewer.py: Result Viewer 위젯

  **API/Type References** (contracts to implement against):
  - PySide6 Signal/Slot: https://doc.qt.io/qtforpython/PySide6.QtCore/Signal.html

  **Test References** (testing patterns to follow):
  - prompt_manager_main_dashboard.ui: "3. 핵심 사용자 경험 (UX) 디테일" 섹션 (변수 감지, 버전 타임라인, 접기/펴기)

  **Documentation References** (specs and requirements):
  - prompt_manager_main_dashboard.ui: "3. 핵심 사용자 경험 (UX) 디테일" 섹션
  - README.md: "사용 가이드" 섹션 (사용자 워크플로우)

  **External References** (libraries and frameworks):
  - PySide6 Signal/Slot: https://doc.qt.io/qtforpython/PySide6.QtCore/Signal.html

  **WHY Each Reference Matters** (explain the relevance):
  - prompt_manager_main_dashboard.ui의 "핵심 사용자 경험" 섹션을 참조하여 기능 연동
  - README.md의 "사용 가이드" 섹션을 참조하여 사용자 워크플로우 구현

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] Test file created: tests/gui/test_integration.py
  - [ ] Test covers: task selection updates prompt editor
  - [ ] Test covers: RUN button sends prompt and displays result (mock)
  - [ ] pytest-qt tests/gui/test_integration.py -v → PASS (all tests)

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Feature Integration (interactive_bash):**

  \`\`\`
  Scenario: Task selection updates prompt editor
    Tool: interactive_bash (tmux)
    Preconditions: GUI running, tasks with prompts exist
    Steps:
      1. tmux send-keys: "python src/gui/main.py" Enter
      2. Wait 3 seconds for window to open
      3. Send: "Ctrl+Shift+F3" (debug hotkey to select first task)
      4. Send: "Ctrl+Shift+F4" (debug hotkey to log prompt editor content)
      5. Read from log file: .sisyphus/evidence/integration.log
      6. Assert "Prompt content: " in log (not empty)
    Expected Result: Task selection updates prompt editor
    Evidence: Integration log captured

  Scenario: RUN button sends prompt (mock)
    Tool: Bash (python -c)
    Preconditions: src/gui/main_window.py exists, mock LLM service
    Steps:
      1. python -c "from unittest.mock import patch; from src.gui.main_window import MainWindow; from PySide6.QtWidgets import QApplication; app = QApplication([]); mw = MainWindow(); with patch('src.core.llm_service.LLMService.call_llm', return_value='Mock LLM response'): mw.run_prompt(); print('Prompt sent')"
      2. Assert "Prompt sent" in output
    Expected Result: RUN button triggers LLM call
    Evidence: Prompt sent output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] Integration log (task selection)
  - [ ] Prompt sent output

  **Commit**: YES
  - Message: `feat: 기능 연동 및 완성`
  - Files: src/gui/main_window.py (updated)
  - Pre-commit: pytest-qt tests/gui/test_integration.py -v

- [x] 11. 최종 검증 및 품질 보증

  **What to do**:
  - [ ] LSP Diagnostics 검사 (에러 없음 확인)
  - [ ] 코드 리팩토링 (파일당 500줄 준수)
  - [ ] 문서화 완료 ([overview], [description] 태그)
  - [ ] lint 검사 (ruff check src/ tests/)
  - [ ] 타입 검사 (mypy src/)
  - [ ] 커버리지 검사 (pytest tests/ --cov=src --cov-report=html, 80% 이상)

  **Must NOT do**:
  - [ ] 파일 길이 500줄 초과 허용
  - [ ] Linting/Typing 에러 무시

  **Recommended Agent Profile**:
  > Select category + skills based on task domain. Justify each choice.
  - **Category**: `quick`
    - Reason: Final verification and quality assurance, no implementation
  - **Skills**: []
    - No special skills needed - linting, type checking

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (final task)
  - **Blocks**: None (final)
  - **Blocked By**: Task 10

  **References** (CRITICAL - Be Exhaustive):

  > The executor has NO context from your interview. References are their ONLY guide.
  > Each reference must answer: "What should I look at and WHY?"

  **Pattern References** (existing code to follow):
  - AGENTS.md: "File Documentation" 규칙 ([overview], [description] 태그)

  **API/Type References** (contracts to implement against):
  - None (verification only)

  **Test References** (testing patterns to follow):
  - AGENTS.md: "Build, Lint, Test Commands" 섹션

  **Documentation References** (specs and requirements):
  - AGENTS.md: "File Documentation" 섹션
  - AGENTS.md: "Build, Lint, Test Commands" 섹션

  **External References** (libraries and frameworks):
  - ruff: https://docs.astral.sh/ruff/
  - mypy: https://mypy.readthedocs.io/

  **WHY Each Reference Matters** (explain the relevance):
  - AGENTS.md의 "File Documentation" 섹션을 참조하여 [overview], [description] 태그 확인
  - AGENTS.md의 "Build, Lint, Test Commands" 섹션을 참조하여 검증 명령어 실행

  **Acceptance Criteria**:

  > **AGENT-EXECUTABLE VERIFICATION ONLY** — No human action permitted.
  > Every criterion MUST be verifiable by running a command or using a tool.
  > REPLACE all placeholders with actual values from task context.

  **If TDD (tests enabled):**
  - [ ] LSP Diagnostics: 0 errors
  - [ ] ruff check src/ tests/ → exit code 0
  - [ ] mypy src/ → exit code 0
  - [ ] pytest tests/ --cov=src --cov-report=html → coverage >= 80%
  - [ ] All files: wc -l src/**/*.py → max 500 lines per file

  **Agent-Executed QA Scenarios (MANDATORY — per-scenario, ultra-detailed):**

  > Write MULTIPLE named scenarios per task: happy path AND failure cases.
  > Each scenario = exact tool + steps with real commands/data + evidence path.

  **Example — Final Verification (Bash):**

  \`\`\`
  Scenario: All tests pass
    Tool: Bash (pytest)
    Preconditions: All implementation complete
    Steps:
      1. pytest tests/ -v
      2. Assert exit code 0
      3. Assert "X passed" in output (X is number of tests)
    Expected Result: All tests pass
    Evidence: Test output captured

  Scenario: Linting passes
    Tool: Bash (ruff)
    Preconditions: All code written
    Steps:
      1. ruff check src/ tests/
      2. Assert exit code 0
    Expected Result: No linting errors
    Evidence: ruff output captured

  Scenario: Type checking passes
    Tool: Bash (mypy)
    Preconditions: All code written
    Steps:
      1. mypy src/
      2. Assert exit code 0
    Expected Result: No type errors
    Evidence: mypy output captured

  Scenario: Coverage is 80%+
    Tool: Bash (pytest)
    Preconditions: All tests written
    Steps:
      1. pytest tests/ --cov=src --cov-report=term
      2. Assert "TOTAL" in output
      3. Assert coverage percentage >= 80
    Expected Result: Coverage >= 80%
    Evidence: Coverage report captured

  Scenario: No file exceeds 500 lines
    Tool: Bash (wc -l)
    Preconditions: All Python files in src/
    Steps:
      1. find src/ -name "*.py" -exec wc -l {} \; | sort -rn
      2. Assert no line count > 500
    Expected Result: All files <= 500 lines
    Evidence: Line count output captured

  Scenario: All files have [overview] and [description]
    Tool: Bash (grep)
    Preconditions: All Python files in src/
    Steps:
      1. grep -L "^\[overview\]" src/**/*.py
      2. Assert output is empty (all files have [overview])
      3. grep -L "^\[description\]" src/**/*.py
      4. Assert output is empty (all files have [description])
    Expected Result: All files documented
    Evidence: grep output captured
  \`\`\`

  **Evidence to Capture:**
  - [ ] pytest test output
  - [ ] ruff linting output
  - [ ] mypy type checking output
  - [ ] coverage report
  - [ ] line count output
  - [ ] documentation check output

  **Commit**: NO (final verification, no code changes)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 0 | NO (setup only, no implementation) | pytest.ini, tests/__init__.py | pytest --help |
| 1 | `feat: 프로젝트 설정 (requirements.txt, pytest.ini, run.py)` | requirements.txt, pytest.ini (updated), run.py | pytest --help |
| 2 | `feat: 유틸리티 모듈 (string_utils, id_generator, config)` | src/utils/*.py, src/utils/__init__.py | pytest tests/utils/ -v |
| 3 | `feat: 데이터 계층 (models, database, repository)` | src/data/*.py, src/data/__init__.py | pytest tests/data/ -v |
| 4 | `feat: 코어 로직 - Plugin Interface 및 Task Manager` | src/core/plugin_interface.py, src/core/task_manager.py, src/core/__init__.py | pytest tests/core/test_task_manager.py -v |
| 5 | `feat: 코어 로직 - Version Manager 및 Template Engine` | src/core/version_manager.py, src/core/template_engine.py | pytest tests/core/test_*.py -v |
| 6 | `feat: 코어 로직 - LLM Service 및 Provider Manager` | src/core/llm_service.py, src/core/provider_manager.py | pytest tests/core/test_*.py -v |
| 7 | `feat: GUI 프레임워크 (main.py, main_window.py)` | src/gui/main.py, src/gui/main_window.py, src/gui/__init__.py | pytest-qt tests/gui/test_main_window.py -v |
| 8 | `feat: GUI 위젯 (Task Navigator, Prompt Editor, Result Viewer)` | src/gui/widgets/task_navigator.py, src/gui/widgets/prompt_editor.py, src/gui/widgets/result_viewer.py, src/gui/widgets/__init__.py | pytest-qt tests/gui/widgets/ -v |
| 9 | `feat: LLM Provider Management UI` | src/gui/widgets/provider_list_panel.py, src/gui/widgets/provider_config_panel.py, src/gui/widgets/provider_dialog.py | pytest-qt tests/gui/widgets/test_provider_*.py -v |
| 10 | `feat: 기능 연동 및 완성` | src/gui/main_window.py (updated) | pytest-qt tests/gui/test_integration.py -v |
| 11 | NO (final verification) | None | All verification commands |

---

## Success Criteria

### Verification Commands
```bash
# 단위 테스트
pytest tests/ -v
# Expected: All tests pass (X passed)

# 커버리지 검사
pytest tests/ --cov=src --cov-report=html --cov-report=term
# Expected: Coverage >= 80%

# Linting 검사
ruff check src/ tests/
# Expected: No errors

# 타입 검사
mypy src/
# Expected: No errors

# 파일 길이 검사
find src/ -name "*.py" -exec wc -l {} \; | sort -rn
# Expected: No file > 500 lines

# 문서화 검사
grep -L "^\[overview\]" src/**/*.py
grep -L "^\[description\]" src/**/*.py
# Expected: No output (all files documented)

# 애플리케이션 실행 테스트
python run.py &
APP_PID=$!
sleep 3
ps -p $APP_PID > /dev/null
# Assert: exit code 0
kill $APP_PID
```

### Final Checklist
- [ ] 모든 테스트 통과 (pytest tests/ -v)
- [ ] 커버리지 80% 이상 (pytest --cov=src)
- [ ] Linting 통과 (ruff check src/ tests/)
- [ ] 타입 검사 통과 (mypy src/)
- [ ] 모든 파일 500줄 이내 (wc -l src/**/*.py)
- [ ] 모든 파일에 [overview], [description] 태그 포함
- [ ] 애플리케이션 실행 가능 (python run.py)
- [ ] "Must Have" 모두 포함
- [ ] "Must NOT Have" 모두 제외
- [ ] AGENTS.md 아키텍처 원칙 준수
- [ ] 디자인 스펙 엄격 준수
