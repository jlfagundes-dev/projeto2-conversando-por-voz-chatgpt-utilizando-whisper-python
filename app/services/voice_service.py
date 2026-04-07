"""Orquestra a experiência completa de voz: Whisper -> ChatGPT -> gTTS."""

from __future__ import annotations

import os

from app.services.chatgpt_service import gerar_resposta_chatgpt
from app.services.transcricao import transcrever_audio
from app.services.tts_service import sintetizar_resposta


def processar_audio(
    arquivo_audio: bytes,
    nome_arquivo: str,
    modelo_whisper: str | None = None,
) -> dict:
    """Processa um audio enviado pelo usuario e devolve resposta em texto e voz."""
    modelo = modelo_whisper or os.getenv("WHISPER_MODEL", "base")

    transcricao = transcrever_audio(
        arquivo_audio=arquivo_audio,
        modelo=modelo,
        idioma="pt",
        nome_arquivo=nome_arquivo or "audio.webm",
    )

    if not transcricao.get("sucesso"):
        return {
            "sucesso": False,
            "transcricao": "",
            "resposta": "",
            "audio_url": None,
            "modelo_whisper": modelo,
            "erro": transcricao.get("erro", "Falha ao transcrever audio."),
        }

    resposta = gerar_resposta_chatgpt(transcricao["transcricao"])
    audio = sintetizar_resposta(resposta["resposta"])

    return {
        "sucesso": True,
        "transcricao": transcricao["transcricao"],
        "confianca": transcricao.get("confianca", 0.0),
        "resposta": resposta["resposta"],
        "origem_resposta": resposta.get("origem", "mock"),
        "modelo_whisper": transcricao.get("modelo", modelo),
        "modelo_chat": resposta.get("modelo", os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")),
        "audio_url": audio["audio_url"],
        "idioma_tts": audio.get("idioma", "pt"),
    }
