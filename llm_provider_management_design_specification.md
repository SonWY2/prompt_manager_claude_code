⚙️ LLM Provider Management: Design Specification
1. 디자인 컨셉
목적: 복잡한 API 설정 과정을 단순화하고, 현재 사용 가능한 모델의 상태를 시각적으로 즉시 확인.
스타일: Postman이나 Insomnia와 같은 개발 도구 스타일의 Split-View 레이아웃.
사용자 경험: "등록 -> 설정 -> 테스트 -> 저장"으로 이어지는 선형적인 워크플로우 제공.
2. 레이아웃 구조 (Split-View)
[좌측: Provider List Panel] (Width: 300px)
등록된 모든 LLM 연결 설정을 관리하는 목록 영역입니다.

Header: 'Providers' 타이틀과 함께 신규 추가를 위한 + Add 버튼 배치.
List Item (QListWidget 커스텀):
아이콘: 서비스 로고(OpenAI, Anthropic 등) 또는 로컬 서버 아이콘.
텍스트: 설정 별칭 (예: "Production GPT-4", "Local Llama3").
상태 표시등: 우측 끝에 작은 원형 도트 표시 (#4CAF50 초록: 연결됨, #F44336 빨강: 연결 오류, #9E9E9E 회색: 테스트 전).
삭제 버튼: 호버(Hover) 시 나타나는 휴지통 아이콘.
[우측: Configuration Detail Panel] (Main Content)
선택된 Provider의 세부 정보를 수정하는 영역으로, 세 가지 섹션으로 구분됩니다.

섹션 1: General Info (기본 정보)
Provider Name: 사용자가 식별하기 위한 고유 이름 입력 필드.
Description: 해당 연결에 대한 짧은 메모 (예: "사내 테스트용 Ollama 서버").
섹션 2: Connection Settings (연결 설정)
API Base URL: https://api.openai.com/v1 또는 http://localhost:11434와 같은 엔드포인트 주소.
API Key: 비밀번호 마스킹 처리(●●●●●●)가 된 입력 필드와 우측의 '눈 모양' 아이콘(Toggle Visibility).
Organization ID: (선택 사항) 특정 LLM 제공자에 필요한 ID 입력 필드.
Test Connection 버튼: 입력된 정보로 실제 API를 호출하여 유효성을 검사하는 버튼. 성공 시 "Success: Connection established" 메시지 출력.
섹션 3: Default Model Parameters (기본 파라미터)
이 제공자를 사용할 때 기본적으로 적용될 값들을 미리 설정합니다.

Default Model: 해당 서버에서 제공하는 모델 목록 드롭다운 (QComboBox).
Temperature Slider: 0.0 ~ 2.0 사이의 값을 조절하는 슬라이더와 수치 입력 칸.
Max Tokens: 생성할 최대 토큰 수 제한 (QSpinBox).
Stop Sequences: 특정 문자열에서 멈추도록 설정하는 태그형 입력창.
3. 인터렉션 디테일 (UX)
실시간 유효성 검사: URL 형식이나 API 키 입력 여부에 따라 'Save' 버튼의 활성화 상태가 동적으로 변함.
연결 테스트 애니메이션: 'Test Connection' 클릭 시 버튼 내부에 작은 스피너(Spinner)가 돌아가며 비동기 통신 중임을 표시.
저장 알림: 우측 하단에 잠깐 나타났다 사라지는 토스트 메시지(Toast Message)로 저장 완료 알림.
4. PySide6 구현 가이드라인
비동기 통신: API 테스트 시 GUI가 프리징되지 않도록 QNetworkAccessManager 또는 QThread를 사용하여 비동기로 처리하세요.
보안: API Key는 메모리 상에서 안전하게 관리하고, 저장 시에는 운영체제의 안전한 저장소(Keyring 등)를 활용하는 것을 권장합니다.
컴포넌트:
좌측 리스트는 QScrollArea 내의 QVBoxLayout에 커스텀 위젯을 동적으로 추가하는 방식으로 구현하면 유연합니다.
우측 설정창은 QFormLayout을 사용하여 라벨과 입력 필드를 깔끔하게 정렬하세요.
이 명세서는 사용자가 "내 프롬프트가 어떤 환경에서 돌아가는가"를 가장 직관적으로 관리할 수 있도록 돕는 데 초점을 맞추고 있습니다. 이 디자인을 실제 PySide6 코드로 옮기기 위한 추가 정보가 필요하신가요?
