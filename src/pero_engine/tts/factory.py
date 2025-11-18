"""TTS Factory - Provider 선택"""
from typing import Optional
from .base import BaseTTS
from .edge_tts_client import EdgeTTSClient
from .openai_tts_client import OpenAITTSClient


class TTSFactory:
    """TTS 클라이언트 팩토리"""

    @staticmethod
    def create(
        provider: str,
        # Edge TTS 설정
        edge_voice: Optional[str] = None,
        edge_rate: Optional[str] = None,
        edge_volume: Optional[str] = None,
        # OpenAI TTS 설정
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        openai_voice: Optional[str] = None,
    ) -> BaseTTS:
        """Provider에 따라 TTS 클라이언트 생성"""

        provider = provider.lower()

        if provider == "edge":
            return EdgeTTSClient(
                voice=edge_voice or "ko-KR-SunHiNeural",
                rate=edge_rate or "+0%",
                volume=edge_volume or "+0%",
            )

        elif provider == "openai":
            if not openai_api_key:
                raise ValueError(
                    "OpenAI TTS를 사용하려면 API 키가 필요합니다. "
                    "config.yaml에서 tts.openai.api_key를 설정하세요."
                )

            return OpenAITTSClient(
                api_key=openai_api_key,
                model=openai_model or "tts-1",
                voice=openai_voice or "alloy",
            )

        else:
            raise ValueError(
                f"지원하지 않는 TTS provider: {provider}. " f"사용 가능: edge, openai"
            )


async def test_factory():
    """Factory 테스트"""
    import asyncio

    print("🔍 TTS Factory 테스트...\n")

    # Edge TTS 테스트
    print("1. Edge TTS 클라이언트 생성")
    edge = TTSFactory.create(provider="edge", edge_voice="ko-KR-SunHiNeural")
    print(f"   ✅ 생성됨: {type(edge).__name__}")

    success = await edge.synthesize("안녕하세요!", "test_edge.mp3")
    if success:
        print("   ✅ 음성 생성 성공")
    else:
        print("   ❌ 음성 생성 실패")

    print()

    # OpenAI TTS 테스트 (API 키가 있을 경우)
    import os

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("2. OpenAI TTS 클라이언트 생성")
        openai_tts = TTSFactory.create(
            provider="openai",
            openai_api_key=openai_key,
            openai_model="tts-1",
            openai_voice="alloy",
        )
        print(f"   ✅ 생성됨: {type(openai_tts).__name__}")

        success = await openai_tts.synthesize("Hello!", "test_openai.mp3")
        if success:
            print("   ✅ 음성 생성 성공")
        else:
            print("   ❌ 음성 생성 실패")
    else:
        print("2. OpenAI TTS 건너뛰기 (API 키 없음)")

    print("\n✅ Factory 테스트 완료!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_factory())
