"""
Testes do motor de regras. Rodar com: pytest
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.analyzer import analisar_conteudo
from app.models import TipoConteudo, NivelConfiabilidade


def test_texto_neutro_sem_alertas():
    resultado = analisar_conteudo("O prefeito anunciou hoje o novo plano de mobilidade urbana.", TipoConteudo.texto)
    assert resultado.score >= 50
    assert len(resultado.alertas) == 0


def test_dominio_confiavel_aumenta_score():
    resultado = analisar_conteudo("Veja em https://g1.globo.com/noticia/exemplo", TipoConteudo.link)
    assert resultado.score > 60
    assert "g1.globo.com" in resultado.fontes


def test_dominio_suspeito_reduz_score():
    resultado = analisar_conteudo("Leia em https://boatos-urgentes.com/materia", TipoConteudo.link)
    assert resultado.score < 40
    assert resultado.nivel == NivelConfiabilidade.baixa
    assert any(a.tipo == "dominio_suspeito" for a in resultado.alertas)


def test_linguagem_urgencia_gera_alerta():
    resultado = analisar_conteudo("URGENTE! Compartilhe agora antes que apaguem esse vídeo!", TipoConteudo.texto)
    assert any(a.tipo == "linguagem_urgencia" for a in resultado.alertas)
    assert resultado.score < 60


def test_excesso_caixa_alta_gera_alerta():
    resultado = analisar_conteudo("ISSO É MUITO GRAVE E TODO MUNDO PRECISA SABER AGORA MESMO", TipoConteudo.texto)
    assert any(a.tipo == "excesso_caixa_alta" for a in resultado.alertas)


def test_imagem_retorna_placeholder_neutro():
    resultado = analisar_conteudo("foto.jpg", TipoConteudo.imagem)
    assert resultado.score == 50
    assert resultado.alertas[0].tipo == "modulo_indisponivel"


def test_score_nunca_sai_do_intervalo():
    resultado = analisar_conteudo(
        "URGENTE CHOCANTE BOMBA VERDADE OCULTA COMPARTILHE AGORA ANTES QUE APAGUEM "
        "https://boatos-urgentes.com/1 https://noticia-bomba.net/2",
        TipoConteudo.texto,
    )
    assert 0 <= resultado.score <= 100
