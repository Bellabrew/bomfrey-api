# BOMFREY Insight API — v1 (motor de regras)

Backend real do BOMFREY Insight. Substitui o placeholder aleatório (`Math.random()`)
que estava no `index.html` da PWA por uma análise de verdade — determinística e
explicável, mesmo que ainda simples.

## O que já funciona nesta v1

- **Texto e link:** análise real, baseada em regras:
  - Domínio da fonte (lista de confiáveis/suspeitos em `app/domains.py`)
  - Linguagem de urgência/manipulação ("compartilhe agora", "antes que apaguem"...)
  - Clickbait ("você não vai acreditar", "bomba"...)
  - Excesso de CAIXA ALTA
- **Imagem, vídeo, áudio:** ainda retornam um resultado neutro (`score: 50`) sinalizando
  que o módulo de IA correspondente ainda não foi implementado — isso é intencional,
  não é um bug. Ver seção "Próximos passos".

## Rodar localmente

```bash
cd bomfrey-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Documentação interativa (Swagger) em `http://localhost:8000/docs` — dá pra testar
o endpoint direto pelo navegador, sem precisar de Postman ou curl.

## Rodar os testes

```bash
pytest tests/ -v
```

## Endpoint principal

```
POST /api/v1/analyze
Content-Type: application/json

{
  "conteudo": "https://exemplo.com/noticia",
  "tipo": "link"
}
```

Tipos aceitos: `texto`, `link`, `imagem`, `video`, `audio`.

Resposta segue exatamente a "Estrutura de Dados" definida no documento do produto:
`score`, `nivel`, `probabilidade_fake_news`, `probabilidade_ia`, `fontes`, `alertas`, `explicacao`.

## Conectar com o frontend (index.html da PWA)

No `index.html` que já está em `devlobbo.com/bomfrey/`, a função `runAnalysis()`
hoje gera números aleatórios. Trocar por uma chamada real:

```javascript
async function runAnalysis(){
  const text = document.getElementById('inputText').value.trim();
  if(!text){ return; }

  const tipo = text.startsWith('http') ? 'link' : 'texto';

  const response = await fetch('https://SEU_BACKEND_AQUI/api/v1/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conteudo: text, tipo: tipo })
  });
  const data = await response.json();

  // usar data.score, data.nivel, data.probabilidade_fake_news, etc.
  // no lugar dos valores aleatórios que estão lá hoje
}
```

**Importante:** o CORS em `app/main.py` já está liberado para `https://devlobbo.com`.
Se o backend for hospedado em outro domínio/subdomínio, ajustar a lista `allow_origins`.

## Onde hospedar este backend (opções com free tier)

- **Railway** ou **Render** — sobem direto de um repositório GitHub, com free tier
- Ambos suportam Python/FastAPI nativamente, sem Dockerfile obrigatório (mas dá pra
  usar Docker se preferirem, já que o documento do produto menciona isso)

## Próximos passos sugeridos

1. Hospedar esta API (Railway/Render) e trocar `SEU_BACKEND_AQUI` no frontend
2. Expandir `app/domains.py` com mais domínios confiáveis/suspeitos (hoje é uma
   lista pequena, só pra validar o mecanismo)
3. Adicionar banco de dados (PostgreSQL, como já definido na arquitetura) para
   guardar o **histórico de análises** por usuário — hoje cada chamada é isolada,
   sem persistência
4. Módulo de imagem: começar simples, verificando metadados EXIF e reverse image
   search antes de partir para detecção de deepfake por IA (que é mais cara e complexa)
5. Detecção de texto gerado por IA (`probabilidade_ia`, hoje sempre retorna 0):
   dá pra integrar uma API especializada nisso quando fizer sentido no orçamento
