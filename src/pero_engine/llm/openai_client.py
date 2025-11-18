"""OpenAI LLM 클라이언트"""
from typing import AsyncIterator, Optional
from openai import AsyncOpenAI
from .base import BaseLLM


class OpenAIClient(BaseLLM):
    """OpenAI API 클라이언트"""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        base_url: Optional[str] = None,
    ):
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")

        self.model = model
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def is_available(self) -> bool:
        """API 키 유효성 확인"""
        try:
            # 간단한 테스트 요청
            await self.client.models.retrieve(self.model)
            return True
        except Exception as e:
            print(f"⚠️  OpenAI API 오류: {e}")
            return False

    async def chat(
        self, message: str, context: list[dict] = None, system_prompt: str = None
    ) -> str:
        """채팅 (전체 응답 반환)"""
        messages = []

        # 시스템 프롬프트 추가
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 대화 히스토리 추가
        if context:
            messages.extend(context)

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"OpenAI API 오류: {str(e)}"

    async def chat_stream(
        self, message: str, context: list[dict] = None
    ) -> AsyncIterator[str]:
        """채팅 (스트리밍)"""
        messages = context or []
        messages.append({"role": "user", "content": message})

        try:
            stream = await self.client.chat.completions.create(
                model=self.model, messages=messages, stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"OpenAI API 오류: {str(e)}"

    async def close(self):
        """클라이언트 종료"""
        await self.client.close()


async def test_openai():
    """OpenAI 테스트"""
    import os
    import asyncio

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY 환경변수를 설정하세요.")
        return

    print("🔍 OpenAI 테스트 시작...")

    client = OpenAIClient(api_key=api_key, model="gpt-3.5-turbo")

    # API 확인
    available = await client.is_available()
    if not available:
        print("❌ OpenAI API에 연결할 수 없습니다.")
        return

    print("✅ OpenAI API 연결 성공!")

    # 테스트 메시지
    print("\n💬 테스트 메시지 전송...")
    response = await client.chat("안녕! 간단히 자기소개 해줘.")
    print(f"🤖 응답: {response}")

    await client.close()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_openai())
