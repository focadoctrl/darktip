import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

POSTS_DIR = Path("posts")
QUEUE_DIR = POSTS_DIR / "queue"
PUBLISHED_DIR = POSTS_DIR / "published"
ARCHIVE_DIR = POSTS_DIR / "archive"


def save_post_to_queue(post_data: dict, scheduled_time: datetime = None) -> Path:
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = QUEUE_DIR / f"post_{timestamp}_{post_data.get('type', 'post')}.json"
    post_data["scheduled_for"] = (
        scheduled_time.isoformat() if scheduled_time else None
    )
    filename.write_text(json.dumps(post_data, ensure_ascii=False, indent=2))
    return filename


def get_queue() -> list[dict]:
    if not QUEUE_DIR.exists():
        return []
    posts = []
    for f in sorted(QUEUE_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        data["_file"] = str(f)
        posts.append(data)
    return posts


def mark_published(post_file: str, media_id: str):
    src = Path(post_file)
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(src.read_text())
    data["published_at"] = datetime.now().isoformat()
    data["instagram_media_id"] = media_id
    dest = PUBLISHED_DIR / src.name
    dest.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    src.unlink()


def show_queue():
    posts = get_queue()
    table = Table(title="Fila de Posts", show_header=True)
    table.add_column("Arquivo", style="dim")
    table.add_column("Tipo")
    table.add_column("Tópico")
    table.add_column("Agendado para")

    for p in posts:
        table.add_row(
            Path(p["_file"]).name,
            p.get("type", "—"),
            p.get("topic", "—"),
            p.get("scheduled_for") or "Sem agendamento",
        )

    console.print(table)
    if not posts:
        console.print("[yellow]Fila vazia. Use 'generate' para criar posts.[/yellow]")


def generate_schedule(week_plan: dict) -> list[dict]:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    day_map = {
        "segunda": 0, "terca": 1, "quarta": 2,
        "quinta": 3, "sexta": 4, "sabado": 5, "domingo": 6,
    }
    current_weekday = today.weekday()

    scheduled = []
    for day_name, offset in day_map.items():
        delta = (offset - current_weekday) % 7
        post_date = today + timedelta(days=delta)
        day_data = week_plan.get("days", {}).get(day_name, {})

        if "morning" in day_data:
            slot = day_data["morning"]
            scheduled.append({
                "day": day_name,
                "time": "09:00",
                "datetime": post_date.replace(hour=9).isoformat(),
                **slot,
            })

        if "evening" in day_data:
            slot = day_data["evening"]
            scheduled.append({
                "day": day_name,
                "time": "19:00",
                "datetime": post_date.replace(hour=19).isoformat(),
                **slot,
            })

    return scheduled
