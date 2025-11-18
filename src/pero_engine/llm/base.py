"""LLM 기본 인터페이스"""
from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseLLM(ABC):
    """LLM 기본 클래스"""

    @abstractmethod
    async def chat(self, message: str, context: list[dict] = None) -> str:
        """일반 채팅"""
        pass

    @abstractmethod
    async def chat_stream(
        self, message: str, context: list[dict] = None
    ) -> AsyncIterator[str]:
        """스트리밍 채팅"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """서비스 사용 가능 여부"""
        pass
