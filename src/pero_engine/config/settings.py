"""PeroEngine 설정 관리"""
import yaml
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ServerConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000
    reload: bool = False


class SystemConfig(BaseModel):
    device: Literal["auto", "cpu", "cuda"] = "auto"
    mode: Literal["auto", "background", "active", "performance"] = "auto"
    models_dir: str = "./models"
    characters_dir: str = "./characters"


class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2:3b"
    model_active: str = "qwen2.5:7b"
    auto_download: bool = True


class OpenAIConfig(BaseModel):
    api_key: str = ""
    model: str = "gpt-3.5-turbo"


class ClaudeConfig(BaseModel):
    api_key: str = ""
    model: str = "claude-3-haiku-20240307"


class LLMConfig(BaseModel):
    provider: Literal["ollama", "openai", "claude"] = "ollama"
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    claude: ClaudeConfig = Field(default_factory=ClaudeConfig)


class EdgeTTSConfig(BaseModel):
    voice: str = "ko-KR-SunHiNeural"
    rate: str = "+0%"
    volume: str = "+0%"


class OpenAITTSConfig(BaseModel):
    api_key: str = ""
    model: str = "tts-1"
    voice: str = "alloy"


class TTSConfig(BaseModel):
    provider: Literal["edge", "openai"] = "edge"
    edge: EdgeTTSConfig = Field(default_factory=EdgeTTSConfig)
    openai: OpenAITTSConfig = Field(default_factory=OpenAITTSConfig)


class WhisperConfig(BaseModel):
    model: Literal["tiny", "base", "small", "medium", "large"] = "base"
    language: str = "ko"
    device: Literal["auto", "cpu", "cuda"] = "auto"


class ASRConfig(BaseModel):
    provider: Literal["whisper", "faster_whisper"] = "whisper"
    whisper: WhisperConfig = Field(default_factory=WhisperConfig)


class CharacterConfig(BaseModel):
    default_name: str = "Pero"
    default_persona: str = "당신은 친근하고 유쾌한 AI 어시스턴트입니다."


class AnimationConfig(BaseModel):
    fps: int = 30
    quality: Literal["low", "medium", "high"] = "medium"
    expressions: list[str] = ["neutral", "happy", "sad", "surprised", "thinking"]


class AdaptiveModeConfig(BaseModel):
    enable: bool = True
    gpu_threshold: int = 60
    check_interval: int = 5
    game_processes: list[str] = []


class Settings(BaseSettings):
    """PeroEngine 전체 설정"""

    server: ServerConfig = Field(default_factory=ServerConfig)
    system: SystemConfig = Field(default_factory=SystemConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    asr: ASRConfig = Field(default_factory=ASRConfig)
    character: CharacterConfig = Field(default_factory=CharacterConfig)
    animation: AnimationConfig = Field(default_factory=AnimationConfig)
    adaptive_mode: AdaptiveModeConfig = Field(default_factory=AdaptiveModeConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str = "config.yaml") -> "Settings":
        """YAML 파일에서 설정 로드"""
        path = Path(yaml_path)
        if not path.exists():
            print(f"⚠️  설정 파일을 찾을 수 없습니다: {yaml_path}")
            print("기본 설정을 사용합니다.")
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        return cls(**config_dict)


# 전역 설정 인스턴스
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """설정 인스턴스 가져오기 (싱글톤)"""
    global _settings
    if _settings is None:
        _settings = Settings.from_yaml()
    return _settings
