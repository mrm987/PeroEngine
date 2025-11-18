# PeroEngine Desktop App

Electron 기반 데스크톱 애플리케이션

## 특징

- 🖥️ **크로스 플랫폼**: Windows, macOS, Linux 지원
- 🔔 **시스템 트레이**: 백그라운드 실행 및 빠른 접근
- ⌨️ **전역 단축키**: Ctrl+Shift+P로 언제든 호출
- 🐍 **Python 통합**: FastAPI 백엔드 자동 시작/종료
- 🎨 **네이티브 느낌**: 독립 실행형 데스크톱 앱

## 개발 모드 실행

### 1. 의존성 설치

```bash
npm install
```

### 2. Python 환경 설정

```bash
cd ..
pip install -r requirements.txt
```

### 3. 개발 모드 시작

```bash
npm run dev
```

이 명령어는 Python 서버와 Electron 앱을 동시에 시작합니다.

#### 빠른 시작 (Python 서버 수동 실행)

```bash
# 터미널 1: Python 서버
cd ..
python run_server.py

# 터미널 2: Electron 앱
npm run dev:quick
```

## 빌드

### Windows 빌드

```bash
npm run build:win
```

생성물: `dist/PeroEngine-Setup-0.1.0.exe`

### macOS 빌드

```bash
npm run build:mac
```

생성물: `dist/PeroEngine-0.1.0.dmg`

### Linux 빌드

```bash
npm run build:linux
```

생성물: `dist/PeroEngine-0.1.0.AppImage`

## 사용법

### 전역 단축키

- **Ctrl+Shift+P** (또는 Cmd+Shift+P on Mac): 창 표시/숨기기

### 시스템 트레이

앱을 닫아도 시스템 트레이에서 계속 실행됩니다:

- **트레이 아이콘 더블클릭**: 창 표시
- **우클릭 메뉴**:
  - 열기: 창 표시 및 포커스
  - 설정: 설정 페이지 열기
  - 종료: 앱 완전 종료

### 창 관리

- 창을 닫으면 백그라운드로 이동 (완전 종료 아님)
- 완전 종료하려면 트레이 메뉴에서 "종료" 선택

## 프로젝트 구조

```
electron/
├── main.js              # 메인 프로세스 (Node.js)
├── preload.js           # Preload 스크립트 (보안 레이어)
├── dev.js               # 개발 모드 실행 스크립트
├── build.js             # 빌드 스크립트
├── assets/              # 리소스 파일
│   ├── icon.png         # 앱 아이콘 (512x512)
│   └── tray-icon.png    # 트레이 아이콘 (22x22)
└── README.md            # 이 파일
```

## 아이콘 교체

`assets/` 디렉토리의 아이콘을 교체하여 커스터마이징할 수 있습니다:

- **icon.png**: 512x512 PNG (투명 배경 권장)
- **tray-icon.png**: 22x22 PNG (트레이용 작은 아이콘)

자세한 내용은 `assets/README.md` 참조.

## 프로덕션 배포

### 1. 빌드 전 체크리스트

- [ ] 커스텀 아이콘 준비
- [ ] `package.json`의 버전 업데이트
- [ ] Python 의존성 확인 (`requirements.txt`)
- [ ] 설정 파일 확인 (`config.yaml`)

### 2. 빌드 실행

```bash
npm run build:win    # Windows 사용자용
npm run build:mac    # macOS 사용자용
npm run build:linux  # Linux 사용자용
```

### 3. 설치 파일 테스트

`dist/` 디렉토리의 설치 파일을 실제 환경에서 테스트합니다.

### 4. 배포

- Windows: `.exe` 파일 배포
- macOS: `.dmg` 파일 배포 (코드 서명 권장)
- Linux: `.AppImage` 또는 `.deb` 파일 배포

## 개발 팁

### 디버깅

개발 모드에서는 자동으로 개발자 도구가 열립니다 (electron/main.js:94).

### 핫 리로드

코드 변경 시:
- Electron 코드 (main.js, preload.js): 앱 재시작 필요
- Python 코드: `config.yaml`의 `server.reload: true` 설정으로 자동 리로드

### 로그 확인

```bash
npm run dev  # 모든 로그 표시
```

## 문제 해결

### Python 서버가 시작되지 않음

1. Python 설치 확인: `python --version`
2. 의존성 설치 확인: `pip install -r requirements.txt`
3. 포트 8000이 사용 중인지 확인

### Electron 앱이 빈 화면만 표시

1. Python 서버가 실제로 실행 중인지 확인
2. http://localhost:8000/static/index.html 접근 가능한지 확인
3. 3초 대기 시간을 늘려보기 (main.js:91)

### 빌드가 실패함

1. `node_modules` 삭제 후 재설치: `npm install`
2. 디스크 공간 확인
3. 빌드 로그에서 에러 메시지 확인

## 라이선스

MIT License
