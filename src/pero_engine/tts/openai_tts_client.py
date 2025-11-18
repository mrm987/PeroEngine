"""OpenAI TTS 클라이언트"""
from pathlib import Path
from openai import AsyncOpenAI
from .base import BaseTTS


class OpenAITTSClient(BaseTTS):
    """OpenAI TTS API 클라이언트"""

    def __init__(
        self,
        api_key: str,
        model: str = "tts-1",
        voice: str = "alloy",
    ):
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")

        self.model = model  # tts-1 or tts-1-hd
        self.voice = voice  # alloy, echo, fable, onyx, nova, shimmer
        self.client = AsyncOpenAI(api_key=api_key)

    async def is_available(self) -> bool:
        """API 키 유효성 확인"""
        try:
            # 간단한 테스트 (짧은 텍스트)
            response = await self.client.audio.speech.create(
                model=self.model, voice=self.voice, input="test"
            )
            return True
        except Exception as e:
            print(f"⚠️  OpenAI TTS API 오류: {e}")
            return False

    async def synthesize(self, text: str, output_path: str) -> bool:
        """텍스트를 음성으로 변환"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            response = await self.client.audio.speech.create(
                model=self.model, voice=self.voice, input=text
            )

            # 스트리밍으로 파일에 저장
            response.stream_to_file(str(output_file))

            return output_file.exists()

        except Exception as e:
            print(f"❌ OpenAI TTS 변환 실패: {e}")
            return False


async def test_openai_tts():
    """OpenAI TTS 테스트"""
    import os
    import asyncio

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY 환경변수를 설정하세요.")
        return

    print("🔍 OpenAI TTS 테스트 시작...")

    client = OpenAITTSClient(api_key=api_key, voice="alloy")

    # 테스트 문장
    text = "Hello! I am PeroEngine. Nice to meet you!"
    output_path = "test_openai_tts.mp3"

    print(f"💬 테스트 텍스트: {text}")
    print(f"🎵 음성 생성 중...")

    success = await client.synthesize(text, output_path)

    if success:
        print(f"✅ 음성 파일 생성 완료: {output_path}")
    else:
        print("❌ 음성 파일 생성 실패")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_openai_tts())
