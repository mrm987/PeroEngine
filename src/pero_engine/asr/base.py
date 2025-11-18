"""ASR 기본 인터페이스"""
from abc import ABC, abstractmethod


class BaseASR(ABC):
    """ASR 기본 클래스"""

    @abstractmethod
    async def transcribe(self, audio_path: str) -> str:
        """음성 파일을 텍스트로 변환"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """서비스 사용 가능 여부"""
        pass
