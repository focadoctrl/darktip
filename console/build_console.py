#!/usr/bin/env python3
"""Regera console/consoletip.html a partir do status.json mais recente.

Uso: python3 console/build_console.py
Roda a partir de qualquer lugar (usa caminho absoluto do projeto).
"""
import glob
import json
import os
from datetime import datetime, date

PROJECT = "/Users/santori/darkdale"
POSTS_DIR = f"{PROJECT}/posts"
OUT_PATH = f"{PROJECT}/console/consoletip.html"

WEEKDAY_PT = {
    "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua", "Thursday": "Qui",
    "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom",
}
PILLAR_LABEL = {
    "mercados": "Mercados",
    "estatisticas": "Estatísticas",
    "curiosidades": "Curiosidades",
}


def latest_week_dir():
    candidates = sorted(glob.glob(f"{POSTS_DIR}/semana_*"))
    if not candidates:
        raise SystemExit("Nenhuma pasta semana_* encontrada em posts/")
    return candidates[-1]


def load_week(week_dir):
    with open(f"{week_dir}/status.json", encoding="utf-8") as f:
        status = json.load(f)
    manifest_path = f"{week_dir}/manifest.json"
    meta = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            for e in json.load(f):
                meta[e["folder"]] = {"n_images": e.get("n_images", 1), "pillar": e.get("pillar", "mercados")}
    for entry in status:
        m = meta.get(entry["folder"], {})
        entry["n_images"] = m.get("n_images", 1)
        entry.setdefault("pillar", m.get("pillar", "mercados"))
    return status


def slot_time(iso):
    dt = datetime.fromisoformat(iso)
    return dt.strftime("%H:%M")


def build_days(status):
    by_date = {}
    for e in status:
        by_date.setdefault(e["date"], []).append(e)
    days = []
    for d in sorted(by_date):
        dt = date.fromisoformat(d)
        weekday_en = dt.strftime("%A")
        is_weekend = weekday_en in ("Saturday", "Sunday")
        slots = sorted(by_date[d], key=lambda e: slot_time(e["scheduled_at"]))
        days.append({
            "date": d,
            "ddate": dt.strftime("%d/%m"),
            "dname": WEEKDAY_PT[weekday_en],
            "weekend": is_weekend,
            "slots": slots,
        })
    return days


def render_slot(e):
    posted = e["status"] == "posted"
    chip_cls = "posted" if posted else "scheduled"
    chip_label = "publicado" if posted else "agendado"
    pillar = e["pillar"]
    fmt = f'{e["n_images"]} imagens' if e["n_images"] > 1 else "imagem única"
    fmt_kind = "carrossel" if e["n_images"] > 1 else "único"
    extra = f' · media {e["media_id"]}' if posted and e.get("media_id") else ""
    return f'''
      <div class="slot {chip_cls}">
        <div class="slot-top"><span class="time mono">{slot_time(e["scheduled_at"])}</span><span class="chip {chip_cls}">{chip_label}</span></div>
        <span class="pillar {pillar}">{PILLAR_LABEL.get(pillar, pillar)} · {fmt_kind}</span>
        <span class="topic">{e["topic"]}</span>
        <span class="fmt">{fmt}{extra}</span>
      </div>'''


def render_day(day):
    cls = "day weekend" if day["weekend"] else "day"
    slots_html = "\n".join(render_slot(s) for s in day["slots"])
    return f'''
    <div class="{cls}">
      <div class="day-head"><span class="dname">{day["dname"]}</span><span class="ddate mono">{day["ddate"]}</span></div>
      {slots_html}
    </div>'''


def main():
    week_dir = latest_week_dir()
    week_name = os.path.basename(week_dir)
    status = load_week(week_dir)
    days = build_days(status)

    total = len(status)
    posted = sum(1 for e in status if e["status"] == "posted")
    remaining = total - posted
    next_up = next((e for e in sorted(status, key=lambda e: e["scheduled_at"]) if e["status"] != "posted"), None)
    next_str = f'{next_up["date"]} {slot_time(next_up["scheduled_at"])} · {next_up["topic"]}' if next_up else "—"

    days_html = "\n".join(render_day(d) for d in days)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    template_path = f"{PROJECT}/console/consoletip_template.html"
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    html = (
        template
        .replace("{{WEEK_NAME}}", week_name.replace("semana_", ""))
        .replace("{{DAYS}}", days_html)
        .replace("{{POSTED}}", f"{posted:02d}")
        .replace("{{REMAINING}}", f"{remaining:02d}")
        .replace("{{TOTAL}}", f"{total:02d}")
        .replace("{{NEXT}}", next_str)
        .replace("{{GENERATED_AT}}", generated_at)
    )

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"OK: {OUT_PATH}")
    print(f"Semana: {week_name} | publicados: {posted} | restantes: {remaining} | próximo: {next_str}")


if __name__ == "__main__":
    main()
