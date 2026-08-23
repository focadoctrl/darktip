import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

MEDIA_DIR = Path("media/carousels")
TEMPLATES_DIR = Path("media/templates")

# Paleta DarkTip — extraída do logo (vermelho-laranja + teal sobre escuro)
COLORS = {
    "bg_dark":      (8, 8, 8),
    "bg_card":      (17, 17, 24),
    "bg_card2":     (22, 22, 32),
    "accent_red":   (232, 65, 24),      # laranja-vermelho do logo
    "accent_teal":  (0, 196, 189),      # teal/ciano do logo
    "accent_orange":(255, 100, 40),     # laranja quente
    "text_white":   (255, 255, 255),
    "text_gray":    (150, 150, 165),
    "border":       (35, 35, 48),
    "border_red":   (80, 25, 10),
}

SIZE = (1080, 1080)
BRAND = "@darktip.bet"


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        font_name = "Arial Bold.ttf" if bold else "Arial.ttf"
        paths = [
            f"/System/Library/Fonts/Supplemental/{font_name}",
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'Bold' if bold else ''}.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
        for path in paths:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()


def _draw_gradient_bar(draw: ImageDraw.Draw, y0: int, y1: int):
    """Barra gradiente vermelho→teal da esquerda para direita."""
    w = SIZE[0]
    for x in range(w):
        t = x / w
        r = int(232 + (0 - 232) * t)
        g = int(65 + (196 - 65) * t)
        b = int(24 + (189 - 24) * t)
        draw.rectangle([x, y0, x + 1, y1], fill=(r, g, b))


def _draw_slide_base(draw: ImageDraw.Draw, slide_num: int, total: int):
    draw.rectangle([0, 0, SIZE[0], SIZE[1]], fill=COLORS["bg_dark"])
    draw.rectangle([0, 0, SIZE[0] - 1, SIZE[1] - 1], outline=COLORS["border"], width=2)

    # Barra superior gradiente vermelho→teal
    _draw_gradient_bar(draw, 0, 6)

    # Linha inferior fina teal
    draw.rectangle([0, SIZE[1] - 3, SIZE[0], SIZE[1]], fill=COLORS["accent_teal"])

    # Marca
    font_brand = _get_font(28, bold=True)
    draw.text((40, 28), BRAND, fill=COLORS["accent_teal"], font=font_brand)

    # Contador de slide
    font_small = _get_font(26)
    counter = f"{slide_num}/{total}"
    bbox = draw.textbbox((0, 0), counter, font=font_small)
    draw.text((SIZE[0] - bbox[2] - 40, 30), counter, fill=COLORS["text_gray"], font=font_small)


def _wrap_text(text: str, font, max_width: int, draw: ImageDraw.Draw) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_cover_slide(headline: str, subtext: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img)
    _draw_slide_base(draw, slide_num, total)

    # Elemento decorativo: círculo concêntrico estilo logo
    cx, cy = SIZE[0] // 2, 300
    for r, alpha in [(180, 12), (130, 18), (80, 25)]:
        overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        ov_draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                        outline=(232, 65, 24, alpha), width=2)
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

    font_title = _get_font(68, bold=True)
    font_sub = _get_font(38)

    lines = _wrap_text(headline, font_title, SIZE[0] - 120, draw)
    y = 400
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=COLORS["text_white"], font=font_title)
        y += 82

    y += 24
    sub_lines = _wrap_text(subtext, font_sub, SIZE[0] - 160, draw)
    for line in sub_lines:
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=COLORS["accent_teal"], font=font_sub)
        y += 52

    # Seta de arrastar
    font_arrow = _get_font(28)
    arrow_text = "→ Arraste para ver mais"
    bbox = draw.textbbox((0, 0), arrow_text, font=font_arrow)
    x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((x, SIZE[1] - 70), arrow_text, fill=COLORS["text_gray"], font=font_arrow)

    return img


def create_content_slide(headline: str, body: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img)
    _draw_slide_base(draw, slide_num, total)

    font_headline = _get_font(54, bold=True)
    font_body = _get_font(36)
    font_num = _get_font(48, bold=True)

    card_margin = 56
    card_y = 148
    card_h = SIZE[1] - 240
    draw.rounded_rectangle(
        [card_margin, card_y, SIZE[0] - card_margin, card_y + card_h],
        radius=18, fill=COLORS["bg_card"],
    )

    # Borda esquerda vermelha
    draw.rounded_rectangle(
        [card_margin, card_y, card_margin + 5, card_y + card_h],
        radius=4, fill=COLORS["accent_red"],
    )

    # Número do ponto em teal
    num_label = f"{slide_num - 1}."
    draw.text((card_margin + 28, card_y + 28), num_label,
              fill=COLORS["accent_red"], font=font_num)

    # Headline
    lines = _wrap_text(headline, font_headline, SIZE[0] - card_margin * 2 - 70, draw)
    y = card_y + 100
    for line in lines:
        draw.text((card_margin + 28, y), line, fill=COLORS["text_white"], font=font_headline)
        y += 64

    y += 16
    # Separador gradiente
    for px in range(card_margin + 28, SIZE[0] - card_margin - 28):
        t = (px - card_margin - 28) / (SIZE[0] - card_margin * 2 - 56)
        r = int(232 * (1 - t))
        g = int(65 + (196 - 65) * t)
        b = int(24 + (189 - 24) * t)
        draw.rectangle([px, y, px + 1, y + 2], fill=(r, g, b))
    y += 20

    # Body
    body_lines = _wrap_text(body, font_body, SIZE[0] - card_margin * 2 - 70, draw)
    for line in body_lines:
        draw.text((card_margin + 28, y), line, fill=COLORS["text_gray"], font=font_body)
        y += 48

    return img


def create_cta_slide(cta_text: str, handle: str, slide_num: int, total: int) -> Image.Image:
    img = Image.new("RGB", SIZE)
    draw = ImageDraw.Draw(img)
    _draw_slide_base(draw, slide_num, total)

    font_large = _get_font(60, bold=True)
    font_med = _get_font(38)
    font_handle = _get_font(44, bold=True)

    # Card central
    draw.rounded_rectangle([72, 280, SIZE[0] - 72, 800], radius=24, fill=COLORS["bg_card"])

    # Barra gradiente no card
    for x in range(72, SIZE[0] - 72):
        t = (x - 72) / (SIZE[0] - 144)
        r = int(232 + (0 - 232) * t)
        g = int(65 + (196 - 65) * t)
        b = int(24 + (189 - 24) * t)
        draw.rectangle([x, 280, x + 1, 356], fill=(r, g, b))
    # Arredondar corners da barra (simples — cobrir cantos com bg_card)
    draw.rectangle([72, 280, 96, 340], fill=COLORS["bg_card"])
    draw.rectangle([SIZE[0] - 96, 280, SIZE[0] - 72, 340], fill=COLORS["bg_card"])

    # Texto "SIGA AGORA"
    bbox = draw.textbbox((0, 0), "SIGA AGORA", font=font_large)
    x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((x, 294), "SIGA AGORA", fill=COLORS["bg_dark"], font=font_large)

    y = 400
    lines = _wrap_text(cta_text, font_med, SIZE[0] - 200, draw)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_med)
        x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, fill=COLORS["text_white"], font=font_med)
        y += 52

    y += 24
    bbox = draw.textbbox((0, 0), handle, font=font_handle)
    x = (SIZE[0] - (bbox[2] - bbox[0])) // 2
    draw.text((x, y), handle, fill=COLORS["accent_teal"], font=font_handle)

    return img


def build_carousel(script: dict, output_dir: Path = None) -> list[Path]:
    if output_dir is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = MEDIA_DIR / ts

    output_dir.mkdir(parents=True, exist_ok=True)
    slides = script.get("slides", [])
    total = len(slides)
    paths = []

    for slide in slides:
        num = slide["slide_number"]
        slide_type = slide.get("type", "conteudo")

        if slide_type == "capa":
            img = create_cover_slide(
                slide.get("headline", ""),
                slide.get("subtext", ""),
                num, total
            )
        elif slide_type in ("cta", "chamada"):
            img = create_cta_slide(
                slide.get("headline", "Siga para mais dicas!"),
                BRAND,
                num, total
            )
        else:
            img = create_content_slide(
                slide.get("headline", ""),
                slide.get("body", slide.get("subtext", "")),
                num, total
            )

        path = output_dir / f"slide_{num:02d}.jpg"
        img.save(path, "JPEG", quality=95)
        paths.append(path)
        print(f"  ✓ Slide {num}/{total} salvo: {path.name}")

    return paths
