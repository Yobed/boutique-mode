"""
catalog.py — Lecture du catalogue de la boutique pour la modélisation 3D par lot.

Source : table Supabase `articles` si NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_ANON_KEY sont
définies (environnement ou .env.local), sinon la collection de démonstration lib/mock-data.ts.
Sortie : liste de {id, nom, categorie, photos}. Lecture seule, clé anonyme publique uniquement.
"""

import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MOCK_DATA = os.path.join(ROOT, "lib", "mock-data.ts")
HTTP_TIMEOUT = 20
USER_AGENT = "elsi-3d-pipeline/1.0"


def _read_env_files():
    values = {}
    for name in (".env", ".env.local"):
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                match = re.match(r"\s*([A-Z0-9_]+)\s*=\s*\"?([^\"\r\n]*)\"?\s*$", line)
                if match:
                    values[match.group(1)] = match.group(2)
    return values


def _supabase_credentials():
    env = {**_read_env_files(), **os.environ}
    url, key = env.get("NEXT_PUBLIC_SUPABASE_URL", ""), env.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    return (url.rstrip("/"), key) if url.startswith("https://") and key else None


def _from_supabase(url, key):
    request = urllib.request.Request(
        f"{url}/rest/v1/articles?select=id,nom,categorie,photos&order=created_at.desc",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT) as response:
        rows = json.load(response)
    return [{"id": str(r["id"]), "nom": r.get("nom", ""), "categorie": r.get("categorie", ""),
             "photos": list(r.get("photos") or [])} for r in rows]


PHOTO_TOKEN = re.compile(r"P\('([^']+)'(?:\s*,\s*(\d+))?\)|'((?:https?://|/)[^']+)'")


def _unsplash(photo_id, exp):
    """Réplique le helper `P(id, exp)` de lib/mock-data.ts."""
    return f"https://images.unsplash.com/photo-{photo_id}?w=1600&auto=format&q=80" + (f"&exp={exp}" if exp else "")


def _photo_urls(block):
    return [_unsplash(m.group(1), m.group(2)) if m.group(1) else m.group(3) for m in PHOTO_TOKEN.finditer(block)]


def parse_mock_data(text):
    """Extrait les articles de lib/mock-data.ts (objets littéraux, un `id:` par article, doublons écartés)."""
    articles, seen = [], set()
    for chunk in re.split(r"(?m)^(?=\s*id:\s*')", text):
        id_match = re.match(r"\s*id:\s*'([^']+)'", chunk)
        photos_match = re.search(r"photos:\s*\[(.*?)\]", chunk, re.DOTALL)
        cat_match = re.search(r"categorie:\s*'([^']+)'", chunk)
        if not (id_match and photos_match and cat_match) or id_match.group(1) in seen:
            continue
        seen.add(id_match.group(1))
        name = re.search(r"nom:\s*(?:'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\")", chunk)
        articles.append({
            "id": id_match.group(1),
            "nom": (name.group(1) or name.group(2)) if name else "",
            "categorie": cat_match.group(1),
            "photos": _photo_urls(photos_match.group(1)),
            "has_model": bool(re.search(r"\bmodele_3d\s*:", chunk)),  # le site l'utilise déjà, il est prioritaire
        })
    return articles


def read_catalog():
    """Retourne (articles, source) où source vaut 'supabase' ou 'mock-data'."""
    credentials = _supabase_credentials()
    if credentials:
        try:
            articles = _from_supabase(*credentials)
            if articles:
                return articles, "supabase"
        except Exception as exc:  # réseau ou schéma : on retombe sur la démo, en le disant
            print(f"[catalogue] Supabase indisponible ({type(exc).__name__}), repli sur mock-data.ts")
    with open(MOCK_DATA, encoding="utf-8") as f:
        return parse_mock_data(f.read()), "mock-data"
