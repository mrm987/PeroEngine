"""TTS 기본 인터페이스"""
from abc import ABC, abstractmethod
from pathlib import Path


class BaseTTS(ABC):
    """TTS 기본 클래스"""

    @abstractmethod
    async def synthesize(self, text: str, output_path: str) -> bool:
        """텍스트를 음성으로 변환하여 파일로 저장"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """서비스 사용 가능 여부"""
        pass
