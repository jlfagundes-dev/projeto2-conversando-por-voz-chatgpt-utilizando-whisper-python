"""Rotas da assistente de voz."""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.voice_service import processar_audio

router = APIRouter(prefix="/api", tags=["voice"])
logger = logging.getLogger(__name__)


class VoiceResponse(BaseModel):
    sucesso: bool
    transcricao: str = ""
    confianca: float = 0.0
    resposta: str = ""
    origem_resposta: str = "mock"
    modelo_whisper: str = "small"
    modelo_chat: str = "llama-3.1-8b-instant"
    audio_url: str | None = None
    idioma_tts: str = "pt"
    erro: str | None = None


@router.post("/voice", response_model=VoiceResponse)
async def voice(audio: UploadFile = File(...)) -> VoiceResponse:
    """Recebe audio do microfone e devolve resposta falada."""
    inicio = time.perf_counter()
    logger.info("[VOICE] request recebida")

    try:
        conteudo = await audio.read()
        if not conteudo:
            raise HTTPException(status_code=400, detail="Nao recebi audio para processar.")

        resultado = processar_audio(
            arquivo_audio=conteudo,
            nome_arquivo=audio.filename or "audio.webm",
        )

        if not resultado.get("sucesso"):
            logger.error("[VOICE] falha no pipeline: %s", resultado.get("erro", "erro desconhecido"))
            raise HTTPException(
                status_code=422,
                detail=resultado.get("erro", "Nao foi possivel processar o audio."),
            )

        tempo_ms = (time.perf_counter() - inicio) * 1000
        logger.info("[VOICE] request finalizada com sucesso em %.2fms", tempo_ms)
        return VoiceResponse(**resultado)
    except HTTPException:
        raise
    except Exception:
        logger.exception("[VOICE] erro interno ao processar audio")
        raise HTTPException(status_code=500, detail="Erro interno ao processar audio.")


@router.get("/health")
async def health_check() -> dict:
    """Verifica se a API e o pipeline estao ativos."""
    return {
        "status": "ok",
        "servico": "Assistente de Voz EVA",
        "fluxo": "EVA - Assistente Financeiro por Voz",
    }
