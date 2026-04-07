"""Rotas da assistente de voz."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.voice_service import processar_audio

router = APIRouter(prefix="/api", tags=["voice"])


class VoiceResponse(BaseModel):
    sucesso: bool
    transcricao: str = ""
    confianca: float = 0.0
    resposta: str = ""
    origem_resposta: str = "mock"
    modelo_whisper: str = "small"
    modelo_chat: str = "gpt-4o-mini"
    audio_url: str | None = None
    idioma_tts: str = "pt"
    erro: str | None = None


@router.post("/voice", response_model=VoiceResponse)
async def voice(audio: UploadFile = File(...)) -> VoiceResponse:
    """Recebe audio do microfone ou upload e devolve resposta falada."""
    try:
        conteudo = await audio.read()
        resultado = processar_audio(
            arquivo_audio=conteudo,
            nome_arquivo=audio.filename or "audio.webm",
        )
        return VoiceResponse(**resultado)
    except Exception as erro:
        raise HTTPException(status_code=500, detail=f"Erro ao processar audio: {erro}")


@router.get("/health")
async def health_check() -> dict:
    """Verifica se a API e o pipeline estao ativos."""
    return {
        "status": "ok",
        "servico": "Assistente de Voz EVA",
        "fluxo": "Whisper + ChatGPT + gTTS",
    }
