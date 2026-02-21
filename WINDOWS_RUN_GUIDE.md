# Windows 실행 가이드

## 배치 파일 개요

프로젝트에는 3개의 배치 파일이 포함되어 있습니다:

| 파일 | 용도 |
|------|------|
| `run.bat` | 애플리케이션 실행 (가상환경 및 의존성이 이미 설치된 경우) |
| `setup_and_run.bat` | 초기 설정 및 실행 (처음 실행 시 사용) |
| `activate_venv.bat` | 가상환경 활성화 (수동으로 명령어를 실행할 때 사용) |

---

## 사용 방법

### 1. 처음 실행 (초기 설정)

아직 가상환경이나 의존성이 설치되지 않은 경우:

```cmd
setup_and_run.bat
```

이 배치 파일은 다음 작업을 수행합니다:
1. 가상환경 생성 (없는 경우)
2. Python 패키지 설치 (requirements.txt)
3. 애플리케이션 실행

**전제 조건:**
- Python 3.12+이 설치되어 있어야 함
- [Python 다운로드](https://www.python.org/downloads/)

---

### 2. 일반 실행 (애플리케이션 시작)

가상환경과 의존성이 이미 설치된 경우:

```cmd
run.bat
```

**사용 시기:**
- 애플리케이션을 일상적으로 실행할 때
- 이미 한 번 setup_and_run.bat을 실행한 적이 있는 경우

---

### 3. 가상환경 활성화 (수동 명령어 실행)

개발 목적으로 가상환경에서 직접 Python 명령어를 실행하고 싶을 때:

```cmd
activate_venv.bat
```

활성화 후 다음 명령어들을 실행할 수 있습니다:
- `python run.py` - 애플리케이션 실행
- `pytest tests/` - 테스트 실행
- `ruff check src/` - 코드 린팅
- `mypy src/` - 타입 검사

종료하려면 `exit`를 입력하세요.

---

## 문제 해결

### 문제: "Python이 설치되어 있지 않습니다" 오류

**해결 방법:**
1. [Python 공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.12+ 다운로드
2. 설치 시 "Add Python to PATH" 옵션 체크
3. 설치 후 터미널을 닫고 다시 실행

### 문제: 가상환경 활성화 오류

**해결 방법:**
1. `setup_and_run.bat`을 실행하여 가상환경을 새로 생성
2. `venv` 폴더를 수동으로 삭제 후 `setup_and_run.bat` 재실행

### 문제: 의존성 설치 오류

**해결 방법:**
```cmd
setup_and_run.bat
```

또는 수동으로 실행:
```cmd
activate_venv.bat
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 추가 팁

### 테스트 실행

가상환경을 활성화한 후 테스트를 실행하세요:

```cmd
activate_venv.bat
pytest tests/
```

### 코드 검사

```cmd
activate_venv.bat
ruff check src/
mypy src/
```

### 의존성 업데이트

```cmd
activate_venv.bat
pip install --upgrade -r requirements.txt
```

---

## 참고

- 배치 파일을 더블 클릭하여 실행할 수 있습니다
- 오류 발생 시 터미널 창이 닫히지 않도록 `pause` 명령어가 포함되어 있습니다
- **참고**: Windows cmd.exe의 UTF-8 인코딩 문제로 인해 배치 파일 내의 메시지는 영어로 표시됩니다 (가이드는 한국어로 제공됨)
