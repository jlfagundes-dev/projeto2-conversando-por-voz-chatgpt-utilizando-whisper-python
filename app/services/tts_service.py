"""Servicos de sintese de voz com gTTS."""

from __future__ import annotations

import os
import uuid


def sintetizar_resposta(texto: str) -> dict:
    """Gera um arquivo MP3 a partir do texto recebido."""
    mensagem = (texto or "").strip()
    if not mensagem:
        raise ValueError("Texto vazio para sintese de voz.")

    try:
        from gtts import gTTS
    except ImportError as erro:
        raise RuntimeError("Dependencia ausente: instale 'gTTS' para sintetizar audio.") from erro

    idioma = os.getenv("GTTS_LANG", "pt")
    tld = os.getenv("GTTS_TLD", "com.br")
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static", "generated")
    os.makedirs(static_dir, exist_ok=True)

    nome_arquivo = f"resposta_{uuid.uuid4().hex}.mp3"
    caminho_audio = os.path.join(static_dir, nome_arquivo)

    sintetizador = gTTS(text=mensagem, lang=idioma, tld=tld, slow=False)
    sintetizador.save(caminho_audio)

    return {
        "audio_path": caminho_audio,
        "audio_url": f"/static/generated/{nome_arquivo}",
        "idioma": idioma,
    }
