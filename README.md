# PeroEngine 🎭

**"이미지 한 장이면 나만의 AI 어시스턴트가 생깁니다"**

PeroEngine은 2D 이미지 한 장으로 음성 대화형 AI 어시스턴트를 만들 수 있는 오픈소스 프로젝트입니다.

## ✨ 핵심 특징

- 🖼️ **이미지 1장 → AI 어시스턴트**: Live2D 제작 없이 이미지만으로 캐릭터 생성
- 🎮 **백그라운드 동반자**: 게임하면서도 FPS 영향 <2%
- 🔒 **완전 오프라인**: 모든 기능 로컬 실행 가능
- ⚡ **동적 모드 전환**: 시스템 부하에 따라 자동으로 경량/고성능 모드 전환
- 🛒 **마켓플레이스 준비**: 통일된 규격으로 캐릭터/음성/페르소나 거래

## 🎯 차별점

| 특징 | Open-LLM-VTuber | PeroEngine |
|------|-----------------|------------|
| 캐릭터 생성 | Live2D 수동 제작 | **이미지 1장 자동** |
| 진입 장벽 | 높음 | **매우 낮음** |
| 게임 중 사용 | 어려움 | **최적화됨** |
| 기본 TTS | Edge TTS (API) | **MeloTTS (로컬)** |

## 🚀 빠른 시작

### 필수 요구사항

```yaml
최소 사양:
  RAM: 12GB
  CPU: 4코어 이상
  디스크: 20GB 여유 공간

권장 사양:
  RAM: 16-32GB
  CPU: 8코어 이상
  GPU: RTX 3060 (8GB VRAM) 이상
  디스크: 50GB SSD
```

### 옵션 1: 데스크톱 앱 (권장)

```bash
# 1. 리포지토리 클론
git clone https://github.com/yourusername/PeroEngine.git
cd PeroEngine

# 2. Python 의존성 설치
pip install -r requirements.txt

# 3. Node.js 의존성 설치
npm install

# 4. Ollama 설치 (LLM용)
# https://ollama.ai 에서 다운로드

# 5. 개발 모드 실행
npm run dev
```

**특징:**
- 🖥️ 독립 실행형 데스크톱 앱
- 🔔 시스템 트레이에서 백그라운드 실행
- ⌨️ 전역 단축키 (Ctrl+Shift+P)로 빠른 호출
- 📦 설치 파일 빌드 가능 (.exe, .dmg, .AppImage)

자세한 내용: [electron/README.md](electron/README.md)

### 옵션 2: 웹 버전

```bash
# 1. 리포지토리 클론
git clone https://github.com/yourusername/PeroEngine.git
cd PeroEngine

# 2. Python 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. Ollama 설치 (LLM용)
# https://ollama.ai 에서 다운로드

# 5. 서버 실행
python run_server.py
```

브라우저에서 `http://localhost:8000` 접속

### 첫 AI 어시스턴트 만들기

1. 앱 실행 또는 웹 접속
2. 캐릭터 이미지 업로드 (PNG/JPG)
3. 이름과 성격 설정
4. 생성 버튼 클릭!

## 📁 프로젝트 구조

```
PeroEngine/
├── src/pero_engine/          # 핵심 소스 코드
│   ├── llm/                  # LLM 통합 (Ollama, OpenAI, Claude)
│   ├── tts/                  # 음성 합성 (Edge TTS, OpenAI TTS)
│   ├── asr/                  # 음성 인식 (Whisper)
│   ├── animation/            # 이미지 → 애니메이션
│   ├── config/               # 설정 관리
│   └── server.py             # FastAPI 서버
├── electron/                 # 데스크톱 앱 (Electron)
│   ├── main.js               # 메인 프로세스
│   ├── preload.js            # Preload 스크립트
│   ├── dev.js                # 개발 모드 실행
│   ├── build.js              # 빌드 스크립트
│   └── assets/               # 아이콘 등 리소스
├── static/                   # 웹 UI
├── characters/               # 캐릭터 저장소
├── models/                   # 로컬 모델 저장
├── config.yaml               # 메인 설정 파일
├── package.json              # Node.js 설정
└── run_server.py             # Python 서버 실행
```

## 🛠️ 기술 스택

- **Backend**: FastAPI, Python 3.10+
- **Desktop**: Electron, Node.js
- **LLM**: Ollama (로컬), OpenAI/Claude (선택)
- **TTS**: Edge TTS (기본), OpenAI TTS (선택)
- **ASR**: Whisper
- **Animation**: 2D 스프라이트 (Live2D 지원 예정)

## 📖 문서

- [데스크톱 앱 가이드](electron/README.md)
- [API Provider 설정](docs/API_PROVIDERS.md)
- [아이콘 가이드](electron/assets/README.md)

## 🤝 기여

PeroEngine은 오픈소스 프로젝트입니다! 기여를 환영합니다.

## 📄 라이선스

MIT License

## 🙏 크레딧

- Inspired by [Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)
- Built with [Ollama](https://ollama.ai)
