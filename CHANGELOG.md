# Changelog — DarkTip Automação

Formato baseado em [Keep a Changelog](https://keepachangelog.com/).
Versionamento livre (não é uma lib publicada) — cada versão marca um
marco funcional do pipeline, não um release de software.

## [0.4.0] — 2026-08-23

### Added
- ConsoleTip: dashboard local em `console/consoletip.html`, gerado por
  `console/build_console.py` a partir do `status.json` mais recente.
  Mostra publicados/na fila/próximo post e a grade da semana com status
  por slot.

### Fixed
- `status.json` não tinha o campo `pillar` nas entradas — causava erro
  ao gerar o ConsoleTip. Backfillado a partir do `manifest.json`.

## [0.3.0] — 2026-08-23

### Added
- 20 tarefas agendadas one-shot (`darktip-YYYYMMDD-slot`), uma por post
  restante da semana, cada uma publicando via Windsor no horário
  estratégico do slot e atualizando `status.json` + commit/push
  automaticamente ao concluir.
- Tarefa recorrente `darktip-inventory-monitor` (diária, 08:00): conta
  posts restantes e, quando chegarem a ≤5, dispara sozinha a geração da
  próxima semana de conteúdo (sem agendar os horários — isso fica pra
  revisão manual).
- `posts/semana_2026-08-24/status.json`: rastreio de publicação por
  post (`scheduled` / `posted` + `media_id`).

### Changed
- Horários estratégicos definidos: dias úteis 09:00/12:30/19:00, fim de
  semana 10:00/14:00/20:00 (America/Sao_Paulo).

## [0.2.0] — 2026-08-23

### Added
- Semana completa de 21 posts (24–30/08/2026): 7 dias × 3 slots
  (mercados/estatísticas/curiosidades).
- `publish_manifest.json`: URLs públicas `raw.githubusercontent.com` +
  parâmetros prontos pra ação do Windsor (`create_carousel_post` /
  `create_image_post`) por post.
- Repositório `focadoctrl/darktip` tornado **público** (necessário pra
  Instagram/Windsor conseguir buscar as imagens).
- Primeiro post publicado ao vivo no Instagram (Match Odds, carrossel de
  8 imagens, media id `17974314479919256`).

### Changed
- Todas as 21 legendas atualizadas: CTA rotativo de seguir/acompanhar +
  disclaimer "Aposta não é investimento — envolve risco, jogue com
  responsabilidade. 18+" (substituindo o disclaimer anterior, mais
  genérico).

## [0.1.0] — 2026-08-23

### Added
- Repositório git inicializado em `darkdale/`, conectado a
  `github.com/focadoctrl/darktip` via GitHub CLI.
- `.gitignore` (exclui `venv/`, `.env`, `__pycache__`, `.DS_Store`).
- Commit inicial: código do projeto + imagens de teste
  (`media/darktip_test/`, `media/test_carousel/`).

## Pendências / próximos passos

- **Monitor de criativos**: banco de ideias de tópicos por pilar
  (mercados/estatísticas/curiosidades) com conexões entre eles
  (ex.: "Resultado Exato" estende "Match Odds"), pra dar sequência
  lógica ao conteúdo e alimentar a geração automática da
  `darktip-inventory-monitor` sem repetir tópicos. Ainda não construído.
- Commit da liberação de permissão do Windsor `execute_action` em
  `.claude/settings.local.json` ficou bloqueado pelo classificador de
  segurança — funciona localmente, mas não está versionado.
