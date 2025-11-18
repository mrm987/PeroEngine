#!/usr/bin/env python3
"""PeroEngine 서버 실행 스크립트"""
import sys
import uvicorn
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pero_engine.config import get_settings


def main():
    """서버 실행"""
    settings = get_settings()

    print("\n" + "=" * 60)
    print("🎭 PeroEngine - AI 어시스턴트 플랫폼")
    print("=" * 60)
    print(f"\n📡 서버 주소: http://{settings.server.host}:{settings.server.port}")
    print(f"📁 캐릭터 저장 경로: {settings.system.characters_dir}")
    print(f"🤖 LLM 모델: {settings.llm.ollama.model}")
    print(f"🎤 TTS: {settings.tts.provider}")
    print(f"🎧 ASR: {settings.asr.provider}")
    print("\n" + "=" * 60)
    print("✅ 서버 시작 준비 완료!")
    print("⚠️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 60 + "\n")

    # Uvicorn으로 FastAPI 서버 실행
    uvicorn.run(
        "pero_engine.server:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )


if __name__ == "__main__":
    main()
