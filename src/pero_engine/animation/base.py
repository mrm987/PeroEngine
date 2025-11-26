"""애니메이션 기본 인터페이스"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseAnimation(ABC):
    """애니메이션 기본 클래스"""

    @abstractmethod
    async def generate(
        self, image_path: str, audio_path: str, output_path: str
    ) -> bool:
        """
        이미지 + 오디오 → 립싱크 비디오 생성

        Args:
            image_path: 캐릭터 이미지 경로
            audio_path: 오디오 파일 경로
            output_path: 출력 비디오 경로

        Returns:
            성공 여부
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """서비스 사용 가능 여부"""
        pass
