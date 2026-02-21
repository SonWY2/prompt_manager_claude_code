# Prompt Editor Version Name Input & Persistence Plan

## TL;DR
> **Quick Summary**: 새 버전 생성 시 사용자가 입력한 이름이 빈 값/중복 없이 저장·표시되도록 `MainWindow`와 `VersionManager`를 정합해 수정하고, 관련 테스트를 확장합니다.

> **Deliverables**
> - 새 버전명 직접 입력 유효성(필수 입력/중복 금지) 강제
> - 에디터에서 입력한 이름이 버전 저장값으로 정확 반영
> - 버전 목록/상태바/선택 표시가 입력명을 우선 사용
> - 핵심 GUI + 코어 테스트 확장

> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves
> **Critical Path**: 검증 로직 강화 -> GUI 바인딩 수정 -> 테스트 확장 -> 회귀 검증

---

## Context

### Original Request
- Prompt Editor에서 새로 추가되는 버전의 이름을 사용자가 직접 입력
- UI에서 새 정책(빈값 불가/중복 불가) 반영
- 입력값이 버전 생성·표시·조회 흐름에 정확히 반영되도록 코드 수정

### Interview Summary
- 기존 동작은 `MainWindow._on_new_version_clicked`에서 다이얼로그로 이름을 받되 `strip() or None` 처리
- `Version` 모델은 `version_name: str | None`; validator가 공백 문자열을 `None`으로 정규화
- `serialize_prompt_snapshot("", "")`을 버전 생성 content로 사용(요청자 확인 필요 시점에서 기존 동작 유지로 확정)

### Research Findings
- 핵심 구현 지점: `src/gui/main_window.py:393`, `src/core/version_manager.py:82`, `src/data/models.py:84`
- 기존 중복/빈값 정책 테스트는 코어에서 일부만 존재하고, GUI 정책 테스트는 부족
- 현재 테스트는 새 버전이 빈 스냅샷으로 저장되는 동작을 이미 가정

### Metis Review
- 핵심 갭: 중복 판정 규칙과 우회 경로(예: GUI 바깥에서의 create_version 호출)에서 정책 미강제
- 위험: 메시지/라벨이 정책과 불일치(예: `optional` 라벨)
- 제안: 정책은 도메인 레이어(`VersionManager`)에 집중 강제, GUI는 사용자 피드백 중심 보강

---

## Work Objectives

### Core Objective
버전 생성 경로에서 사용자 입력 검증을 일관되게 강제하고, 유효한 버전명이 저장·표시·복원에 반영되도록 한다.

### Concrete Deliverables
- `VersionManager.create_version`에 빈 이름 및 prompt 단위 중복 검증 추가
- `MainWindow._on_new_version_clicked` 정책 라벨/오류 피드백 정리
- 새/기존 테스트의 성공적 갱신

### Definition of Done
- 빈 문자열, 공백 문자열, 중복 이름 입력 시 새 버전이 생성되지 않고, 명시적 오류 메시지로 실패
- 유효한 이름은 `Version.version_name`에 그대로 저장
- 목록 라벨은 `version_name` 우선, 값 없을 때만 `v{version_number}` fallback

### Must Have
- 버전명은 task/prompt 단위로 중복 금지
- 버전명 공백/빈 값 입력은 거부
- 중복/빈값 검증은 GUI 실패시만이 아닌 코어 레이어에서도 강제
- 기존 스냅샷 정책은 빈 스냅샷 유지

### Must NOT Have
- `version_number` 정렬/생성 규칙 변경
- DB 스키마 변경이나 대규모 마이그레이션
- 비요구 기능(버전 삭제/복원 정책 변경)

---

## Verification Strategy

> **ZERO HUMAN INTERVENTION** — 검증은 실행 가능한 시나리오와 테스트로만 확인.

### Test Decision
- **Infrastructure exists**: YES (`pytest`)
- **Automated tests**: Tests-after
- **Framework**: `pytest`

### QA Policy
- 각 태스크는 1개 이상의 성공/실패 시나리오를 포함
- 실패 시나리오는 명시적 메시지 또는 상태 변경으로 판정
- 증빙 경로는 `.sisyphus/evidence/task-<N>-<slug>.txt` 또는 `.png`

### Validation Commands
```bash
pytest tests/core/test_version_manager.py -q
QT_QPA_PLATFORM=offscreen pytest tests/gui/test_main_window.py -q
```

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (Foundation):
- T1. 코어 검증 규칙/오류 메시지 기반 추가 (`VersionManager`)

Wave 2 (Core Changes):
- T2. `tests/core/test_version_manager.py` 정책 테스트 추가(빈값/중복)
- T3. `tests/gui/test_main_window.py` 정책 테스트 추가(공백/중복/메시지)

Wave 3 (Integration + Regression):
- T4. `_on_new_version_clicked` 라벨/검증/오류 처리 정리

Wave FINAL (Independent Review):
- F1-F4. 계획 준수/품질/통합/범위 확인

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|------------|--------|------|
| T1 | none | T2, T3, T4 | 1 |
| T2 | T1 | F3 | 2 |
| T3 | T1 | F3 | 2 |
| T4 | T1, T2, T3 | F2, F3, F4 | 3 |

### Agent Dispatch Summary

| Wave | # Tasks | Recommended Agent |
|------|---------|------------------|
| 1 | 1 | `quick` |
| 2 | 2 | `unspecified-high` |
| 3 | 1 | `quick` |
| FINAL | 4 | `oracle`, `unspecified-high` |

## TODOs

- [ ] 1. VersionManager 정책 강화 (빈/중복 검증)

  **What to do**:
  - `src/core/version_manager.py:82`에서 `create_version(...)` 진입점에 빈 문자열/공백 검사 추가
  - prompt 단위 중복 조회 로직 추가 (`get_timeline` 결과 기반)
  - 중복 판단은 입력을 공백 trim 후 비교하고, 대소문자는 구분
  - 위반 시 사용자 정의 예외(`ValueError`) 또는 기존 타입을 통한 예외를 일관되게 던지도록 처리

  **Must NOT do**:
  - 저장소 구조 변경이나 중복 정책을 task 단위로 오버라이드하지 않음

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: `git-master`
    - Why: 변경 범위 추적과 영향도 최소화를 위해 변경 전/후 비교가 중요

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1 (T1)
  - Blocks: T2, T3, T4
  - Blocked By: None

  **References**:
  - `src/core/version_manager.py:82` (create_version 엔트리)
  - `src/data/models.py:84` (`version_name` validator)

  **Acceptance Criteria**:
  - [ ] `create_version(prompt_id, content, "   ")`는 실패(예외)
  - [ ] 같은 prompt 내 동일 이름(공백 trim 후, 대소문자 구분) 2회 생성은 실패(예외)

  **QA Scenarios**:
  - Scenario: 빈 이름 실패
    - Tool: Bash (pytest)
    - Preconditions: 임시 DB 생성, prompt 존재
    - Steps:
      1. `pytest tests/core/test_version_manager.py::TestVersionManagerCreateVersion::test_create_version_rejects_blank_name`
    - Expected Result: 예외 발생으로 테스트 통과, 새 버전 저장 미발생
    - Failure Indicators: 예외 미발생, 생성 성공
    - Evidence: `.sisyphus/evidence/task-1-blank-name.txt`

  - Scenario: 동일 이름 중복 실패
    - Tool: Bash (pytest)
    - Steps: `pytest tests/core/test_version_manager.py::TestVersionManagerCreateVersion::test_create_version_rejects_duplicate_name_within_prompt`
    - Expected Result: 두 번째 생성에서 예외, 버전 개수 1 유지
    - Failure Indicators: 버전 개수가 2 증가
    - Evidence: `.sisyphus/evidence/task-1-duplicate-name.txt`

- [ ] 2. 새 버전 생성 UI 라벨/검증/오류 메시지 정리

  **What to do**:
  - `src/gui/main_window.py:405` 라벨을 `Version name:` 등 필수 입력 문구로 변경
  - `version_name = version_name.strip() or None` 로직을 정책 위반시 즉시 반환으로 변경
  - `ok=False` 또는 빈값/중복 실패일 때 `statusBar` 메시지로 이유 전달
  - `VersionManager.create_version` 예외를 받아 사용자에게 재입력 유도

  **Must NOT do**:
  - 스냅샷 정책(빈 값 직렬화)을 변경하지 않음

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: `playwright`
    - Why: GUI 상태/메시지/선택자 정합성은 직접 실행 시나리오 검증 필요

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2 (T4)
  - Blocks: T4
  - Blocked By: T1

  **References**:
  - `src/gui/main_window.py:393` (신규 버전 생성 핸들러)

  **Acceptance Criteria**:
  - [ ] 빈 입력 시 새 버전 미생성 및 메시지 노출
  - [ ] 중복 입력 시 새 버전 미생성 및 메시지 노출

  **QA Scenarios**:
  - Scenario: 빈 이름 거부
    - Tool: Bash (pytest)
    - Steps:
      1. `monkeypatch`로 `_ask_text_input`을 `("", True)`로 설정
      2. `QT_QPA_PLATFORM=offscreen pytest tests/gui/test_main_window.py::TestMainWindowVersionBehavior::test_new_version_rejects_blank_name_input -q`
    - Expected Result: create_version mock 미호출, 상태바 메시지 경로 포함
    - Failure Indicators: create_version 호출 또는 선택자/메시지 변경
    - Evidence: `.sisyphus/evidence/task-2-blank-input.txt`

  - Scenario: 중복 이름 거부
    - Tool: Bash (pytest)
    - Steps:
      1. 중복 이름이 있는 timeline monkeypatch
      2. `_ask_text_input`을 중복 값으로 고정 후 `_on_new_version_clicked` 호출
      3. `QT_QPA_PLATFORM=offscreen pytest ...::test_new_version_rejects_duplicate_name_input -q` 실행
    - Expected Result: create_version 미호출, 실패 메시지 반환
    - Failure Indicators: 중복 이름으로도 create_version 호출
    - Evidence: `.sisyphus/evidence/task-2-duplicate-input.txt`

- [ ] 3. 코어 레벨 중복/빈 값 테스트 정리

  **What to do**:
  - `tests/core/test_version_manager.py`에 새 테스트를 추가해 핵심 제약을 고정
    - 빈/공백 문자열 입력은 실패
    - 동일 prompt 내 동일 이름은 실패

  **Must NOT do**:
  - 기존 `test_create_first_version`/`test_create_second_version` 기대 동작 변경

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: `playwright`
    - Why: 직접 사용하지 않으며 기본 테스트 실행만으로 충분, 외부 도구 생략

  **Parallelization**:
  - Can Run In Parallel: NO
  - Parallel Group: Wave 2 (T2)
  - Blocks: F3
  - Blocked By: T1

  **References**:
  - `tests/core/test_version_manager.py`
  - `src/core/version_manager.py`

  **Acceptance Criteria**:
  - [ ] 추가한 테스트 2개가 신규 정책을 커버
  - [ ] 새 정책이 기존 테스트 흐름을 회귀 없이 통과

  **QA Scenarios**:
  - Scenario: 중복/빈 값 제약 고정
    - Tool: Bash (pytest)
    - Steps:
      1. `pytest tests/core/test_version_manager.py -q`
    - Expected Result: 테스트가 실패 없이 통과
    - Failure Indicators: 새 추가 테스트 1개 이상 실패
    - Evidence: `.sisyphus/evidence/task-3-core-tests.txt`

- [ ] 4. GUI 레벨 회귀 및 실패 시나리오 정합성 정리

  **What to do**:
  - `tests/gui/test_main_window.py`에 기존/신규 시나리오를 반영해 표시 라벨·메시지·선택 동작 회귀를 점검
  - 기존 스냅샷 동작(`serialize_prompt_snapshot("", "")`)이 테스트로 고정되어 있는지 확인

  **Must NOT do**:
  - 실패 메시지 문자열을 과도하게 하드코딩하지 않음

  **Recommended Agent Profile**:
  - Category: `unspecified-high`
  - Skills: `playwright`
    - Why: UI 상태 전환(버전 선택, 저장바) 근거 확보에 유리

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 3 (T4)
  - Blocks: F2, F3, F4
  - Blocked By: T2, T3

  **References**:
  - `tests/gui/test_main_window.py`
  - `src/gui/main_window.py:138`
  - `src/core/prompt_snapshot.py:19`

  **Acceptance Criteria**:
  - [ ] 기존 신규 버전 동작 테스트 279~350 범위가 정책 변경 후에도 성공
  - [ ] 스냅샷 값 테스트가 정책 의도와 충돌하지 않음

  **QA Scenarios**:
  - Scenario: 기존 회귀 테스트 유지
    - Tool: Bash (pytest)
    - Steps:
      1. `QT_QPA_PLATFORM=offscreen pytest tests/gui/test_main_window.py::TestMainWindowVersionBehavior::test_new_version_created_with_empty_snapshot -q`
      2. `QT_QPA_PLATFORM=offscreen pytest tests/gui/test_main_window.py::TestMainWindowVersionBehavior::test_new_version_persists_custom_name -q`
    - Expected Result: 두 테스트 모두 `1 passed`
    - Failure Indicators: 기존 동작 실패
    - Evidence: `.sisyphus/evidence/task-4-regression.txt`

---

## Final Verification Wave

- [ ] F1. Plan Compliance Audit (`oracle`)
- [ ] F2. Quality Review (`unspecified-high`)
- [ ] F3. Manual/GUI QA (`playwright`)
- [ ] F4. Scope Fidelity Check (`deep`)

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat: validate version name on creation` | `src/core/version_manager.py` | target tests |
| 2 | `feat(ui): enforce version name input feedback` | `src/gui/main_window.py` | target tests |
| 3 | `test: add core version name validation` | `tests/core/test_version_manager.py` | pytest |
| 4 | `test: add gui version name validation` | `tests/gui/test_main_window.py` | pytest |

## Success Criteria

- [ ] 새 버전명 필수 입력 및 중복 금지 정책이 `VersionManager`에서 강제됨
- [ ] 사용자 입력 시 실패 케이스가 메시지로 즉시 표시되고 새 버전이 생성되지 않음
- [ ] 기존 버전 표시 로직(`version_name` 우선, `vN` fallback)은 유지됨
- [ ] `pytest tests/core/test_version_manager.py tests/gui/test_main_window.py -q` 통과

Plan saved to: `.sisyphus/plans/prompt-editor-version-name.md`
