"""애니메이션 팩토리"""
from typing import Optional
from .base import BaseAnimation
from .musetalk_client import MuseTalkClient


class AnimationFactory:
    """애니메이션 클라이언트 생성 팩토리"""

    @staticmethod
    def create(
        provider: str = "musetalk",
        # MuseTalk 옵션
        musetalk_model_path: Optional[str] = None,
        musetalk_device: str = "auto",
        musetalk_fps: int = 25,
    ) -> BaseAnimation:
        """
        애니메이션 클라이언트 생성

        Args:
            provider: 'musetalk', 'sadtalker', 'wav2lip' 등
            musetalk_model_path: MuseTalk 모델 경로
            musetalk_device: MuseTalk 디바이스
            musetalk_fps: MuseTalk FPS

        Returns:
            BaseAnimation 인스턴스
        """
        if provider == "musetalk":
            return MuseTalkClient(
                model_path=musetalk_model_path,
                device=musetalk_device,
                fps=musetalk_fps,
            )
        # 향후 다른 애니메이션 방법 추가 가능
        # elif provider == "sadtalker":
        #     return SadTalkerClient(...)
        # elif provider == "wav2lip":
        #     return Wav2LipClient(...)
        else:
            raise ValueError(f"지원하지 않는 애니메이션 provider: {provider}")
