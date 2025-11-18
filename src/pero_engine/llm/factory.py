"""LLM Factory - Provider 선택"""
from typing import Optional
from .base import BaseLLM
from .ollama_client import OllamaClient
from .openai_client import OpenAIClient
from .claude_client import ClaudeClient


class LLMFactory:
    """LLM 클라이언트 팩토리"""

    @staticmethod
    def create(
        provider: str,
        # Ollama 설정
        ollama_base_url: Optional[str] = None,
        ollama_model: Optional[str] = None,
        ollama_auto_download: bool = True,
        # OpenAI 설정
        openai_api_key: Optional[str] = None,
        openai_model: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        # Claude 설정
        claude_api_key: Optional[str] = None,
        claude_model: Optional[str] = None,
        claude_base_url: Optional[str] = None,
    ) -> BaseLLM:
        """Provider에 따라 LLM 클라이언트 생성"""

        provider = provider.lower()

        if provider == "ollama":
            return OllamaClient(
                base_url=ollama_base_url or "http://localhost:11434",
                model=ollama_model or "llama3.2:3b",
                auto_download=ollama_auto_download,
            )

        elif provider == "openai":
            if not openai_api_key:
                raise ValueError(
                    "OpenAI를 사용하려면 API 키가 필요합니다. "
                    "config.yaml에서 llm.openai.api_key를 설정하세요."
                )

            return OpenAIClient(
                api_key=openai_api_key,
                model=openai_model or "gpt-3.5-turbo",
                base_url=openai_base_url,
            )

        elif provider == "claude":
            if not claude_api_key:
                raise ValueError(
                    "Claude를 사용하려면 API 키가 필요합니다. "
                    "config.yaml에서 llm.claude.api_key를 설정하세요."
                )

            return ClaudeClient(
                api_key=claude_api_key,
                model=claude_model or "claude-3-haiku-20240307",
                base_url=claude_base_url,
            )

        else:
            raise ValueError(
                f"지원하지 않는 LLM provider: {provider}. "
                f"사용 가능: ollama, openai, claude"
            )


async def test_factory():
    """Factory 테스트"""
    import asyncio

    print("🔍 LLM Factory 테스트...\n")

    # Ollama 테스트
    print("1. Ollama 클라이언트 생성")
    ollama = LLMFactory.create(provider="ollama", ollama_model="llama3.2:3b")
    print(f"   ✅ 생성됨: {type(ollama).__name__}")

    if await ollama.is_available():
        print("   ✅ Ollama 서버 연결 성공")
        response = await ollama.chat("Hi, say hello!")
        print(f"   🤖 응답: {response[:50]}...")
    else:
        print("   ⚠️  Ollama 서버에 연결할 수 없습니다.")

    print()

    # OpenAI 테스트 (API 키가 있을 경우)
    import os

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("2. OpenAI 클라이언트 생성")
        openai = LLMFactory.create(
            provider="openai", openai_api_key=openai_key, openai_model="gpt-3.5-turbo"
        )
        print(f"   ✅ 생성됨: {type(openai).__name__}")
    else:
        print("2. OpenAI 건너뛰기 (API 키 없음)")

    print()

    # Claude 테스트 (API 키가 있을 경우)
    claude_key = os.getenv("ANTHROPIC_API_KEY")
    if claude_key:
        print("3. Claude 클라이언트 생성")
        claude = LLMFactory.create(
            provider="claude",
            claude_api_key=claude_key,
            claude_model="claude-3-haiku-20240307",
        )
        print(f"   ✅ 생성됨: {type(claude).__name__}")
    else:
        print("3. Claude 건너뛰기 (API 키 없음)")

    print("\n✅ Factory 테스트 완료!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_factory())
