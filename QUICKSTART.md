# PeroEngine 빠른 시작 가이드

## 📦 설치

### 1. 필수 요구사항

- **Python**: 3.10 이상 3.13 미만
- **Ollama**: https://ollama.ai 에서 다운로드
- **시스템 요구사항**:
  - 최소: RAM 12GB, CPU 4코어, 디스크 20GB
  - 권장: RAM 16-32GB, CPU 8코어, GPU (RTX 3060 이상)

### 2. Ollama 설치 및 실행

```bash
# https://ollama.ai 에서 OS에 맞는 버전 다운로드 후 설치

# Ollama 서버 실행 (백그라운드)
ollama serve
```

### 3. PeroEngine 설치

```bash
# 리포지토리 클론
git clone https://github.com/yourusername/PeroEngine.git
cd PeroEngine

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 🚀 서버 실행

```bash
# 서버 실행
python run_server.py
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:

```
========================================================
🎭 PeroEngine - AI 어시스턴트 플랫폼
========================================================

📡 서버 주소: http://localhost:8000
📁 캐릭터 저장 경로: ./characters
🤖 LLM 모델: llama3.2:3b
🎤 TTS: edge
🎧 ASR: whisper

========================================================
✅ 서버 시작 준비 완료!
⚠️  종료하려면 Ctrl+C를 누르세요
========================================================
```

첫 실행 시 Ollama가 자동으로 모델을 다운로드합니다 (약 2GB, 수 분 소요).

## 🎨 첫 AI 어시스턴트 만들기

1. 브라우저에서 `http://localhost:8000/static/index.html` 접속

2. **캐릭터 만들기** 탭에서:
   - 캐릭터 이름 입력 (예: "페로")
   - 캐릭터 이미지 업로드 (PNG/JPG)
   - 성격 설정 (선택사항)
   - "✨ AI 어시스턴트 만들기" 클릭

3. **대화하기** 탭으로 이동하여 AI와 대화!

## 📝 설정 변경

`config.yaml` 파일을 수정하여 설정을 변경할 수 있습니다:

```yaml
# LLM 모델 변경 (더 작은 모델 = 더 빠름, 더 큰 모델 = 더 좋은 품질)
llm:
  ollama:
    model: "llama3.2:1b"  # 1B: 초경량 (6GB RAM)
    # model: "llama3.2:3b"  # 3B: 경량 (12GB RAM) - 기본값
    # model: "qwen2.5:7b"   # 7B: 고성능 (16GB RAM)

# TTS 음성 변경
tts:
  edge:
    voice: "ko-KR-InJoonNeural"  # 남성 목소리
    # voice: "ko-KR-SunHiNeural"  # 여성 목소리 (기본값)
```

## 🧪 API 테스트

### 헬스 체크

```bash
curl http://localhost:8000/health
```

### 채팅 테스트

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕!"}'
```

### TTS 테스트

```bash
curl -X POST http://localhost:8000/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요!"}' \
  --output test.mp3
```

## 🐛 문제 해결

### Ollama 연결 실패

```
❌ Ollama 서버에 연결할 수 없습니다.
```

**해결책**:
1. Ollama가 설치되었는지 확인: `ollama --version`
2. Ollama 서버 실행: `ollama serve`
3. 다른 터미널에서 PeroEngine 실행

### 모델 다운로드 실패

```
❌ 모델 다운로드 실패
```

**해결책**:
1. 인터넷 연결 확인
2. 수동 다운로드: `ollama pull llama3.2:3b`
3. 다시 서버 실행

### 메모리 부족

```
RuntimeError: CUDA out of memory
```

**해결책**:
1. 더 작은 모델 사용: `config.yaml`에서 `model: "llama3.2:1b"` 설정
2. CPU 모드 사용: `device: "cpu"` 설정

## 📚 다음 단계

- [API 문서](docs/api.md) - REST API 상세 가이드
- [설정 가이드](docs/configuration.md) - 고급 설정 옵션
- [마켓플레이스](docs/marketplace.md) - 캐릭터 공유 및 거래

## 💬 지원

문제가 있으신가요? GitHub Issues에 문의해주세요:
https://github.com/yourusername/PeroEngine/issues
