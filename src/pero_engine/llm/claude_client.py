"""Claude LLM 클라이언트"""
from typing import AsyncIterator, Optional
from anthropic import AsyncAnthropic
from .base import BaseLLM


class ClaudeClient(BaseLLM):
    """Claude API 클라이언트"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        base_url: Optional[str] = None,
    ):
        if not api_key:
            raise ValueError("Claude API 키가 필요합니다.")

        self.model = model
        self.client = AsyncAnthropic(api_key=api_key, base_url=base_url)

    async def is_available(self) -> bool:
        """API 키 유효성 확인"""
        try:
            # 간단한 테스트 메시지
            await self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return True
        except Exception as e:
            print(f"⚠️  Claude API 오류: {e}")
            return False

    async def chat(
        self, message: str, context: list[dict] = None, system_prompt: str = None
    ) -> str:
        """채팅 (전체 응답 반환)"""
        messages = []

        # 대화 히스토리 추가
        if context:
            messages.extend(context)

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": message})

        try:
            # Claude는 system을 별도 파라미터로 전달
            kwargs = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": messages,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = await self.client.messages.create(**kwargs)

            return response.content[0].text

        except Exception as e:
            return f"Claude API 오류: {str(e)}"

    async def chat_stream(
        self, message: str, context: list[dict] = None
    ) -> AsyncIterator[str]:
        """채팅 (스트리밍)"""
        messages = context or []
        messages.append({"role": "user", "content": message})

        try:
            async with self.client.messages.stream(
                model=self.model, max_tokens=4096, messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            yield f"Claude API 오류: {str(e)}"

    async def close(self):
        """클라이언트 종료"""
        await self.client.close()


async def test_claude():
    """Claude 테스트"""
    import os
    import asyncio

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY 환경변수를 설정하세요.")
        return

    print("🔍 Claude 테스트 시작...")

    client = ClaudeClient(api_key=api_key, model="claude-3-haiku-20240307")

    # API 확인
    available = await client.is_available()
    if not available:
        print("❌ Claude API에 연결할 수 없습니다.")
        return

    print("✅ Claude API 연결 성공!")

    # 테스트 메시지
    print("\n💬 테스트 메시지 전송...")
    response = await client.chat("안녕! 간단히 자기소개 해줘.")
    print(f"🤖 응답: {response}")

    await client.close()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_claude())
