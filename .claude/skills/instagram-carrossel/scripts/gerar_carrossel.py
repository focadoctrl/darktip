#!/usr/bin/env python3
"""
Gerador de carrossel Instagram para @darktip.bet
Uso: python scripts/gerar_carrossel.py "topico do carrossel"
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # raiz do projeto

from src.content.generator import generate_carousel_script
from src.carousel.builder import build_carousel


def main():
    if len(sys.argv) < 2:
        print("Uso: python gerar_carrossel.py 'topico'")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    print(f"\n🎯 Gerando carrossel: {topic}")
    print("─" * 50)

    # 1. Gerar roteiro com IA
    print("⚙️  Gerando roteiro com Claude AI...")
    script = generate_carousel_script(topic)

    print(f"\n📋 Título: {script['title']}")
    print(f"   Slides: {len(script['slides'])}")

    # 2. Salvar roteiro na fila
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic[:30].replace(" ", "_").replace("/", "-")
    queue_dir = Path("posts/queue")
    queue_dir.mkdir(parents=True, exist_ok=True)
    script_path = queue_dir / f"carousel_{ts}_{safe_topic}.json"
    script_path.write_text(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"\n💾 Roteiro salvo: {script_path}")

    # 3. Renderizar slides
    print("\n🖼️  Renderizando slides 1080x1080...")
    output_dir = Path("media/carousels") / f"{ts}_{safe_topic}"
    slide_paths = build_carousel(script, output_dir)

    # 4. Resultado final
    print(f"\n{'─'*50}")
    print(f"✅ Carrossel gerado com sucesso!")
    print(f"   Slides: {len(slide_paths)} imagens em {output_dir}/")
    print(f"   Roteiro: {script_path}")
    print(f"\n📝 Legenda gerada:")
    print(f"   {script.get('caption', '')[:200]}...")
    print(f"\n#️⃣  Hashtags: {' '.join('#'+h for h in script.get('hashtags', [])[:8])}...")
    print(f"\n👉 CTA: {script.get('cta', '')}")

    # Output estruturado para o Claude ler
    result = {
        "topic": topic,
        "title": script["title"],
        "slides_count": len(slide_paths),
        "output_dir": str(output_dir),
        "script_path": str(script_path),
        "slide_paths": [str(p) for p in slide_paths],
        "caption": script.get("caption", ""),
        "hashtags": script.get("hashtags", []),
        "cta": script.get("cta", ""),
    }

    result_path = output_dir / "result.json"
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n📄 Resultado salvo em: {result_path}")
    return result


if __name__ == "__main__":
    main()
