"""PeroEngine - 이미지 한 장으로 AI 어시스턴트 만들기"""

__version__ = "0.1.0"
__author__ = "PeroEngine Team"

from .config import get_settings
from .llm import OllamaClient
from .tts import EdgeTTSClient

# ASR은 선택적으로 import (whisper 설치 안 되어 있으면 건너뜀)
try:
    from .asr import WhisperClient
    __all__ = [
        "get_settings",
        "OllamaClient",
        "EdgeTTSClient",
        "WhisperClient",
    ]
except ImportError:
    __all__ = [
        "get_settings",
        "OllamaClient",
        "EdgeTTSClient",
    ]
