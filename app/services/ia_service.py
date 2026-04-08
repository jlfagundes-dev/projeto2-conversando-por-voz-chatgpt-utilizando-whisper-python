"""Servicos de geracao de resposta usando a API da Groq."""

from __future__ import annotations

import logging
import os


logger = logging.getLogger(__name__)


def _resposta_mock(pergunta: str) -> str:
    pergunta_normalizada = (pergunta or "").strip().lower()
    if not pergunta_normalizada:
        return "Nao consegui entender a pergunta. Pode repetir com mais detalhes?"

    if any(termo in pergunta_normalizada for termo in ("pagamento", "boleto", "fatura")):
        return "Posso te ajudar com informacoes sobre pagamento, segunda via e status de cobranca."

    if any(termo in pergunta_normalizada for termo in ("cancelar", "cancelamento")):
        return "Entendi. Posso iniciar um fluxo de cancelamento e orientar os proximos passos."

    if any(termo in pergunta_normalizada for termo in ("suporte", "erro", "problema")):
        return "Vamos resolver isso. Me diga o que aconteceu para eu te orientar da melhor forma."

    return "Recebi sua mensagem e posso ajudar com atendimento, suporte, pagamentos e cancelamentos."


def gerar_resposta_ia(pergunta: str) -> dict:
    """Gera resposta com Groq e usa fallback local caso a chave nao exista."""
    texto = (pergunta or "").strip()
    modelo = os.getenv("GROQ_CHAT_MODEL", "llama-3.1-8b-instant")
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not texto:
        return {
            "resposta": "Nao recebi nenhuma pergunta para responder.",
            "origem": "mock",
            "modelo": modelo,
        }

    if not api_key:
        logger.warning("GROQ_API_KEY nao configurada, usando resposta mock")
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
        }

    try:
        from groq import Groq
    except ImportError as erro:
        logger.exception("Falha ao importar SDK da Groq")
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
            "erro": "Servico de IA temporariamente indisponivel.",
        }

    try:
        client = Groq(api_key=api_key)
        logger.info("Gerando resposta via Groq com modelo=%s", modelo)
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce e um assistente financeiro. "
                        "Responda de forma objetiva, clara e com no maximo 3 frases. "
                        "Mantenha foco em contexto bancario e seguranca financeira."
                    ),
                },
                {"role": "user", "content": texto},
            ],
            temperature=0.4,
        )
        texto_resposta = (resposta.choices[0].message.content or "").strip()
        if not texto_resposta:
            texto_resposta = _resposta_mock(texto)

        return {
            "resposta": texto_resposta,
            "origem": "groq",
            "modelo": modelo,
        }
    except Exception as erro:
        logger.exception("Falha na chamada da Groq")
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
            "erro": "Nao foi possivel gerar resposta agora.",
        }
