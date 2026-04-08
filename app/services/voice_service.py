"""Orquestra a experiência completa de voz: Whisper -> ChatGPT -> gTTS."""

from __future__ import annotations

import logging
import os
import time

from app.services.ia_service import gerar_resposta_ia
from app.services.transcricao import transcrever_audio
from app.services.tts_service import sintetizar_resposta


logger = logging.getLogger(__name__)


def processar_audio(
    arquivo_audio: bytes,
    nome_arquivo: str,
    modelo_whisper: str | None = None,
) -> dict:
    """Processa um audio enviado pelo usuario e devolve resposta em texto e voz."""
    inicio = time.perf_counter()
    modelo = modelo_whisper or os.getenv("WHISPER_MODEL", "base")
    logger.info("Pipeline iniciado: modelo_whisper=%s arquivo=%s", modelo, nome_arquivo)

    transcricao = transcrever_audio(
        arquivo_audio=arquivo_audio,
        modelo=modelo,
        idioma="pt",
        nome_arquivo=nome_arquivo or "audio.webm",
    )

    if not transcricao.get("sucesso"):
        logger.error("Falha na transcricao: %s", transcricao.get("erro", "erro desconhecido"))
        return {
            "sucesso": False,
            "transcricao": "",
            "resposta": "",
            "audio_url": None,
            "modelo_whisper": modelo,
            "erro": "Nao foi possivel transcrever o audio. Tente novamente.",
        }

    try:
        resposta = gerar_resposta_ia(transcricao["transcricao"])
        audio = sintetizar_resposta(resposta["resposta"])
    except Exception:
        logger.exception("Falha no pipeline de resposta/sintese")
        return {
            "sucesso": False,
            "transcricao": transcricao.get("transcricao", ""),
            "resposta": "",
            "audio_url": None,
            "modelo_whisper": transcricao.get("modelo", modelo),
            "erro": "Nao foi possivel gerar a resposta em voz agora.",
        }

    tempo_total = (time.perf_counter() - inicio) * 1000
    logger.info("Pipeline finalizado com sucesso em %.2fms", tempo_total)

    return {
        "sucesso": True,
        "transcricao": transcricao["transcricao"],
        "confianca": transcricao.get("confianca", 0.0),
        "resposta": resposta["resposta"],
        "origem_resposta": resposta.get("origem", "mock"),
        "modelo_whisper": transcricao.get("modelo", modelo),
        "modelo_chat": resposta.get("modelo", os.getenv("GROQ_CHAT_MODEL", "llama-3.1-8b-instant")),
        "audio_url": audio["audio_url"],
        "idioma_tts": audio.get("idioma", "pt"),
    }
