"""애니메이션 팩토리"""
from typing import Optional
from .base import BaseAnimation
from .musetalk_client import MuseTalkClient
from .liveportrait_client import LivePortraitClient


class AnimationFactory:
    """애니메이션 클라이언트 생성 팩토리"""

    @staticmethod
    def create(
        provider: str = "liveportrait",
        # MuseTalk 옵션
        musetalk_model_path: Optional[str] = None,
        musetalk_device: str = "auto",
        musetalk_fps: int = 25,
        # LivePortrait 옵션
        liveportrait_path: Optional[str] = None,
        joyvasa_path: Optional[str] = None,
        liveportrait_device: str = "auto",
        liveportrait_fps: int = 30,
        liveportrait_use_tensorrt: bool = True,
        liveportrait_backend: str = "joyvasa",
    ) -> BaseAnimation:
        """
        애니메이션 클라이언트 생성

        Args:
            provider: 'liveportrait', 'musetalk', 'sadtalker', 'wav2lip' 등
            musetalk_*: MuseTalk 관련 옵션
            liveportrait_*: LivePortrait 관련 옵션

        Returns:
            BaseAnimation 인스턴스
        """
        if provider == "liveportrait":
            return LivePortraitClient(
                liveportrait_path=liveportrait_path,
                joyvasa_path=joyvasa_path,
                device=liveportrait_device,
                fps=liveportrait_fps,
                use_tensorrt=liveportrait_use_tensorrt,
                backend=liveportrait_backend,
            )
        elif provider == "musetalk":
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
