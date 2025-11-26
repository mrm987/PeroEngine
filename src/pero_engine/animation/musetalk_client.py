"""MuseTalk 애니메이션 클라이언트"""
import asyncio
import os
from pathlib import Path
from typing import Optional
from .base import BaseAnimation


class MuseTalkClient(BaseAnimation):
    """MuseTalk 립싱크 애니메이션 클라이언트"""

    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "auto",
        fps: int = 25,
    ):
        """
        Args:
            model_path: MuseTalk 모델 경로 (None이면 자동 다운로드)
            device: 'auto', 'cpu', 'cuda'
            fps: 출력 비디오 FPS
        """
        self.model_path = model_path
        self.device = self._resolve_device(device)
        self.fps = fps
        self.initialized = False

    def _resolve_device(self, device: str) -> str:
        """디바이스 자동 감지"""
        if device == "auto":
            try:
                import torch

                return "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                return "cpu"
        return device

    async def is_available(self) -> bool:
        """MuseTalk 사용 가능 여부 확인"""
        try:
            # TODO: MuseTalk 라이브러리 import 테스트
            # import musetalk
            # return True

            # 현재는 구조만 구현
            print("⚠️  MuseTalk 라이브러리가 설치되지 않았습니다.")
            print("   GitHub에서 설치: https://github.com/TMElyralab/MuseTalk")
            return False

        except Exception as e:
            print(f"⚠️  MuseTalk 확인 중 오류: {e}")
            return False

    async def _initialize(self) -> bool:
        """MuseTalk 모델 초기화"""
        if self.initialized:
            return True

        try:
            # TODO: MuseTalk 모델 로드
            # from musetalk import MuseTalk
            # self.model = MuseTalk(model_path=self.model_path, device=self.device)

            print(f"✅ MuseTalk 초기화 완료 (Device: {self.device})")
            self.initialized = True
            return True

        except Exception as e:
            print(f"❌ MuseTalk 초기화 실패: {e}")
            return False

    async def generate(
        self, image_path: str, audio_path: str, output_path: str
    ) -> bool:
        """
        이미지 + 오디오 → 립싱크 비디오 생성

        Args:
            image_path: 캐릭터 이미지 경로
            audio_path: 오디오 파일 경로 (wav, mp3 등)
            output_path: 출력 비디오 경로 (.mp4)

        Returns:
            성공 여부
        """
        # 초기화
        if not await self._initialize():
            print("❌ MuseTalk가 초기화되지 않았습니다.")
            return False

        # 파일 존재 확인
        if not Path(image_path).exists():
            print(f"❌ 이미지를 찾을 수 없습니다: {image_path}")
            return False

        if not Path(audio_path).exists():
            print(f"❌ 오디오를 찾을 수 없습니다: {audio_path}")
            return False

        try:
            print(f"🎬 립싱크 비디오 생성 중...")
            print(f"   이미지: {image_path}")
            print(f"   오디오: {audio_path}")
            print(f"   출력: {output_path}")

            # TODO: 실제 MuseTalk 실행
            # result = await asyncio.to_thread(
            #     self.model.inference,
            #     source_image=image_path,
            #     driven_audio=audio_path,
            #     output_path=output_path,
            #     fps=self.fps,
            # )

            # 임시: 더미 구현
            print("⚠️  MuseTalk 라이브러리가 아직 통합되지 않았습니다.")
            print("   구조만 구현된 상태입니다.")
            return False

        except Exception as e:
            print(f"❌ 비디오 생성 실패: {e}")
            return False


async def test_musetalk():
    """MuseTalk 테스트"""
    print("🔍 MuseTalk 테스트 시작...")

    client = MuseTalkClient(device="auto", fps=25)

    # 사용 가능 여부 확인
    available = await client.is_available()
    if not available:
        print("❌ MuseTalk를 사용할 수 없습니다.")
        return

    print("✅ MuseTalk 사용 가능!")

    # 테스트 파일 경로 (예시)
    image_path = "test_character.png"
    audio_path = "test_audio.wav"
    output_path = "output_video.mp4"

    # 비디오 생성 테스트
    success = await client.generate(image_path, audio_path, output_path)

    if success:
        print(f"✅ 비디오 생성 성공: {output_path}")
    else:
        print("❌ 비디오 생성 실패")


if __name__ == "__main__":
    asyncio.run(test_musetalk())
