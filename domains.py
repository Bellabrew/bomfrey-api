"""
Listas de referência de domínios para o motor de regras.

Isto é um ponto de partida pequeno e deliberadamente simples — o ideal a médio
prazo é mover isso para o banco de dados (tabela `fontes_confiaveis`) e permitir
atualização sem precisar de deploy, além de integrar com bases mais completas
(ex: checadores de fatos, agências de imprensa reconhecidas).
"""

# Fontes com histórico editorial estabelecido (não é endosso de conteúdo específico,
# apenas sinal de que é uma organização jornalística reconhecida)
DOMINIOS_CONFIAVEIS = {
    "g1.globo.com",
    "bbc.com",
    "bbc.co.uk",
    "reuters.com",
    "apnews.com",
    "folha.uol.com.br",
    "estadao.com.br",
    "oglobo.globo.com",
    "agenciabrasil.ebc.com.br",
    "gov.br",
    "who.int",
    "saude.gov.br",
}

# Padrões associados a sites de baixa qualidade/desinformação recorrente.
# Lista propositalmente pequena no MVP - o objetivo aqui é o mecanismo, não a cobertura.
DOMINIOS_SUSPEITOS = {
    "boatos-urgentes.com",
    "noticia-bomba.net",
    "verdade-oculta.info",
}
