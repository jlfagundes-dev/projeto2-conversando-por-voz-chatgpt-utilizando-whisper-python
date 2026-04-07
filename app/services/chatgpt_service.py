"""Servicos de geracao de resposta usando a API da OpenAI."""

from __future__ import annotations

import os


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


def gerar_resposta_chatgpt(pergunta: str) -> dict:
    """Gera resposta com OpenAI e usa fallback local caso a chave nao exista."""
    texto = (pergunta or "").strip()
    modelo = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not texto:
        return {
            "resposta": "Nao recebi nenhuma pergunta para responder.",
            "origem": "mock",
            "modelo": modelo,
        }

    if not api_key:
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
        }

    try:
        from openai import OpenAI
    except ImportError as erro:
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
            "erro": f"openai indisponivel: {erro}",
        }

    try:
        client = OpenAI(api_key=api_key)
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Voce e a EVA, uma assistente de voz em portugues do Brasil. "
                        "Responda de forma clara, curta, natural e profissional."
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
            "origem": "openai",
            "modelo": modelo,
        }
    except Exception as erro:
        return {
            "resposta": _resposta_mock(texto),
            "origem": "mock",
            "modelo": modelo,
            "erro": str(erro),
        }
