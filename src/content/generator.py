import os
import json
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

SYSTEM_PROMPT = """Você é o gestor de conteúdo do perfil @darktip.bet no Instagram — especialista em apostas esportivas focado em eSoccer (FIFA/EA FC / fifinha).
Seu trabalho é criar conteúdo de alta qualidade para o nicho de esoccer betting no Brasil.

IDENTIDADE DO PERFIL:
- Handle: @darktip.bet
- Foco: eSoccer / Fifinha (apostas esportivas virtuais)
- Tom: Especialista, direto, confiante — mas sempre responsável
- Público: Apostadores brasileiros de 18-35 anos
- Idioma: Português brasileiro informal mas profissional
- Estilo: Direto ao ponto, com dados reais, emojis estratégicos (não excessivos)
- Visual: Tema escuro, identidade agressiva (vermelho-laranja + teal)
- Disclaimer: Incluir aviso de jogo responsável quando falar de apostas reais

TIPOS DE CONTEÚDO:
1. Análise de estratégia (ROI, gestão de banca)
2. Dicas de mercados específicos (Ambas marcam, Over/Under, Handicap)
3. Educacional (como funcionam as odds, como ler estatísticas)
4. Resultados e análise de performance
5. Notícias do mercado de esoccer
6. Motivacional / Mindset de apostador

REGRAS:
- Nunca prometer lucro garantido
- Sempre mencionar responsabilidade nas apostas quando falar de apostas reais
- Usar linguagem do nicho: banca, odd, EV+, value bet, lay, back
- Hashtags sempre em português + inglês
- CTAs claros e persuasivos"""


def generate_post(topic: str = None, post_type: str = "estrategia") -> dict:
    types = {
        "estrategia": "Uma dica ou estratégia de apostas em esoccer",
        "educacional": "Conteúdo educacional sobre apostas esportivas ou esoccer",
        "analise": "Análise de mercado ou odds em esoccer",
        "motivacional": "Conteúdo motivacional para apostadores",
        "noticias": "Notícia ou update do mercado de esoccer",
        "carrossel": "Script para carrossel (5-7 slides) sobre esoccer betting",
    }

    topic_instruction = f"Tópico específico: {topic}" if topic else f"Crie sobre: {types.get(post_type, types['estrategia'])}"

    prompt = f"""Crie um post completo para Instagram de apostas em esoccer.

{topic_instruction}

Retorne APENAS um JSON válido com esta estrutura:
{{
  "type": "{post_type}",
  "caption": "legenda completa do post com emojis e quebras de linha (máx 2200 chars)",
  "hashtags": ["lista", "de", "hashtags", "sem", "o", "simbolo"],
  "hook": "primeira linha chamativa para parar o scroll",
  "cta": "chamada para ação",
  "best_time": "horário sugerido para postar (ex: 19:00)",
  "notes": "observações para criação da imagem/arte"
}}"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    data = json.loads(text)
    data["generated_at"] = datetime.now().isoformat()
    data["topic"] = topic or post_type
    return data


def generate_carousel_script(topic: str) -> dict:
    prompt = f"""Crie um roteiro completo de carrossel para Instagram sobre: {topic}

O carrossel é sobre apostas em esoccer (FIFA/EA FC) para apostadores brasileiros.

Retorne APENAS um JSON válido:
{{
  "title": "título do carrossel",
  "slides": [
    {{
      "slide_number": 1,
      "type": "capa",
      "headline": "título principal chamativo",
      "subtext": "subtítulo ou complemento",
      "visual_notes": "instruções visuais para o designer"
    }},
    {{
      "slide_number": 2,
      "type": "conteudo",
      "headline": "título do slide",
      "body": "texto do slide (máx 150 chars)",
      "visual_notes": "instruções visuais"
    }}
  ],
  "caption": "legenda completa para o post",
  "hashtags": ["lista", "de", "hashtags"],
  "cta": "chamada para ação",
  "notes": "observações gerais"
}}

Crie entre 6 e 8 slides. O último slide deve ser de CTA."""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    data = json.loads(text)
    data["generated_at"] = datetime.now().isoformat()
    data["topic"] = topic
    return data


def generate_weekly_plan() -> dict:
    prompt = """Crie um plano de conteúdo semanal para um perfil de Instagram de apostas em esoccer.

Frequência: 2 posts por dia (manhã ~9h e noite ~19h) + stories
Dias: Segunda a Domingo (14 posts + stories diários)

Retorne APENAS um JSON válido:
{
  "week_theme": "tema da semana",
  "days": {
    "segunda": {
      "morning": {"type": "tipo do post", "topic": "tópico", "format": "imagem|carrossel|reels"},
      "evening": {"type": "tipo do post", "topic": "tópico", "format": "imagem|carrossel|reels"},
      "stories": ["ideia 1", "ideia 2"]
    },
    "terca": { ... },
    "quarta": { ... },
    "quinta": { ... },
    "sexta": { ... },
    "sabado": { ... },
    "domingo": { ... }
  },
  "hashtag_sets": {
    "principal": ["hashtags para posts principais"],
    "educacional": ["hashtags para posts educacionais"],
    "estrategia": ["hashtags para dicas e estratégias"]
  }
}"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    data = json.loads(text)
    data["generated_at"] = datetime.now().isoformat()
    return data
