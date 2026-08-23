#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv

load_dotenv()
console = Console()


@click.group()
def cli():
    """Darkdale - Gerenciador de Instagram para Esoccer Betting"""
    pass


@cli.command()
def status():
    """Mostra status da conta e fila de posts"""
    from src.instagram.api import InstagramAPI
    from src.scheduler.planner import show_queue, get_queue

    try:
        api = InstagramAPI()
        info = api.get_account_info()
        console.print(Panel(
            f"[bold green]@{info.get('username')}[/bold green]\n"
            f"Seguidores: [cyan]{info.get('followers_count', 0):,}[/cyan]\n"
            f"Posts: [cyan]{info.get('media_count', 0)}[/cyan]\n"
            f"Bio: {info.get('biography', '')}",
            title="Conta Instagram",
        ))
    except ValueError as e:
        console.print(f"[yellow]API não configurada: {e}[/yellow]")

    queue = get_queue()
    console.print(f"\n[bold]Fila de posts:[/bold] {len(queue)} post(s) aguardando")
    show_queue()


@cli.command()
@click.option("--type", "-t", "post_type",
              type=click.Choice(["estrategia", "educacional", "analise", "motivacional", "noticias"]),
              default="estrategia", show_default=True)
@click.option("--topic", "-p", default=None, help="Tópico específico do post")
@click.option("--queue/--no-queue", default=True, help="Salvar na fila")
def generate(post_type, topic, queue):
    """Gera um post com IA"""
    from src.content.generator import generate_post
    from src.scheduler.planner import save_post_to_queue

    console.print(f"[cyan]Gerando post do tipo '{post_type}'...[/cyan]")
    post = generate_post(topic=topic, post_type=post_type)

    console.print(Panel(
        f"[bold]{post['hook']}[/bold]\n\n"
        f"{post['caption'][:500]}{'...' if len(post['caption']) > 500 else ''}\n\n"
        f"[green]CTA:[/green] {post['cta']}\n"
        f"[yellow]Melhor horário:[/yellow] {post['best_time']}\n"
        f"[dim]Arte:[/dim] {post.get('notes', '')}",
        title=f"Post: {post['topic']}",
    ))

    if queue:
        path = save_post_to_queue(post)
        console.print(f"[green]✓ Salvo na fila:[/green] {path}")

    return post


@cli.command()
@click.argument("topic")
@click.option("--build/--no-build", default=True, help="Gerar imagens dos slides")
def carousel(topic, build):
    """Gera um carrossel completo com roteiro e imagens"""
    from src.content.generator import generate_carousel_script
    from src.carousel.builder import build_carousel
    from src.scheduler.planner import save_post_to_queue

    console.print(f"[cyan]Gerando roteiro do carrossel: '{topic}'...[/cyan]")
    script = generate_carousel_script(topic)

    console.print(f"\n[bold green]{script['title']}[/bold green]")
    console.print(f"[cyan]{len(script['slides'])} slides[/cyan]\n")

    for slide in script["slides"]:
        console.print(f"[bold]Slide {slide['slide_number']}[/bold] [{slide['type']}]: {slide['headline']}")
        if slide.get("body"):
            console.print(f"  {slide['body'][:100]}...")

    script_path = Path("posts/queue") / f"carousel_{topic[:20].replace(' ', '_')}.json"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    console.print(f"\n[green]✓ Roteiro salvo:[/green] {script_path}")

    if build:
        console.print("\n[cyan]Gerando imagens...[/cyan]")
        from src.carousel.builder import build_carousel
        paths = build_carousel(script)
        console.print(f"[green]✓ {len(paths)} slides gerados em media/carousels/[/green]")

    return script


@cli.command()
def plan():
    """Gera plano semanal de conteúdo"""
    from src.content.generator import generate_weekly_plan
    from src.scheduler.planner import generate_schedule

    console.print("[cyan]Gerando plano semanal...[/cyan]")
    week = generate_weekly_plan()

    console.print(f"\n[bold green]Tema da semana:[/bold green] {week['week_theme']}\n")

    day_names = {"segunda": "Seg", "terca": "Ter", "quarta": "Qua",
                 "quinta": "Qui", "sexta": "Sex", "sabado": "Sab", "domingo": "Dom"}

    for day_key, day_label in day_names.items():
        day_data = week.get("days", {}).get(day_key, {})
        morning = day_data.get("morning", {})
        evening = day_data.get("evening", {})
        console.print(
            f"[bold]{day_label}[/bold]  "
            f"[green]09h[/green] {morning.get('topic', '—')} [{morning.get('format', '—')}]  "
            f"[yellow]19h[/yellow] {evening.get('topic', '—')} [{evening.get('format', '—')}]"
        )

    plan_path = Path("posts") / "weekly_plan.json"
    plan_path.write_text(json.dumps(week, ensure_ascii=False, indent=2))
    console.print(f"\n[green]✓ Plano salvo:[/green] {plan_path}")


@cli.command()
def queue():
    """Mostra fila de posts pendentes"""
    from src.scheduler.planner import show_queue
    show_queue()


@cli.command()
@click.argument("post_file")
@click.argument("image_url")
def publish(post_file, image_url):
    """Publica um post da fila no Instagram"""
    from src.instagram.api import InstagramAPI
    from src.scheduler.planner import mark_published

    post_data = json.loads(Path(post_file).read_text())
    caption = post_data["caption"]
    hashtags = " ".join(f"#{h}" for h in post_data.get("hashtags", []))
    full_caption = f"{caption}\n\n{hashtags}"

    console.print(f"[cyan]Publicando no Instagram...[/cyan]")
    api = InstagramAPI()
    media_id = api.post_image(image_url, full_caption)
    mark_published(post_file, media_id)
    console.print(f"[green]✓ Publicado! Media ID: {media_id}[/green]")


@cli.command()
def setup():
    """Guia de configuração inicial"""
    guide = """
## Configuração do Darkdale

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
```
Edite o `.env` com suas credenciais.

### 3. Configurar conta Instagram Business
1. Vá para facebook.com e crie uma **Página** para o seu perfil
2. No Instagram, vá em Configurações → Conta → Mudar para conta profissional
3. Selecione **Criador** ou **Empresa** e vincule à sua Facebook Page

### 4. Criar App no Meta Developers
1. Acesse: developers.facebook.com
2. Clique em **Criar App** → Tipo: **Business**
3. Adicione o produto **Instagram Graph API**
4. Gere um User Token com permissões:
   - instagram_basic
   - instagram_content_publish
   - pages_read_engagement
5. Troque pelo **Page Access Token** (longa duração)

### 5. Pegar o Instagram Business Account ID
```bash
python main.py get-ig-id
```

### 6. Configurar ANTHROPIC_API_KEY
Acesse console.anthropic.com para pegar sua chave.
"""
    console.print(Markdown(guide))


if __name__ == "__main__":
    cli()
