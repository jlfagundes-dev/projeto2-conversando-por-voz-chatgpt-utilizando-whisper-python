"""Servicos de transcricao usando Whisper."""

import logging
import os
import tempfile
from functools import lru_cache


logger = logging.getLogger(__name__)


@lru_cache(maxsize=2)
def carregar_modelo_whisper(nome_modelo: str):
    """Carrega o modelo Whisper apenas uma vez por nome."""
    try:
        import whisper
    except ImportError as erro:
        raise RuntimeError(
            "Dependencia ausente: instale 'openai-whisper' para usar transcricao de audio."
        ) from erro
    return whisper.load_model(nome_modelo)


def transcrever_audio(
    arquivo_audio: bytes,
    modelo: str = "base",
    idioma: str = "pt",
    nome_arquivo: str = "audio.webm",
) -> dict:
    """Transcreve um audio em bytes para texto usando Whisper."""
    try:
        logger.info("Iniciando transcricao com Whisper modelo=%s", modelo)
        whisper_model = carregar_modelo_whisper(modelo)
        sufixo = os.path.splitext(nome_arquivo or "audio.webm")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as arquivo_temporario:
            arquivo_temporario.write(arquivo_audio)
            caminho_temporario = arquivo_temporario.name

        try:
            resultado = whisper_model.transcribe(
                caminho_temporario,
                language=idioma,
                task="transcribe",
                fp16=False,
                temperature=0,
            )
        finally:
            try:
                os.remove(caminho_temporario)
            except OSError:
                pass

        texto = (resultado.get("text", "") or "").strip()
        segmentos = resultado.get("segments", []) or []
        confianca = 1.0 if segmentos else 0.92

        return {
            "transcricao": texto,
            "confianca": float(confianca),
            "modelo": modelo,
            "sucesso": True,
        }
    except Exception:
        logger.exception("Erro durante a transcricao do audio")
        return {
            "transcricao": "",
            "confianca": 0.0,
            "modelo": modelo,
            "sucesso": False,
            "erro": "Falha ao transcrever audio.",
        }
