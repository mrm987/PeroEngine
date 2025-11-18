"""Ollama LLM 클라이언트"""
import asyncio
import httpx
from typing import AsyncIterator, Optional
from .base import BaseLLM


class OllamaClient(BaseLLM):
    """Ollama 로컬 LLM 클라이언트"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b",
        auto_download: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.auto_download = auto_download
        self.client = httpx.AsyncClient(timeout=300.0)

    async def is_available(self) -> bool:
        """Ollama 서버 실행 중인지 확인"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def ensure_model_exists(self) -> bool:
        """모델이 존재하는지 확인하고, 없으면 다운로드"""
        try:
            # 설치된 모델 목록 가져오기
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code != 200:
                return False

            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if self.model in model_names:
                print(f"✅ 모델 '{self.model}' 이미 설치되어 있습니다.")
                return True

            if not self.auto_download:
                print(f"❌ 모델 '{self.model}'을 찾을 수 없습니다.")
                print(f"   다음 명령어로 설치하세요: ollama pull {self.model}")
                return False

            # 모델 자동 다운로드
            print(f"📥 모델 '{self.model}' 다운로드 중... (시간이 걸릴 수 있습니다)")
            pull_response = await self.client.post(
                f"{self.base_url}/api/pull", json={"name": self.model, "stream": False}
            )

            if pull_response.status_code == 200:
                print(f"✅ 모델 '{self.model}' 다운로드 완료!")
                return True
            else:
                print(f"❌ 모델 다운로드 실패: {pull_response.text}")
                return False

        except Exception as e:
            print(f"❌ 모델 확인 중 오류: {e}")
            return False

    async def chat(
        self, message: str, context: list[dict] = None, system_prompt: str = None
    ) -> str:
        """채팅 (전체 응답 반환)"""
        if not await self.ensure_model_exists():
            return "모델을 사용할 수 없습니다. Ollama가 실행 중인지 확인하세요."

        messages = []

        # 시스템 프롬프트 추가 (캐릭터 페르소나)
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 대화 히스토리 추가
        if context:
            messages.extend(context)

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": message})

        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
            )

            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                return f"오류: {response.status_code} - {response.text}"

        except Exception as e:
            return f"오류: {str(e)}"

    async def chat_stream(
        self, message: str, context: list[dict] = None
    ) -> AsyncIterator[str]:
        """채팅 (스트리밍)"""
        if not await self.ensure_model_exists():
            yield "모델을 사용할 수 없습니다."
            return

        messages = context or []
        messages.append({"role": "user", "content": message})

        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json

                        data = json.loads(line)
                        if "message" in data:
                            content = data["message"].get("content", "")
                            if content:
                                yield content

        except Exception as e:
            yield f"오류: {str(e)}"

    async def close(self):
        """클라이언트 종료"""
        await self.client.aclose()


async def test_ollama():
    """Ollama 테스트"""
    print("🔍 Ollama 테스트 시작...")

    client = OllamaClient(model="llama3.2:3b")

    # 서버 확인
    available = await client.is_available()
    if not available:
        print("❌ Ollama 서버에 연결할 수 없습니다.")
        print("   다음 명령어로 Ollama를 설치하세요:")
        print("   https://ollama.ai")
        return

    print("✅ Ollama 서버 연결 성공!")

    # 모델 다운로드 확인
    model_ok = await client.ensure_model_exists()
    if not model_ok:
        print("❌ 모델을 사용할 수 없습니다.")
        return

    # 테스트 메시지
    print("\n💬 테스트 메시지 전송...")
    response = await client.chat("안녕! 간단히 자기소개 해줘.")
    print(f"🤖 응답: {response}")

    await client.close()
    print("\n✅ 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_ollama())
