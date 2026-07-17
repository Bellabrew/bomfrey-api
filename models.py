"""
Schemas de request/response da API do BOMFREY Insight.

A estrutura de resposta segue o que já foi definido no documento do produto:
score de confiabilidade, nível, probabilidade de fake news, probabilidade de IA,
fontes, alertas e explicação.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TipoConteudo(str, Enum):
    texto = "texto"
    link = "link"
    imagem = "imagem"
    video = "video"
    audio = "audio"


class NivelConfiabilidade(str, Enum):
    alta = "alta"
    moderada = "moderada"
    baixa = "baixa"


class AnaliseRequest(BaseModel):
    conteudo: str = Field(..., description="Texto colado, URL, ou legenda associada à mídia")
    tipo: TipoConteudo = Field(default=TipoConteudo.texto)

    class Config:
        json_schema_extra = {
            "example": {
                "conteudo": "https://exemplo.com/noticia-urgente-compartilhe-agora",
                "tipo": "link",
            }
        }


class Alerta(BaseModel):
    tipo: str
    mensagem: str
    peso: int = Field(description="Quanto esse alerta pesou negativamente no score, de 0 a 100")


class AnaliseResponse(BaseModel):
    score: int = Field(ge=0, le=100, description="Score de confiabilidade, 0 a 100")
    nivel: NivelConfiabilidade
    probabilidade_fake_news: int = Field(ge=0, le=100)
    probabilidade_ia: int = Field(ge=0, le=100)
    fontes: List[str] = Field(default_factory=list)
    alertas: List[Alerta] = Field(default_factory=list)
    explicacao: str
