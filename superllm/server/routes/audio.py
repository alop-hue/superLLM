from __future__ import annotations

import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from superllm.inference.audio import AudioInferenceEngine

router = APIRouter()
_engine: AudioInferenceEngine | None = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = AudioInferenceEngine()
    return _engine


class TTSRequest(BaseModel):
    text: str
    voice: str | None = None
    language: str = "en"
    model: str = "bark"


class TranscribeResponse(BaseModel):
    text: str
    language: str = "unknown"
    segments: list[dict] = []
    duration_ms: float = 0.0


@router.post("/audio/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Form("whisper-small"),
    task: str = Form("transcribe"),
    language: str | None = Form(None),
):
    engine = get_engine()

    try:
        audio_bytes = await file.read()
        result = await engine.transcribe(audio_bytes, task=task)

        return TranscribeResponse(
            text=result.get("text", ""),
            language=result.get("language", "unknown"),
            segments=result.get("segments", []),
            duration_ms=result.get("duration_ms", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


@router.post("/audio/synthesize")
async def synthesize_speech(request: TTSRequest):
    engine = get_engine()
    start = time.time()

    try:
        audio_data = await engine.synthesize(
            text=request.text,
            voice=request.voice,
            language=request.language,
        )
        from fastapi.responses import Response
        return Response(
            content=audio_data,
            media_type="audio/wav",
            headers={
                "X-Model": request.model,
                "X-Duration-Ms": str((time.time() - start) * 1000),
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {e}")


@router.get("/audio/models")
async def list_audio_models():
    engine = get_engine()
    models = await engine.list_models()
    return {
        "models": [{"id": m.id, "object": m.object} for m in models],
        "total": len(models),
    }
