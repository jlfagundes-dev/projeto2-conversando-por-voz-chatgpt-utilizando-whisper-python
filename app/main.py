"""Assistente de Voz EVA - API Principal."""

import logging
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.routes import voice


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s %(name)s - %(message)s",
)

# Inicializa a aplicacao FastAPI
app = FastAPI(
    title="Assistente de Voz EVA",
    description="API de voz com Whisper, ChatGPT e gTTS",
    version="1.0.0",
)

# Configura CORS para permitir requisicoes do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra a rota principal da assistente de voz
app.include_router(voice.router)

# Monta os arquivos estaticos (HTML, CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve a interface web quando disponivel."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "aplicacao": "Assistente de Voz EVA",
        "descricao": "Assistente de voz com Whisper, ChatGPT e gTTS",
        "endpoints": {
            "POST /api/voice": "Recebe audio do microfone e devolve resposta em texto e voz",
            "GET /api/health": "Verifica saude da API",
        },
    }


if __name__ == "__main__":
    import uvicorn

    porta = int(os.getenv("PORT", 8000))
    recarregar = os.getenv("UVICORN_RELOAD", "false").lower() == "true"
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=porta,
        reload=recarregar,
    )
