# Prompt Manager Notepad - Issues

## [2026-02-15] Task 6: 코어 로직 - LLM Service 및 Provider Manager
- **CRITICAL**: 파일 길이 500줄 초과 (llm_service.py: 252줄, provider_manager.py: 188줄, task_manager.py: 174줄, version_manager.py: 180줄)
- 해결 필요: 파일 모듈화 (단일 책임 원칙 준수)
- 현재 상태: 테스트는 통과했으나, 가드레일 위배됨
