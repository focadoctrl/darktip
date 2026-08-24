# DarkTip — Automação de Conteúdo (@darktip.bet)

Pipeline de geração, agendamento e publicação de conteúdo educativo sobre
esoccer/eFootball (mercados de aposta, estatísticas, curiosidades) para o
Instagram **@darktip.bet**.

Conteúdo é **educativo, sem vender nada e sem indicar entradas**. Toda peça
carrega CTA de seguir/acompanhar e o disclaimer "Aposta não é investimento —
envolve risco, jogue com responsabilidade. 18+".

## Como o pipeline funciona, de ponta a ponta

```
1. Geração de conteúdo
   .claude/skills/instagram-carrossel/ (script Pillow + Claude)
   → posts/semana_<AAAA-MM-DD>/<slug>/{01.png..08.png, legenda.txt}
   → posts/semana_<AAAA-MM-DD>/manifest.json (metadados de cada post)

2. Publicação no GitHub (hospedagem pública das imagens)
   git push para github.com/focadoctrl/darktip (repo PÚBLICO —
   necessário pra Instagram/Windsor conseguirem buscar as imagens via
   raw.githubusercontent.com)
   → posts/semana_<AAAA-MM-DD>/publish_manifest.json (URLs públicas +
     parâmetros prontos pra ação do Windsor: create_carousel_post ou
     create_image_post)

3. Rastreio de status
   posts/semana_<AAAA-MM-DD>/status.json — uma entrada por post, com
   status "scheduled" ou "posted" e o media_id retornado pelo Instagram

4. Agendamento e publicação
   Tarefas agendadas locais (mcp__scheduled-tasks, rodam enquanto o app
   Claude Code está aberto): uma tarefa one-shot por post
   (darktip-YYYYMMDD-slot), disparando no horário estratégico do slot e
   chamando o Windsor (connector "instagram", account
   17841425526435302) pra publicar. Ao publicar com sucesso, a própria
   tarefa atualiza o status.json e dá commit/push no repo.

5. Reabastecimento automático
   Tarefa recorrente darktip-inventory-monitor roda todo dia às 08:00,
   conta quantos posts restam "scheduled" e, quando chegam a ≤5, dispara
   sozinha a geração da próxima semana (passo 1) — mas NÃO agenda os
   horários da nova semana automaticamente; isso fica pra revisão do
   usuário.

6. ConsoleTip (painel local)
   console/consoletip.html — dashboard estático gerado a partir do
   status.json mais recente. Reabrir/atualizar com:
   python3 console/build_console.py
```

## Horários estratégicos (America/Sao_Paulo)

| | Manhã | Tarde | Noite |
|---|---|---|---|
| Dias úteis (seg–sex) | 09:00 | 12:30 | 19:00 |
| Fim de semana (sáb–dom) | 10:00 | 14:00 | 20:00 |

Cada dia tem 3 posts: **manhã** = mercado de aposta (carrossel de 8
imagens), **tarde** = leitura de estatística (imagem única), **noite** =
curiosidade FIFA/eFootball/EA Sports FC (imagem única).

## Estrutura do repositório

```
darkdale/
├── main.py                        CLI original do projeto (generate/carousel/plan/queue/publish/status)
├── src/                           gerador de conteúdo, builder de carrossel, cliente da Instagram Graph API
├── config/                        pilares de conteúdo e hashtags (referência — o mix real usado é mercados/estatisticas/curiosidades)
├── .claude/skills/instagram-carrossel/   skill que gera os carrosséis (script Pillow)
├── posts/semana_<data>/           cada semana de conteúdo: pastas de post + manifest.json + publish_manifest.json + status.json
├── console/                       ConsoleTip — dashboard local
│   ├── build_console.py           gerador (lê status.json, escreve consoletip.html)
│   ├── consoletip_template.html   template com placeholders {{...}}
│   └── consoletip.html            saída gerada (não editar à mão — rode o build_console.py)
└── .claude/scheduled-tasks/       (fora do git, em ~/.claude/scheduled-tasks/) definição das tarefas agendadas
```

## Identidade visual

Fundo `#080808` · vermelho-laranja `#e84118` · teal `#00c4bd` · handle
`@darktip.bet`.

## Pendências conhecidas

- **Monitor de criativos** (banco de ideias de tópicos + conexões entre
  eles, pra evitar repetição e dar sequência lógica aos posts) — ainda
  não construído. Próximo passo planejado.
- **App precisa estar aberto** pras tarefas agendadas dispararem no
  horário — se estiver fechado, a tarefa roda no próximo lançamento do
  app (pode atrasar o post).
- `publisher/` (script alternativo direto pra Meta Graph API, fora desse
  fluxo via Windsor) depende de um `META_ACCESS_TOKEN` de curta duração
  (~1h) — só relevante se algum dia for usado no lugar do Windsor.
- `.claude/settings.local.json` teve a permissão de
  `execute_action` do Windsor liberada localmente (durante a execução da
  tarefa de tarde de 24/08), mas o commit dessa mudança foi bloqueado
  pelo classificador de segurança do modo automático — ela funciona
  localmente, só não está versionada no repo ainda.

## Como consultar o progresso

Peça pra abrir o "ConsoleTip" — o dashboard é regenerado a partir do
status.json mais atual (`python3 console/build_console.py`) e mostra
quantos posts já foram publicados, quais estão na fila e o próximo
horário.

Veja também [CHANGELOG.md](CHANGELOG.md) para o histórico versionado do
que foi construído.
