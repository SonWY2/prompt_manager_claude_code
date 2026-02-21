# Prompt Manager

LLM 프롬프트를 관리하고 시험할 수 있는 데스크톱 GUI 애플리케이션입니다. 이 도구는 LLM 프롬프트의 개발, 버전 관리, 테스트를 위한 통합 환경을 제공합니다.

![Prompt Manager 스크린샷](screenshot.png)

## 주요 기능

- **3단 레이아웃**: 태스크 네비게이터, 프롬프트 에디터, 결과 뷰어를 한눈에 확인
- **태스크 관리**: 관련 프롬프트를 그룹화하고 폴더 구조로 정리
- **버전 관리**: 프롬프트의 여러 버전을 생성하고 시각적 타임라인으로 확인
- **템플릿 변수**: `{{변수명}}` 형식의 템플릿 변수로 동적 프롬프트 작성
- **LLM 통합**: 프롬프트를 OpenAI Compatible API로 전송하고 결과를 즉시 확인
- **결과 비교**: 여러 버전의 프롬프트 결과를 나란히 비교
- **성능 메트릭**: 응답 시간, 토큰 사용량 등 통계 확인

## 기술 스택

### GUI 프레임워크
- **PySide6**: Qt for Python GUI 프레임워크
- **Qt Widgets**: 네이티브 데스크톱 UI 컴포넌트

### 백엔드 로직
- **Python 3.12+**: 코어 비즈니스 로직
- **TinyDB**: JSON 파일 기반 데이터베이스
- **requests**: OpenAI Compatible API 호출

## 프로젝트 구조

```
prompt_manager/
├── data/                      # 데이터 스토리지
│   └── prompts.json           # 프롬프트 데이터 JSON 파일
├── src/
│   ├── core/                  # 비즈니스 로직
│   │   ├── task_manager.py    # 태스크 관리
│   │   ├── version_manager.py # 버전 관리
│   │   ├── template_engine.py # 템플릿 변수 렌더링
│   │   └── llm_service.py     # LLM API 서비스
│   ├── data/                  # 데이터 계층
│   │   ├── models.py          # 데이터 모델 정의
│   │   ├── database.py        # TinyDB 초기화
│   │   └── repository.py      # 데이터베이스 CRUD
│   ├── gui/                   # GUI 계층
│   │   ├── main.py            # 애플리케이션 진입점
│   │   ├── main_window.py     # 메인 윈도우
│   │   └── widgets/           # 커스텀 위젯
│   │       ├── task_navigator.py
│   │       ├── prompt_editor.py
│   │       └── result_viewer.py
│   └── utils/                 # 유틸리티 함수
│       ├── string_utils.py
│       └── id_generator.py
├── requirements.txt           # Python 의존성
└── run.py                     # 실행 스크립트
```

## 설치 및 실행

### 전제 조건
- Python 3.12+
- pip

### 설치 단계

1. 레포지토리 클론
   ```bash
   git clone <repository-url>
   cd prompt-manager
   ```

2. 가상환경 생성 및 활성화
   ```bash
   # 가상환경 생성
   python3.12 -m venv venv

   # 가상환경 활성화 (Linux/Mac)
   source venv/bin/activate

   # 가상환경 활성화 (Windows PowerShell)
   .\venv\Scripts\Activate.ps1
   ```

3. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

4. 애플리케이션 실행
   ```bash
   python run.py
   ```

## 사용 가이드

### 태스크 관리
1. 왼쪽 패널에서 "태스크 추가" 버튼을 클릭하여 새 태스크 생성
2. 태스크를 선택하여 관련 프롬프트와 버전 확인
3. 태스크 목록에서 최근 작업한 태스크 확인

### 프롬프트 작성 및 버전 관리
1. 중앙 패널의 에디터에서 프롬프트 작성
2. `{{변수명}}` 형식으로 템플릿 변수 사용
3. "새 버전 생성" 버튼을 클릭하여 현재 프롬프트의 새 버전 생성
4. 버전 타임라인에서 이전 버전으로 돌아가기

### 변수 관리 및 실행
1. 프롬프트 에디터 하단의 변수 관리 섹션에서 변수값 입력
2. "미리보기" 버튼을 클릭하여 렌더링된 프롬프트 확인
3. "실행" 버튼을 클릭하여 LLM API 호출

### 결과 확인 및 비교
1. 오른쪽 패널에서 LLM 응답 확인
2. "이력" 탭에서 이전 실행 결과 확인
3. "비교" 탭에서 두 버전의 프롬프트와 결과 비교
4. "메트릭" 탭에서 성능 통계 확인

## LLM 설정

### OpenAI Compatible API

애플리케이션은 OpenAI Compatible API 서버를 지원합니다. 설정 파일 또는 GUI에서 다음을 구성하세요:

- API 엔드포인트 URL (예: `http://localhost:11434/v1`)
- API 키 (필요한 경우)
- 모델 이름 (예: `llama2`, `gpt-3.5-turbo`)

### 지원되는 서버

- OpenAI API
- Ollama (로컬 LLM)
- vLLM
- 기타 OpenAI Compatible 서버

## 코어 API

내부 API는 함수 호출로 직접 접근 가능합니다:

### 태스크 관리
```python
from src.core.task_manager import TaskManager

manager = TaskManager()
task = manager.create_task("새 태스크", "설명")
tasks = manager.get_all_tasks()
```

### 버전 관리
```python
from src.core.version_manager import VersionManager

version_manager = VersionManager()
version = version_manager.create_version(task_id, "프롬프트 내용")
```

### LLM 실행
```python
from src.core.llm_service import LLMService

llm_service = LLMService(api_url="http://localhost:11434/v1")
response = llm_service.call_llm(prompt, model="llama2")
```

## 향후 개선 사항

- **LLM 프로바이더 다양화**: Anthropic, Google 등 다양한 LLM API 플러그인 지원
- **프롬프트 성능 분석**: A/B 테스트 및 상세 분석 기능
- **데이터베이스 마이그레이션**: SQLite로 전환 옵션
- **데이터 백업/복원**: JSON 내보내기/가져오기 기능
- **프롬프트 템플릿 라이브러리**: 자주 사용하는 패턴 저장 및 불러오기

## 라이센스

[MIT 라이센스](LICENSE)
