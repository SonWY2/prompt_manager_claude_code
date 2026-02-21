# Prompt Manager Notepad - Decisions

## [2026-02-15] Task 0: 테스트 인프라 설정
- pytest를 테스트 프레임워크로 선택
- pytest-qt를 GUI 테스트에 사용

## [2026-02-22] Task 10: 기능 연동 및 완성(Task 10)
- 기존 `MainWindow` 내부 신호/슬롯 연결이 요구 플로우를 충족하므로, 검증 중심으로 진행하고 회귀 수정 없이 완료를 판단.
- 범위를 Task 10로 한정하고 최소 변경 원칙(기존 동작 보존, provider/core 로직 비수정)을 유지.
