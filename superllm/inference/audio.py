from __future__ import annotations

import io
import os
import tempfile
import time
from collections.abc import AsyncGenerator
from enum import Enum

from superllm.inference.base import (
    InferenceEngine,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
)


class AudioTask(str, Enum):
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"
    SYNTHESIZE = "synthesize"
    GENERATE = "generate"


class AudioConfig:
    whisper_model_size: str = "small"
    device: str = "cpu"
    compute_type: str = "int8"
    tts_model: str = "bark"
    sample_rate: int = 24000
    max_audio_length: int = 30


class AudioInferenceEngine(InferenceEngine):
    def __init__(self):
        self._whisper = None
        self._tts = None
        self._faster_whisper = None
        self._config = AudioConfig()

    @property
    def name(self) -> str:
        return "audio"

    async def _load_whisper(self, model_size: str = "small"):
        if self._whisper is not None:
            return
        try:
            import whisper

            self._whisper = whisper.load_model(model_size, device=self._config.device)
        except ImportError:
            try:
                from faster_whisper import WhisperModel

                self._faster_whisper = WhisperModel(
                    model_size_or_path=model_size,
                    device=self._config.device,
                    compute_type=self._config.compute_type,
                )
            except ImportError:
                raise RuntimeError(
                    "No Whisper installation found. "
                    "Install: pip install openai-whisper or pip install faster-whisper"
                )

    async def _load_tts(self, model: str = "bark"):
        if self._tts is not None:
            return
        if model == "bark":
            try:
                from bark import SAMPLE_RATE, generate_audio, preload_models

                preload_models()
                self._tts = {"type": "bark", "generate": generate_audio, "sample_rate": SAMPLE_RATE}
            except ImportError:
                raise RuntimeError(
                    "Bark not installed. Run: pip install 'git+https://github.com/suno-ai/bark.git'"
                )
        elif model == "xtts":
            try:
                from TTS.api import TTS

                self._tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
                self._tts = {"type": "xtts", "model": self._tts}
            except ImportError:
                raise RuntimeError("XTTS not installed. Run: pip install TTS")

    async def transcribe(self, audio_input: bytes | str, task: str = "transcribe") -> dict:
        await self._load_whisper()
        start = time.time()

        if isinstance(audio_input, str):
            audio_path = audio_input
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_input)
                audio_path = f.name

        try:
            if self._whisper is not None:
                result = self._whisper.transcribe(
                    audio_path,
                    task=task,
                    temperature=0.0,
                    language=None,
                    verbose=False,
                )
                segments = []
                for seg in result.get("segments", []):
                    segments.append(
                        {
                            "start": seg.get("start", 0),
                            "end": seg.get("end", 0),
                            "text": seg.get("text", "").strip(),
                        }
                    )
                elapsed = (time.time() - start) * 1000
                return {
                    "text": result.get("text", "").strip(),
                    "language": result.get("language", "unknown"),
                    "segments": segments,
                    "duration_ms": elapsed,
                }
            elif self._faster_whisper is not None:
                segments, info = self._faster_whisper.transcribe(audio_path, task=task)
                text_parts = []
                seg_list = []
                for seg in segments:
                    text_parts.append(seg.text)
                    seg_list.append(
                        {
                            "start": seg.start,
                            "end": seg.end,
                            "text": seg.text.strip(),
                        }
                    )
                elapsed = (time.time() - start) * 1000
                return {
                    "text": " ".join(text_parts).strip(),
                    "language": info.language if info else "unknown",
                    "segments": seg_list,
                    "duration_ms": elapsed,
                }
        finally:
            if not isinstance(audio_input, str) and os.path.exists(audio_path):
                os.unlink(audio_path)

        return {"text": "", "language": "unknown", "segments": [], "duration_ms": 0}

    async def synthesize(self, text: str, voice: str | None = None, language: str = "en") -> bytes:
        await self._load_tts()

        if self._tts["type"] == "bark":
            import numpy as np

            audio_array = self._tts["generate"](text)
            sample_rate = self._tts["sample_rate"]
            buf = io.BytesIO()
            try:
                import scipy.io.wavfile as wavfile

                wavfile.write(buf, sample_rate, (audio_array * 32767).astype(np.int16))
            except ImportError:
                import wave

                with wave.open(buf, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(sample_rate)
                    wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
            buf.seek(0)
            return buf.getvalue()

        elif self._tts["type"] == "xtts":
            speaker = voice or "default"
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                output_path = f.name
            self._tts["model"].tts_to_file(
                text=text,
                speaker_wav=speaker,
                language=language,
                file_path=output_path,
            )
            with open(output_path, "rb") as f:
                audio_data = f.read()
            os.unlink(output_path)
            return audio_data

        return b""

    async def chat(self, request: InferenceRequest) -> InferenceResponse:
        audio_task = AudioTask.TRANSCRIBE
        text = " ".join(m.get("content", "") for m in request.messages if m.get("role") == "user")

        if audio_task == AudioTask.TRANSCRIBE:
            if isinstance(text, str) and len(text) < 100:
                audio_path = text.strip()
                if os.path.exists(audio_path):
                    result = await self.transcribe(audio_path)
                    return InferenceResponse(
                        model=request.model or "whisper-small",
                        content=result.get("text", ""),
                        tokens_in=0,
                        tokens_out=0,
                        total_time_ms=result.get("duration_ms", 0),
                    )
            return InferenceResponse(
                model=request.model or "whisper-small",
                content="Audio task requires an audio file path or bytes input.",
                tokens_in=0,
                tokens_out=0,
            )

        return InferenceResponse(
            model=request.model or "bark",
            content="Audio inference not yet supported for this task.",
            tokens_in=0,
            tokens_out=0,
        )

    async def chat_stream(self, request: InferenceRequest) -> AsyncGenerator[str, None]:
        response = await self.chat(request)
        yield response.content

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="whisper-large-v3"),
            ModelInfo(id="whisper-small"),
            ModelInfo(id="faster-whisper"),
            ModelInfo(id="bark"),
            ModelInfo(id="xtts-v2"),
        ]

    async def health(self) -> ProviderHealth:
        start = time.time()
        try:
            latency = (time.time() - start) * 1000
            return ProviderHealth(name="audio", healthy=True, latency_ms=latency)
        except Exception as e:
            return ProviderHealth(name="audio", healthy=False, latency_ms=0, error=str(e))

    async def close(self):
        self._whisper = None
        self._tts = None
        self._faster_whisper = None
