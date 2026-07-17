"""
BOMFREY Insight — API de análise (v1, motor baseado em regras).

Rodar localmente:
    uvicorn app.main:app --reload --port 8000

Docs automáticas (Swagger):
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analyzer import analisar_conteudo
from app.models import AnaliseRequest, AnaliseResponse

app = FastAPI(
    title="BOMFREY Insight API",
    description="Análise de confiabilidade de textos, links, imagens, vídeos e áudios.",
    version="1.0.0",
)

# CORS liberado para o domínio da PWA. Ajustar em produção para restringir
# apenas ao(s) domínio(s) reais em vez de "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://devlobbo.com",
        "http://localhost:5500",  # útil pra testar o index.html localmente
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health_check():
    """Endpoint simples pra verificar se a API está no ar."""
    return {"status": "ok"}


@app.post("/api/v1/analyze", response_model=AnaliseResponse)
def analyze(request: AnaliseRequest):
    """
    Recebe um texto, link, ou referência a mídia e retorna o score de
    confiabilidade junto com a explicação e os alertas encontrados.
    """
    conteudo = request.conteudo.strip()
    if not conteudo:
        raise HTTPException(status_code=422, detail="O campo 'conteudo' não pode estar vazio.")

    return analisar_conteudo(conteudo, request.tipo)
