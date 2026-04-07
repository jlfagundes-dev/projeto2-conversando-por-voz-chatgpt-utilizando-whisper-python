# Copilot Instructions - EVA assistente de voz (Docker First)

## Objetivo do projeto

Este projeto deve entregar um assistente de voz que:

- recebe a pergunta por voz do usuario
- transcreve o audio com o Whisper da OpenAI
- envia o texto transcrito para a API do ChatGPT/OpenAI
- sintetiza a resposta em audio com Google Text-to-Speech (gTTS)
- funciona igual em desenvolvimento e producao
- sobe com um comando via Docker
- pode ser publicado no Render ou Railway

## Principio fundamental

O projeto nao deve depender de execucao direta com `python main.py`.

Sempre utilizar Docker ou docker-compose para rodar a aplicacao.

Exemplos esperados:

```bash
docker build -t eva-assistente-voz .
docker run -p 8000:8000 eva-assistente-voz
```

Ou:

```bash
docker compose up --build
```

## Arquitetura esperada

```text
/app
  /routes
  /services
  main.py

/static
  index.html

Dockerfile
docker-compose.yml
requirements.txt
README.md
```

Separacao obrigatoria:

- `routes`: endpoints FastAPI
- `services`: logica de transcricao, ChatGPT e TTS
- `main.py`: bootstrap da aplicacao
- `static/index.html`: interface simples para gravar audio e reproduzir resposta

## Stack tecnologica

- Backend: FastAPI
- IA de voz para texto: Whisper
- IA de respostas: API do ChatGPT/OpenAI
- Texto para voz: gTTS
- Frontend: HTML + JS simples
- Containerizacao: Docker
- Deploy: Render via Docker

Evitar:

- dependencia de ambiente local
- scripts fora do container
- configuracoes manuais para rodar
- frameworks pesados no frontend

## Requisitos funcionais obrigatorios

A aplicacao deve:

- captar audio do microfone ou receber upload de audio
- transcrever com Whisper
- enviar a transcricao para o ChatGPT
- gerar a resposta em texto
- converter a resposta em audio com gTTS
- retornar a resposta em texto e o arquivo/URL de audio gerado
- permitir reproducao da resposta no navegador

Fluxo esperado:

1. usuario fala
2. o audio e gravado
3. Whisper transcreve
4. ChatGPT responde
5. gTTS sintetiza a resposta
6. o navegador reproduz o audio retornado

## Diretrizes de backend

- manter separacao clara entre rotas e servicos
- isolar a logica de Whisper, ChatGPT e gTTS em services
- usar variaveis de ambiente para chaves e configuracoes
- ler a porta pela variavel `PORT` com fallback para `8000`
- registrar logs simples no console

## Diretrizes de Docker

O Dockerfile deve:

- usar `python:3.11-slim`
- definir `WORKDIR /app`
- instalar somente o necessario
- copiar apenas os arquivos do projeto
- expor a porta `8000`
- iniciar com `uvicorn`

Exemplo esperado:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

O docker-compose deve permitir execucao com:

```bash
docker compose up --build
```

Exemplo minimo:

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WHISPER_MODEL=base
    restart: always
```

## Interface

A interface deve ser simples, funcional e direta:

- botao para gravar audio
- indicador de gravacao
- area de historico de conversa
- reproduzir a resposta em audio
- visual limpo, sem bibliotecas pesadas

## Deploy no Render

O projeto deve ser compativel com:

- deploy via Docker
- start automatico pelo container
- sem comandos adicionais manuais

A documentacao deve informar:

- descricao do projeto
- como rodar com Docker
- como acessar localmente
- como publicar no Render
- variaveis de ambiente necessarias

## Regras obrigatorias

- nao rodar sem Docker
- nao criar multiplos ambientes sem necessidade
- nao depender de configuracao manual no host
- nao usar caminhos absolutos

## Diferencial esperado

- experiencia real de assistente de voz
- integracao completa entre voz, IA e audio sintetizado
- resposta inteligente e reproduzida em voz
- demonstracao clara de valor para atendimento ou automacao

## Padroes de codigo

- utilizar tipagem explicita sempre que possivel (type hints)
- evitar funcoes com mais de 30 linhas
- nomes de funcoes devem descrever claramente a acao
- nao duplicar logica entre services
- manter funcoes puras sempre que possivel
- evitar codigo "magico" sem explicacao

Exemplo:

transcribe_audio() ✔  
process() ❌

## Engenharia de prompt (obrigatorio)

A chamada para o ChatGPT deve conter contexto claro.

Exemplo:

- definir papel do assistente
- limitar tamanho da resposta
- manter foco em contexto financeiro

Exemplo esperado:

"Você é um assistente financeiro. Responda de forma objetiva, clara e com no máximo 3 frases."

## Tratamento de erros

- sempre tratar excecoes nos services
- nunca expor erro interno diretamente para o usuario
- retornar mensagens amigaveis
- logar erros no console

Exemplo:

try:
  ...
except Exception as e:
  logar erro
  retornar resposta padrao

## Logs

- registrar inicio e fim de cada requisicao
- logar tempo de processamento
- logar erros
- nao logar dados sensiveis

Exemplo:

[INFO] request recebida
[INFO] audio transcrito
[INFO] resposta gerada
[ERROR] falha no whisper

## Seguranca

- nunca expor a OPENAI_API_KEY no codigo
- sempre usar variaveis de ambiente
- validar tamanho do audio enviado
- limitar tamanho da requisicao

## Contrato da API

Endpoint: POST /api/voice

Request:
- arquivo de audio (multipart/form-data)

Response:
{
  "transcription": "texto",
  "response": "resposta do modelo",
  "audio_url": "url ou caminho do audio"
}

## Performance

- evitar recarregar modelo Whisper a cada requisicao
- inicializar modelo uma unica vez
- reutilizar instancia sempre que possivel\

## Testabilidade

- services devem ser independentes das rotas
- logica deve ser testavel isoladamente
- evitar dependencia direta de request dentro dos services

## Regra de ouro

Se nao roda via Docker e nao pode ser testado via API, esta incompleto.
