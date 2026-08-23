#!/usr/bin/env python3
"""
Script de configuração e teste de autenticação do Instagram Graph API.
Rode este script para testar sua conexão e salvar as credenciais no .env
"""
import os
import json
import sys
import requests
from pathlib import Path

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

GRAPH = "https://graph.facebook.com/v21.0"


def print_step(n, title):
    print(f"\n{BOLD}{CYAN}[Passo {n}]{RESET} {BOLD}{title}{RESET}")
    print("─" * 50)


def ok(msg):   print(f"{GREEN}✓ {msg}{RESET}")
def warn(msg): print(f"{YELLOW}⚠ {msg}{RESET}")
def err(msg):  print(f"{RED}✗ {msg}{RESET}")
def info(msg): print(f"  {CYAN}→{RESET} {msg}")


def update_env(key: str, value: str):
    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("")
    content = env_path.read_text()
    if f"{key}=" in content:
        lines = []
        for line in content.splitlines():
            if line.startswith(f"{key}="):
                lines.append(f"{key}={value}")
            else:
                lines.append(line)
        env_path.write_text("\n".join(lines) + "\n")
    else:
        with open(env_path, "a") as f:
            f.write(f"\n{key}={value}\n")


def get_pages(user_token: str) -> list[dict]:
    r = requests.get(f"{GRAPH}/me/accounts", params={
        "access_token": user_token,
        "fields": "id,name,access_token,instagram_business_account"
    })
    r.raise_for_status()
    return r.json().get("data", [])


def get_ig_account(page_token: str, page_id: str) -> dict | None:
    r = requests.get(f"{GRAPH}/{page_id}", params={
        "access_token": page_token,
        "fields": "instagram_business_account"
    })
    r.raise_for_status()
    data = r.json()
    return data.get("instagram_business_account")


def get_ig_profile(ig_id: str, page_token: str) -> dict:
    r = requests.get(f"{GRAPH}/{ig_id}", params={
        "access_token": page_token,
        "fields": "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,website"
    })
    r.raise_for_status()
    return r.json()


def get_recent_posts(ig_id: str, page_token: str, limit: int = 6) -> list[dict]:
    r = requests.get(f"{GRAPH}/{ig_id}/media", params={
        "access_token": page_token,
        "fields": "id,caption,media_type,timestamp,like_count,comments_count,media_url,permalink",
        "limit": limit
    })
    r.raise_for_status()
    return r.json().get("data", [])


def exchange_long_lived_token(short_token: str, app_id: str, app_secret: str) -> str:
    r = requests.get(f"{GRAPH}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    })
    r.raise_for_status()
    return r.json()["access_token"]


def main():
    print(f"""
{BOLD}{GREEN}╔══════════════════════════════════════════╗
║   DARKDALE — Configuração Instagram API  ║
╚══════════════════════════════════════════╝{RESET}
""")

    # ─── PASSO 1: User Token ───────────────────────────────
    print_step(1, "Token de Acesso do Meta")
    print(f"""
{YELLOW}Como obter seu token:{RESET}

  1. Acesse: {CYAN}https://developers.facebook.com/tools/explorer{RESET}
  2. No canto superior direito, selecione seu App
     (Se não tiver um app: developers.facebook.com → Criar App → Outro → Consumidor)
  3. Clique em {BOLD}"Gerar Token de Acesso"{RESET}
  4. Marque as permissões:
     {GREEN}✓{RESET} pages_show_list
     {GREEN}✓{RESET} pages_read_engagement
     {GREEN}✓{RESET} instagram_basic
     {GREEN}✓{RESET} instagram_content_publish
  5. Autorize e copie o token gerado
""")

    user_token = input(f"{BOLD}Cole seu User Access Token aqui: {RESET}").strip()
    if not user_token:
        err("Token não informado. Abortando.")
        sys.exit(1)

    # ─── PASSO 2: Listar páginas ───────────────────────────
    print_step(2, "Detectando suas Facebook Pages")
    try:
        pages = get_pages(user_token)
    except Exception as e:
        err(f"Token inválido ou sem permissão: {e}")
        sys.exit(1)

    if not pages:
        err("Nenhuma Facebook Page encontrada nessa conta.")
        warn("Você precisa criar uma página em: facebook.com/pages/create")
        warn("Depois vincule ao Instagram: Configurações do Instagram → Conta vinculada → Facebook")
        sys.exit(1)

    print(f"\nEncontradas {len(pages)} página(s):\n")
    for i, page in enumerate(pages):
        has_ig = "instagram_business_account" in page
        ig_marker = f"{GREEN}[tem Instagram vinculado]{RESET}" if has_ig else f"{YELLOW}[sem Instagram vinculado]{RESET}"
        print(f"  [{i}] {page['name']} (ID: {page['id']}) {ig_marker}")

    if len(pages) == 1:
        chosen = 0
    else:
        chosen = int(input(f"\n{BOLD}Qual página usar? (número): {RESET}").strip())

    page = pages[chosen]
    page_token = page["access_token"]
    page_id = page["id"]
    ok(f"Página selecionada: {page['name']}")

    # ─── PASSO 3: Instagram Business Account ──────────────
    print_step(3, "Conectando conta Instagram Business")
    ig_data = page.get("instagram_business_account")
    if not ig_data:
        err("Esta página não tem uma conta Instagram Business vinculada.")
        print(f"""
{YELLOW}Para vincular:{RESET}
  1. Abra seu Instagram
  2. Configurações → Conta → Mudar para conta profissional
  3. Escolha: Criador ou Empresa
  4. Selecione a página do Facebook que você acabou de escolher
  5. Rode este script novamente
""")
        sys.exit(1)

    ig_id = ig_data["id"]
    ok(f"Instagram Business Account ID: {ig_id}")

    # ─── PASSO 4: Perfil ──────────────────────────────────
    print_step(4, "Buscando dados do perfil")
    try:
        profile = get_ig_profile(ig_id, page_token)
    except Exception as e:
        err(f"Erro ao buscar perfil: {e}")
        sys.exit(1)

    username = profile.get("username", "?")
    followers = profile.get("followers_count", 0)
    posts = profile.get("media_count", 0)
    bio = profile.get("biography", "")

    print(f"""
{GREEN}@{username}{RESET}
  Seguidores: {BOLD}{followers:,}{RESET}
  Posts:      {BOLD}{posts}{RESET}
  Bio:        {bio[:80] if bio else '(sem bio)'}
""")

    # ─── PASSO 5: Posts recentes ──────────────────────────
    print_step(5, "Analisando posts recentes")
    try:
        recent = get_recent_posts(ig_id, page_token)
        if recent:
            print(f"Últimos {len(recent)} posts:\n")
            for post in recent:
                tipo = post.get("media_type", "?")
                likes = post.get("like_count", 0)
                comments = post.get("comments_count", 0)
                caption = (post.get("caption") or "")[:60]
                ts = post.get("timestamp", "")[:10]
                print(f"  [{ts}] {tipo:10} ❤ {likes:4}  💬 {comments:3}  — {caption}...")
        else:
            warn("Nenhum post encontrado.")
    except Exception as e:
        warn(f"Não foi possível buscar posts: {e}")

    # ─── PASSO 6: App credentials para long-lived token ───
    print_step(6, "Token de longa duração (opcional mas recomendado)")
    print(f"""
{YELLOW}Tokens gerados no Graph Explorer expiram em ~1h.{RESET}
Para usar o sistema por mais tempo, precisamos de um token permanente.

Você precisa do App ID e App Secret do seu Meta App:
  1. developers.facebook.com → Seu App → Configurações → Básico
  2. Copie o "ID do Aplicativo" e o "Chave Secreta do Aplicativo"

(Pressione Enter para pular esta etapa por agora)
""")

    app_id = input(f"App ID (ou Enter para pular): ").strip()
    app_secret = input(f"App Secret (ou Enter para pular): ").strip()

    long_token = page_token
    if app_id and app_secret:
        try:
            long_token = exchange_long_lived_token(user_token, app_id, app_secret)
            ok("Token de longa duração gerado com sucesso!")
            update_env("META_APP_ID", app_id)
            update_env("META_APP_SECRET", app_secret)
        except Exception as e:
            warn(f"Não foi possível gerar token longo: {e}")
            warn("Usando token de curta duração.")

    # ─── PASSO 7: Salvar no .env ──────────────────────────
    print_step(7, "Salvando configurações no .env")
    update_env("META_ACCESS_TOKEN", long_token)
    update_env("FACEBOOK_PAGE_ID", page_id)
    update_env("INSTAGRAM_BUSINESS_ACCOUNT_ID", ig_id)
    update_env("INSTAGRAM_USERNAME", username)

    ok("META_ACCESS_TOKEN salvo")
    ok("FACEBOOK_PAGE_ID salvo")
    ok(f"INSTAGRAM_BUSINESS_ACCOUNT_ID salvo")
    ok(f"INSTAGRAM_USERNAME salvo (@{username})")

    # ─── RESULTADO FINAL ──────────────────────────────────
    print(f"""
{BOLD}{GREEN}╔══════════════════════════════════════════╗
║   Conexão configurada com sucesso!       ║
╚══════════════════════════════════════════╝{RESET}

  Instagram: {GREEN}@{username}{RESET}
  Seguidores: {BOLD}{followers:,}{RESET}
  Posts: {BOLD}{posts}{RESET}

{BOLD}Próximos passos:{RESET}
  1. Adicione sua ANTHROPIC_API_KEY no .env
  2. Gere seu primeiro post:
     {CYAN}python main.py generate --type estrategia{RESET}
  3. Gere o plano semanal:
     {CYAN}python main.py plan{RESET}
  4. Gere um carrossel:
     {CYAN}python main.py carousel "gestão de banca no esoccer"{RESET}
""")

    # Salvar análise do perfil em arquivo
    analysis = {
        "profile": profile,
        "recent_posts": recent if 'recent' in dir() else [],
        "page_id": page_id,
        "ig_account_id": ig_id,
    }
    Path("posts").mkdir(exist_ok=True)
    Path("posts/profile_analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2)
    )
    ok("Análise do perfil salva em posts/profile_analysis.json")


if __name__ == "__main__":
    main()
