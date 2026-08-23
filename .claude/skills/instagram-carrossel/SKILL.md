---
name: instagram-carrossel
description: This skill should be used when the user asks to "criar carrossel", "gerar carrossel", "fazer carrossel", "novo carrossel", "carrossel sobre", "quero um carrossel", "cria um carrossel", "generate carousel", or mentions creating Instagram carousel content for @darktip.bet. Generates complete Instagram carousels with AI-written scripts and branded 1080x1080 slide images for the esoccer betting profile.
version: 1.0.0
---

# Instagram Carrossel — @darktip.bet

Gera carrosséis completos para o Instagram do @darktip.bet: roteiro com IA + imagens 1080×1080 renderizadas com a identidade visual da marca (vermelho `#e84118` + teal `#00c4bd` sobre fundo escuro `#080808`).

## Identidade Visual DarkTip

- **Fundo**: `#080808` (preto profundo)
- **Card**: `#111118`
- **Acento vermelho-laranja**: `#e84118` (fogo, urgência)
- **Acento teal**: `#00c4bd` (tech, precisão)
- **Barra superior**: gradiente vermelho → teal
- **Handle**: `@darktip.bet`

## Workflow

### 1. Obter o tópico

Se o usuário não informou o tópico, perguntar com `AskUserQuestion` antes de continuar. Exemplos de tópicos bons:

- "gestão de banca no esoccer"
- "top 5 mercados do fifinha"
- "erros que destroem sua banca"
- "como calcular o EV+"
- "ambas marcam: tudo que você precisa saber"

### 2. Gerar o carrossel

Executar o script com o venv do projeto:

```bash
cd /Users/santori/darkdale
venv/bin/python .claude/skills/instagram-carrossel/scripts/gerar_carrossel.py "TOPICO AQUI"
```

O script faz tudo automaticamente:
1. Chama `src/content/generator.py` → roteiro JSON com Claude AI
2. Chama `src/carousel/builder.py` → imagens 1080×1080
3. Salva roteiro em `posts/queue/carousel_TIMESTAMP_topico.json`
4. Salva slides em `media/carousels/TIMESTAMP_topico/slide_01.jpg` ... `slide_N.jpg`
5. Salva `result.json` com metadados

### 3. Exibir os slides

Após o script terminar, ler e exibir os slides gerados em ordem usando `Read` em cada `slide_XX.jpg`. Exibir no mínimo o slide de capa (01) e o último (CTA).

### 4. Exibir legenda e hashtags

Apresentar ao usuário:
- **Legenda completa** gerada pela IA
- **Hashtags** agrupadas por categoria
- **CTA** do post
- **Caminho dos arquivos** para upload

### 5. Próximos passos

Informar ao usuário as opções:
- Publicar diretamente: `python main.py publish posts/queue/ARQUIVO.json IMAGE_URL`
- Ajustar o roteiro: editar o JSON em `posts/queue/`
- Regenerar: rodar o skill novamente com um tópico diferente

## Estrutura de arquivos gerados

```
media/carousels/
└── TIMESTAMP_topico/
    ├── slide_01.jpg   ← Capa
    ├── slide_02.jpg   ← Conteúdo 1
    ├── ...
    ├── slide_N.jpg    ← CTA
    └── result.json    ← Metadados completos

posts/queue/
└── carousel_TIMESTAMP_topico.json  ← Roteiro + legenda + hashtags
```

## Tratamento de erros

Se o script falhar por falta de `ANTHROPIC_API_KEY`:
- Verificar se a chave está no `.env`
- Instruir: `echo "ANTHROPIC_API_KEY=sk-ant-..." >> /Users/santori/darkdale/.env`

Se o script falhar por módulo não encontrado:
- Verificar se o venv está ativo: `ls venv/bin/python`
- Reinstalar dependências: `venv/bin/pip install -r requirements.txt`

## Pilares de conteúdo para sugestão de tópicos

| Pilar | % | Exemplos de tópicos |
|---|---|---|
| Estratégia & Tips | 40% | mercados, handicap, value bets, odds |
| Educação & Mindset | 25% | EV+, gestão de banca, psicologia |
| Análise & Dados | 20% | ligas, estatísticas, tendências |
| Comunidade | 15% | perguntas, resultados, engajamento |
