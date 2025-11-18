"""Whisper ASR 클라이언트"""
import whisper
import torch
from pathlib import Path
from .base import BaseASR


class WhisperClient(BaseASR):
    """OpenAI Whisper ASR 클라이언트"""

    def __init__(self, model: str = "base", language: str = "ko", device: str = "auto"):
        self.model_name = model
        self.language = language

        # 디바이스 자동 감지
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.model = None
        print(f"🎤 Whisper ASR 초기화 (모델: {model}, 디바이스: {self.device})")

    def _load_model(self):
        """모델 지연 로딩"""
        if self.model is None:
            print(f"📥 Whisper 모델 '{self.model_name}' 로딩 중...")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✅ 모델 로딩 완료!")

    async def is_available(self) -> bool:
        """항상 사용 가능 (로컬 모델)"""
        return True

    async def transcribe(self, audio_path: str) -> str:
        """음성 파일을 텍스트로 변환"""
        try:
            self._load_model()

            audio_file = Path(audio_path)
            if not audio_file.exists():
                return f"오류: 파일을 찾을 수 없습니다 - {audio_path}"

            print(f"🎧 음성 인식 중: {audio_path}")

            # Whisper 추론
            result = self.model.transcribe(
                str(audio_file), language=self.language, fp16=(self.device == "cuda")
            )

            text = result["text"].strip()
            print(f"✅ 인식 완료: {text}")

            return text

        except Exception as e:
            print(f"❌ 음성 인식 실패: {e}")
            return f"오류: {str(e)}"


async def test_whisper():
    """Whisper 테스트 (음성 파일 필요)"""
    print("🔍 Whisper ASR 테스트 시작...")

    client = WhisperClient(model="base", language="ko")

    # 테스트용 음성 파일이 있다면
    test_file = "test_audio.mp3"
    if Path(test_file).exists():
        text = await client.transcribe(test_file)
        print(f"📝 인식된 텍스트: {text}")
    else:
        print(f"⚠️  테스트 음성 파일이 없습니다: {test_file}")
        print("   TTS로 생성한 파일을 사용하거나, 직접 녹음한 파일을 넣어주세요.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_whisper())
