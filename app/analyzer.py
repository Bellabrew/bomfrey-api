"""
Motor de análise v1 — baseado em regras, sem dependência de IA paga.

Objetivo desta versão: ter um resultado REAL (determinístico, explicável) em vez
do placeholder aleatório do frontend, validando o fluxo ponta a ponta antes de
investir em modelos de IA para os módulos de imagem/vídeo/áudio.

Quando o motor de IA entrar (Insight Engine completo), esta função pode virar
apenas um dos "sinais" combinados no scoring final, em vez do resultado inteiro.
"""

import re
from urllib.parse import urlparse

from app.domains import DOMINIOS_CONFIAVEIS, DOMINIOS_SUSPEITOS
from app.models import Alerta, AnaliseResponse, NivelConfiabilidade, TipoConteudo

URL_REGEX = re.compile(r"https?://[^\s]+")

PALAVRAS_URGENCIA = [
    "compartilhe agora", "urgente", "antes que apaguem", "a mídia não mostra",
    "eles não querem que você saiba", "compartilhe antes",
]

PALAVRAS_CLICKBAIT = [
    "você não vai acreditar", "chocante", "bomba", "verdade oculta", "ninguém está falando sobre isso",
]


def _extrair_dominio(url: str) -> str | None:
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return None


def _checar_dominio(conteudo: str, alertas: list[Alerta], fontes: list[str]) -> int:
    """Retorna um ajuste de score (-40 a +25) baseado no domínio encontrado."""
    urls = URL_REGEX.findall(conteudo)
    if not urls:
        return 0

    ajuste_total = 0
    for url in urls:
        dominio = _extrair_dominio(url)
        if not dominio:
            continue
        fontes.append(dominio)

        if dominio in DOMINIOS_CONFIAVEIS:
            ajuste_total += 25
        elif dominio in DOMINIOS_SUSPEITOS:
            ajuste_total -= 40
            alertas.append(Alerta(
                tipo="dominio_suspeito",
                mensagem=f"O domínio '{dominio}' já foi associado a desinformação recorrente.",
                peso=40,
            ))
    return ajuste_total


def _checar_linguagem_manipulativa(conteudo: str, alertas: list[Alerta]) -> int:
    """Detecta padrões textuais típicos de conteúdo manipulativo/clickbait."""
    texto_lower = conteudo.lower()
    ajuste = 0

    achou_urgencia = any(p in texto_lower for p in PALAVRAS_URGENCIA)
    if achou_urgencia:
        ajuste -= 15
        alertas.append(Alerta(
            tipo="linguagem_urgencia",
            mensagem="O texto usa apelo de urgência típico de correntes e desinformação.",
            peso=15,
        ))

    achou_clickbait = any(p in texto_lower for p in PALAVRAS_CLICKBAIT)
    if achou_clickbait:
        ajuste -= 10
        alertas.append(Alerta(
            tipo="clickbait",
            mensagem="O texto usa expressões sensacionalistas comuns em clickbait.",
            peso=10,
        ))

    return ajuste


def _checar_excesso_caixa_alta(conteudo: str, alertas: list[Alerta]) -> int:
    """Textos com excesso de CAIXA ALTA tendem a ser sensacionalistas."""
    letras = [c for c in conteudo if c.isalpha()]
    if len(letras) < 20:
        return 0

    maiusculas = sum(1 for c in letras if c.isupper())
    proporcao = maiusculas / len(letras)

    if proporcao > 0.4:
        alertas.append(Alerta(
            tipo="excesso_caixa_alta",
            mensagem="Uso excessivo de letras maiúsculas, comum em conteúdo sensacionalista.",
            peso=10,
        ))
        return -10
    return 0


def analisar_conteudo(conteudo: str, tipo: TipoConteudo) -> AnaliseResponse:
    """
    Ponto de entrada do motor de regras v1.

    Só analisa texto e link de forma real nesta versão. Imagem, vídeo e áudio
    ainda não têm processamento de conteúdo (isso depende dos módulos de IA
    descritos no documento do produto) — por enquanto retornam um resultado
    neutro sinalizando que aquela análise ainda não está disponível.
    """
    if tipo in (TipoConteudo.imagem, TipoConteudo.video, TipoConteudo.audio):
        return AnaliseResponse(
            score=50,
            nivel=NivelConfiabilidade.moderada,
            probabilidade_fake_news=0,
            probabilidade_ia=0,
            fontes=[],
            alertas=[Alerta(
                tipo="modulo_indisponivel",
                mensagem=f"Análise de {tipo.value} ainda não está disponível nesta versão do motor.",
                peso=0,
            )],
            explicacao=(
                f"O módulo de análise de {tipo.value} ainda está em desenvolvimento. "
                "Este resultado é um placeholder neutro, não uma avaliação real do conteúdo."
            ),
        )

    alertas: list[Alerta] = []
    fontes: list[str] = []

    score = 60  # ponto de partida neutro
    score += _checar_dominio(conteudo, alertas, fontes)
    score += _checar_linguagem_manipulativa(conteudo, alertas)
    score += _checar_excesso_caixa_alta(conteudo, alertas)
    score = max(0, min(100, score))

    if score >= 70:
        nivel = NivelConfiabilidade.alta
    elif score >= 40:
        nivel = NivelConfiabilidade.moderada
    else:
        nivel = NivelConfiabilidade.baixa

    probabilidade_fake_news = max(0, min(100, 100 - score))

    if alertas:
        explicacao = (
            "Foram encontrados " + str(len(alertas)) + " ponto(s) de atenção no conteúdo: " +
            "; ".join(a.mensagem for a in alertas) + "."
        )
    else:
        explicacao = (
            "Não foram encontrados sinais claros de manipulação nas regras analisadas. "
            "Isso não é garantia de veracidade — recomendamos checar a fonte original."
        )

    return AnaliseResponse(
        score=score,
        nivel=nivel,
        probabilidade_fake_news=probabilidade_fake_news,
        probabilidade_ia=0,  # detecção de geração por IA ainda não implementada nesta v1
        fontes=fontes,
        alertas=alertas,
        explicacao=explicacao,
    )
