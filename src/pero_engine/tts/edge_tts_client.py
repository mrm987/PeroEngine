"""Edge TTS 클라이언트"""
import edge_tts
from pathlib import Path
from .base import BaseTTS


class EdgeTTSClient(BaseTTS):
    """Microsoft Edge TTS 클라이언트 (무료 API)"""

    def __init__(
        self, voice: str = "ko-KR-SunHiNeural", rate: str = "+0%", volume: str = "+0%"
    ):
        self.voice = voice
        self.rate = rate
        self.volume = volume

    async def is_available(self) -> bool:
        """항상 사용 가능 (인터넷 연결만 필요)"""
        return True

    async def synthesize(self, text: str, output_path: str) -> bool:
        """텍스트를 음성으로 변환"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            communicate = edge_tts.Communicate(
                text, self.voice, rate=self.rate, volume=self.volume
            )
            await communicate.save(str(output_file))

            return output_file.exists()

        except Exception as e:
            print(f"❌ TTS 변환 실패: {e}")
            return False

    @staticmethod
    async def list_voices():
        """사용 가능한 음성 목록"""
        voices = await edge_tts.list_voices()
        return voices


async def test_edge_tts():
    """Edge TTS 테스트"""
    print("🔍 Edge TTS 테스트 시작...")

    client = EdgeTTSClient(voice="ko-KR-SunHiNeural")

    # 테스트 문장
    text = "안녕하세요! 저는 페로 엔진입니다. 반갑습니다!"
    output_path = "test_output.mp3"

    print(f"💬 테스트 텍스트: {text}")
    print(f"🎵 음성 생성 중...")

    success = await client.synthesize(text, output_path)

    if success:
        print(f"✅ 음성 파일 생성 완료: {output_path}")
    else:
        print("❌ 음성 파일 생성 실패")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_edge_tts())
