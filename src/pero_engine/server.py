"""PeroEngine FastAPI 서버"""
import asyncio
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import shutil

from .config import get_settings
from .llm import BaseLLM, LLMFactory
from .tts import BaseTTS, TTSFactory
from .asr import WhisperClient

# FastAPI 앱 생성
app = FastAPI(
    title="PeroEngine",
    description="이미지 한 장으로 AI 어시스턴트 만들기",
    version="0.1.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 설정 로드
settings = get_settings()

# 디렉토리 생성
Path(settings.system.characters_dir).mkdir(parents=True, exist_ok=True)
Path(settings.system.models_dir).mkdir(parents=True, exist_ok=True)
Path("temp").mkdir(exist_ok=True)


# 전역 클라이언트
llm_client: BaseLLM = None
tts_client: BaseTTS = None
asr_client: WhisperClient = None


class ChatRequest(BaseModel):
    message: str
    character_id: str = "default"


class TTSRequest(BaseModel):
    text: str
    voice: str = "ko-KR-SunHiNeural"


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global llm_client, tts_client, asr_client

    print("=" * 60)
    print("🚀 PeroEngine 서버 시작 중...")
    print("=" * 60)

    # LLM 클라이언트 초기화
    print(f"\n📚 LLM 클라이언트 초기화 중... (Provider: {settings.llm.provider})")
    try:
        llm_client = LLMFactory.create(
            provider=settings.llm.provider,
            # Ollama
            ollama_base_url=settings.llm.ollama.base_url,
            ollama_model=settings.llm.ollama.model,
            ollama_auto_download=settings.llm.ollama.auto_download,
            # OpenAI
            openai_api_key=settings.llm.openai.api_key,
            openai_model=settings.llm.openai.model,
            # Claude
            claude_api_key=settings.llm.claude.api_key,
            claude_model=settings.llm.claude.model,
        )

        if await llm_client.is_available():
            print(f"✅ {settings.llm.provider.upper()} LLM 연결 성공!")

            # Ollama 전용: 모델 다운로드
            if settings.llm.provider == "ollama" and hasattr(
                llm_client, "ensure_model_exists"
            ):
                await llm_client.ensure_model_exists()
        else:
            print(f"⚠️  {settings.llm.provider.upper()} LLM에 연결할 수 없습니다.")

    except Exception as e:
        print(f"❌ LLM 초기화 실패: {e}")
        llm_client = None

    # TTS 클라이언트 초기화
    print(f"\n🎤 TTS 클라이언트 초기화 중... (Provider: {settings.tts.provider})")
    try:
        tts_client = TTSFactory.create(
            provider=settings.tts.provider,
            # Edge TTS
            edge_voice=settings.tts.edge.voice,
            edge_rate=settings.tts.edge.rate,
            edge_volume=settings.tts.edge.volume,
            # OpenAI TTS
            openai_api_key=settings.tts.openai.api_key,
            openai_model=settings.tts.openai.model,
            openai_voice=settings.tts.openai.voice,
        )
        print(f"✅ {settings.tts.provider.upper()} TTS 준비 완료!")

    except Exception as e:
        print(f"❌ TTS 초기화 실패: {e}")
        tts_client = None

    # ASR 클라이언트 초기화
    print("\n🎧 ASR 클라이언트 초기화 중...")
    asr_client = WhisperClient(
        model=settings.asr.whisper.model,
        language=settings.asr.whisper.language,
        device=settings.asr.whisper.device,
    )
    print("✅ Whisper ASR 준비 완료!")

    print("\n" + "=" * 60)
    print(f"✅ PeroEngine 서버 준비 완료!")
    print(f"🌐 http://{settings.server.host}:{settings.server.port}")
    print("=" * 60 + "\n")


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "PeroEngine API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    ollama_ok = await llm_client.is_available() if llm_client else False

    return {
        "status": "healthy",
        "llm": "online" if ollama_ok else "offline",
        "tts": "online",
        "asr": "online",
    }


@app.post("/character/create")
async def create_character(
    name: str,
    image: UploadFile = File(...),
    persona: str = "",
):
    """캐릭터 생성 (이미지 업로드)"""
    try:
        # 캐릭터 ID 생성
        character_id = str(uuid.uuid4())
        character_dir = Path(settings.system.characters_dir) / character_id
        character_dir.mkdir(parents=True, exist_ok=True)

        # 이미지 저장
        image_path = character_dir / "character.png"
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)

        # 메타데이터 저장
        metadata = {
            "id": character_id,
            "name": name,
            "persona": persona or settings.character.default_persona,
            "image_path": str(image_path),
        }

        import json

        with open(character_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✅ 캐릭터 생성: {name} (ID: {character_id})")

        return {
            "success": True,
            "character_id": character_id,
            "name": name,
            "message": "캐릭터가 생성되었습니다!",
        }

    except Exception as e:
        print(f"❌ 캐릭터 생성 실패: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.post("/chat")
async def chat(request: ChatRequest):
    """채팅 (일반)"""
    try:
        if not llm_client:
            return {"error": "LLM 클라이언트가 초기화되지 않았습니다."}

        response = await llm_client.chat(request.message)

        return {"success": True, "message": response}

    except Exception as e:
        print(f"❌ 채팅 오류: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """채팅 (웹소켓 스트리밍)"""
    await websocket.accept()

    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_json()
            message = data.get("message", "")

            if not message:
                continue

            # 스트리밍 응답
            async for chunk in llm_client.chat_stream(message):
                await websocket.send_json({"type": "chunk", "content": chunk})

            await websocket.send_json({"type": "done"})

    except WebSocketDisconnect:
        print("클라이언트 연결 종료")
    except Exception as e:
        print(f"웹소켓 오류: {e}")


@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """텍스트 → 음성 변환"""
    try:
        # 임시 파일 생성
        audio_id = str(uuid.uuid4())
        audio_path = f"temp/{audio_id}.mp3"

        # TTS 생성
        success = await tts_client.synthesize(request.text, audio_path)

        if success:
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                filename=f"speech_{audio_id}.mp3",
            )
        else:
            return JSONResponse(
                status_code=500, content={"error": "음성 생성 실패"}
            )

    except Exception as e:
        print(f"❌ TTS 오류: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/asr")
async def speech_to_text(audio: UploadFile = File(...)):
    """음성 → 텍스트 변환"""
    try:
        # 임시 파일 저장
        audio_id = str(uuid.uuid4())
        audio_path = f"temp/{audio_id}.wav"

        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)

        # ASR 실행
        text = await asr_client.transcribe(audio_path)

        # 임시 파일 삭제
        Path(audio_path).unlink(missing_ok=True)

        return {"success": True, "text": text}

    except Exception as e:
        print(f"❌ ASR 오류: {e}")
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )


# 정적 파일 서빙 (프론트엔드)
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
except RuntimeError:
    print("⚠️  프론트엔드 디렉토리를 찾을 수 없습니다. API만 실행합니다.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )
