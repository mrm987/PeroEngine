# API Provider 설정 가이드

PeroEngine은 로컬 및 클라우드 API를 선택적으로 사용할 수 있습니다.

## 🎯 기본 전략

- **기본값**: 완전 로컬 (Ollama + Edge TTS)
- **선택적 API**: OpenAI, Claude (config.yaml에서 설정)
- **비용**: API 키를 설정하지 않으면 완전 무료

---

## 📚 LLM (언어 모델)

### 1. Ollama (로컬 - 기본값)

**장점**: ✅ 무료, ✅ 오프라인, ✅ 프라이버시
**단점**: ❌ 성능은 API보다 낮음

```yaml
# config.yaml
llm:
  provider: "ollama"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2:3b"
    auto_download: true
```

**설치**:
```bash
# https://ollama.ai 에서 다운로드
ollama serve
```

**사용 가능 모델**:
- `llama3.2:1b` - 초경량 (8GB RAM)
- `llama3.2:3b` - 경량 (12GB RAM) ⭐ 기본값
- `qwen2.5:7b` - 고성능 (16GB RAM)

---

### 2. OpenAI (클라우드 API)

**장점**: ✅ 최고 품질, ✅ 빠른 응답
**단점**: ❌ 비용 발생, ❌ 인터넷 필요

```yaml
# config.yaml
llm:
  provider: "openai"
  openai:
    api_key: "sk-..."  # 여기에 API 키 입력
    model: "gpt-3.5-turbo"
```

**API 키 발급**:
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키를 config.yaml에 붙여넣기

**비용** (2025년 기준):
- GPT-3.5-turbo: $0.0005/1K tokens (입력), $0.0015/1K tokens (출력)
- GPT-4: $0.03/1K tokens (입력), $0.06/1K tokens (출력)

**예상 월 비용** (하루 100턴 대화):
- GPT-3.5: ~$3-5/월
- GPT-4: ~$30-50/월

---

### 3. Claude (클라우드 API)

**장점**: ✅ 고품질, ✅ 긴 문맥, ✅ 한국어 우수
**단점**: ❌ 비용 발생, ❌ 인터넷 필요

```yaml
# config.yaml
llm:
  provider: "claude"
  claude:
    api_key: "sk-ant-..."  # 여기에 API 키 입력
    model: "claude-3-haiku-20240307"
```

**API 키 발급**:
1. https://console.anthropic.com/settings/keys 접속
2. "Create Key" 클릭
3. 생성된 키를 config.yaml에 붙여넣기

**비용** (2025년 기준):
- Claude 3 Haiku: $0.00025/1K tokens (입력), $0.00125/1K tokens (출력)
- Claude 3 Sonnet: $0.003/1K tokens (입력), $0.015/1K tokens (출력)

**예상 월 비용** (하루 100턴 대화):
- Haiku: ~$2-3/월 ⭐ 가장 저렴
- Sonnet: ~$20-30/월

---

## 🎤 TTS (음성 합성)

### 1. Edge TTS (무료 API - 기본값)

**장점**: ✅ 무료, ✅ 고품질, ✅ 한국어 완벽
**단점**: ❌ 인터넷 필요

```yaml
# config.yaml
tts:
  provider: "edge"
  edge:
    voice: "ko-KR-SunHiNeural"  # 여성
    # voice: "ko-KR-InJoonNeural"  # 남성
    rate: "+0%"
    volume: "+0%"
```

**사용 가능 한국어 음성**:
- `ko-KR-SunHiNeural` - 여성 (기본값)
- `ko-KR-InJoonNeural` - 남성
- `ko-KR-BongJinNeural` - 남성 (젊은 톤)
- `ko-KR-GookMinNeural` - 남성 (차분한 톤)

---

### 2. OpenAI TTS (클라우드 API)

**장점**: ✅ 매우 자연스러움, ✅ 감정 표현
**단점**: ❌ 비용 발생, ❌ 한국어 없음 (영어만)

```yaml
# config.yaml
tts:
  provider: "openai"
  openai:
    api_key: "sk-..."  # LLM과 같은 키 사용 가능
    model: "tts-1"  # or "tts-1-hd" (고품질)
    voice: "alloy"  # alloy, echo, fable, onyx, nova, shimmer
```

**비용** (2025년 기준):
- tts-1: $0.015 / 1K characters
- tts-1-hd: $0.030 / 1K characters

**예상 월 비용** (하루 50개 문장):
- tts-1: ~$3-5/월
- tts-1-hd: ~$6-10/월

---

## 💰 비용 비교표

| 구성 | LLM | TTS | 월 비용 | 품질 |
|------|-----|-----|---------|------|
| **풀 로컬** | Ollama | Edge TTS (무료) | **$0** | ★★★★☆ |
| **하이브리드 1** | OpenAI GPT-3.5 | Edge TTS | **$3-5** | ★★★★★ |
| **하이브리드 2** | Claude Haiku | Edge TTS | **$2-3** | ★★★★★ |
| **풀 API** | OpenAI GPT-3.5 | OpenAI TTS | **$8-10** | ★★★★★ |
| **프리미엄** | Claude Sonnet | OpenAI TTS HD | **$26-40** | ★★★★★ |

---

## 🔧 설정 예시

### 예시 1: 완전 무료 (오프라인)
```yaml
llm:
  provider: "ollama"
  ollama:
    model: "llama3.2:3b"

tts:
  provider: "edge"
  edge:
    voice: "ko-KR-SunHiNeural"
```

---

### 예시 2: 최고 품질 (저비용)
```yaml
llm:
  provider: "claude"
  claude:
    api_key: "sk-ant-..."
    model: "claude-3-haiku-20240307"

tts:
  provider: "edge"  # 무료
  edge:
    voice: "ko-KR-SunHiNeural"
```

**월 비용**: ~$2-3

---

### 예시 3: 프리미엄 경험
```yaml
llm:
  provider: "openai"
  openai:
    api_key: "sk-..."
    model: "gpt-4"

tts:
  provider: "openai"
  openai:
    api_key: "sk-..."  # 같은 키
    model: "tts-1-hd"
    voice: "nova"
```

**월 비용**: ~$36-60

---

## 🔐 환경변수로 API 키 설정 (권장)

보안을 위해 config.yaml에 직접 키를 넣지 말고 환경변수 사용:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Windows (PowerShell)
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

그리고 config.yaml에서:
```yaml
llm:
  openai:
    api_key: "${OPENAI_API_KEY}"
```

---

## 📊 추천 구성

### 일반 사용자 (학생/취미)
```yaml
LLM: Ollama (무료)
TTS: Edge TTS (무료)
월 비용: $0
```

### 비즈니스/프로페셔널
```yaml
LLM: Claude Haiku (고품질, 저비용)
TTS: Edge TTS (무료)
월 비용: $2-3
```

### 최고 품질 원하는 사용자
```yaml
LLM: Claude Sonnet 또는 GPT-4
TTS: OpenAI TTS HD
월 비용: $30-50
```

---

## 🆘 문제 해결

### OpenAI API 오류
```
❌ OpenAI API 키가 유효하지 않습니다
```

**해결책**:
1. API 키 확인: https://platform.openai.com/api-keys
2. 결제 정보 등록 확인
3. 사용량 한도 확인

### Claude API 오류
```
❌ Claude API에 연결할 수 없습니다
```

**해결책**:
1. API 키 확인: https://console.anthropic.com/settings/keys
2. 크레딧 잔액 확인
3. Rate limit 확인 (분당 요청 수)

---

## 💡 팁

1. **테스트 시**: 무료 Ollama로 시작
2. **품질 중요**: Claude Haiku (가성비 최고)
3. **한국어 TTS**: Edge TTS 추천 (무료 + 고품질)
4. **영어 TTS**: OpenAI TTS (감정 표현 우수)
5. **비용 절약**: LLM만 API, TTS는 무료 Edge 사용
