#!/usr/bin/env python3
"""Generate crawlable song landing pages and, when given a public URL, a sitemap."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SONGS = ROOT / "songs"
INDEX = ROOT / "index.html"
ROBOTS = ROOT / "robots.txt"
SITEMAP = ROOT / "sitemap.xml"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Oczekiwano obiektu JSON: {path}")
    return value


def slug_list() -> list[str]:
    path = SONGS / "index.json"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("songs/index.json musi zawierać tablicę slugów.")
    return [str(item) for item in data if (SONGS / str(item) / "config.json").is_file()]


def song_page(slug: str, cfg: dict) -> str:
    title = str(cfg.get("title") or slug)
    artist = str(cfg.get("artist") or "0łak")
    year = str(cfg.get("year") or "")
    features = cfg.get("features") or []
    artist_line = artist + ((" feat. " + ", ".join(map(str, features))) if features else "")
    description = f"Posłuchaj utworu „{title}” — {artist_line}. Polski rap z Oławy. Odtwarzaj online i sprawdź tekst utworu."
    folder = SONGS / slug
    cover = "cover.png" if (folder / "cover.png").is_file() else ("cover.jpg" if (folder / "cover.jpg").is_file() else None)
    audio = "song.mp3" if (folder / "song.mp3").is_file() else ("song.flac" if (folder / "song.flac").is_file() else None)
    audio_links = []
    for filename, label in (("song.mp3", "MP3"), ("song.flac", "FLAC")):
        if (folder / filename).is_file():
            audio_links.append(f'<a href="{filename}" download>Pobierz {label}</a>')
    lyrics_path = folder / "lyrics.txt"
    lyrics = lyrics_path.read_text(encoding="utf-8-sig") if lyrics_path.is_file() else ""
    lyrics_html = (
        f'<section class="lyrics" aria-labelledby="lyrics-heading"><h2 id="lyrics-heading">Tekst utworu „{esc(title)}”</h2><pre>{esc(lyrics)}</pre></section>'
        if lyrics.strip() else ""
    )
    cover_html = (
        f'<img class="cover" src="{esc(cover)}" alt="Okładka utworu {esc(title)} — {esc(artist)}" decoding="async">'
        if cover else ""
    )
    audio_html = (
        f'<audio controls preload="none" src="{esc(audio)}">Twoja przeglądarka nie obsługuje odtwarzania audio.</audio>'
        if audio else '<p>Plik audio nie jest obecnie dostępny.</p>'
    )
    links_html = " · ".join(audio_links)
    schema = {
        "@context": "https://schema.org",
        "@type": "MusicRecording",
        "name": title,
        "byArtist": {"@type": "Person", "name": artist},
        "datePublished": year if year else None,
        "genre": ["Rap", "Hip-hop"],
        "inLanguage": "pl",
        "description": description,
    }
    schema = {key: value for key, value in schema.items() if value is not None}
    schema_json = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")

    return f'''<!doctype html>
<html lang="pl-PL">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} — {esc(artist)} | Polski rap z Oławy</title>
  <meta name="description" content="{esc(description)}">
  <meta name="author" content="{esc(artist)}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <meta name="theme-color" content="#000000">
  <link rel="icon" type="image/png" href="../../assets/ol.png">
  <!-- SEO_CANONICAL -->
  <meta property="og:type" content="music.song">
  <meta property="og:locale" content="pl_PL">
  <meta property="og:site_name" content="0łak">
  <meta property="og:title" content="{esc(title)} — {esc(artist)} | Polski rap z Oławy">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="__SEO_OG_IMAGE__">
  <meta property="og:image:alt" content="Okładka utworu {esc(title)} — {esc(artist)}">
  <!-- SEO_OG_URL -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)} — {esc(artist)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="__SEO_OG_IMAGE__">
  <script type="application/ld+json">{schema_json}</script>
  <style>
    :root {{ color-scheme: dark; --muted: #888; --line: #292929; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: #000; color: #f2f2f2; font: 15px/1.7 'JetBrains Mono', ui-monospace, Consolas, monospace; }}
    main {{ width: min(900px, calc(100% - 36px)); margin: 0 auto; padding: 36px 0 80px; }}
    a {{ color: inherit; }}
    .back {{ display: inline-block; margin-bottom: 34px; color: var(--muted); font-size: 12px; text-decoration: none; }}
    .back:hover {{ color: #fff; }}
    .track {{ display: grid; grid-template-columns: minmax(180px, 320px) 1fr; gap: 34px; align-items: center; }}
    .cover {{ display: block; width: 100%; height: auto; border: 1px solid var(--line); }}
    .eyebrow {{ color: var(--muted); font-size: 11px; letter-spacing: .22em; text-transform: uppercase; }}
    h1 {{ margin: 8px 0; font-size: clamp(34px, 7vw, 64px); line-height: 1.05; }}
    .artist {{ color: #aaa; }}
    .year {{ color: var(--muted); font-size: 12px; }}
    audio {{ width: 100%; margin-top: 24px; }}
    .downloads {{ margin-top: 12px; font-size: 12px; color: var(--muted); }}
    .lyrics {{ margin-top: 46px; border-top: 1px solid var(--line); padding-top: 22px; }}
    h2 {{ font-size: 13px; letter-spacing: .15em; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; font: inherit; color: #ccc; }}
    @media (max-width: 640px) {{ .track {{ grid-template-columns: 1fr; }} .cover {{ max-width: 420px; }} }}
  </style>
</head>
<body>
  <main>
    <a class="back" href="../../">← 0łak / strona główna</a>
    <article>
      <div class="track">
        {cover_html}
        <div>
          <p class="eyebrow">Polski rap · Oława</p>
          <h1>{esc(title)}</h1>
          <p class="artist">{esc(artist_line)}</p>
          {f'<p class="year">{esc(year)}</p>' if year else ''}
          {audio_html}
          <p class="downloads">{links_html}</p>
        </div>
      </div>
      {lyrics_html}
    </article>
  </main>
</body>
</html>
'''


def inject_absolute_urls(base_url: str, page_path: str, image_path: str, html_text: str) -> str:
    full_page = f"{base_url}/{page_path}" if page_path else f"{base_url}/"
    full_image = f"{base_url}/{image_path.lstrip('/')}"
    canonical = f'<link rel="canonical" href="{esc(full_page)}">'
    og_url = f'<meta property="og:url" content="{esc(full_page)}">'
    html_text = re.sub(r'\s*<link rel="canonical" href="[^"]*">', "", html_text)
    html_text = re.sub(r'\s*<meta property="og:url" content="[^"]*">', "", html_text)
    if "<!-- SEO_CANONICAL -->" in html_text:
        html_text = html_text.replace("<!-- SEO_CANONICAL -->", canonical + "\n  " + og_url)
    else:
        html_text = html_text.replace("</head>", "  " + canonical + "\n  " + og_url + "\n</head>")
    html_text = re.sub(r'(<meta (?:property="og:image"|name="twitter:image") content=")[^"]*(")', lambda match: match.group(1) + esc(full_image) + match.group(2), html_text)
    return html_text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="Public site URL, e.g. https://example.pl (needed for canonical URLs and sitemap)")
    args = parser.parse_args()
    base_url = None
    if args.base_url:
        base_url = args.base_url.rstrip("/")
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
            parser.error("--base-url musi być pełnym adresem http(s), bez query i fragmentu.")

    slugs = slug_list()
    urls: list[str] = []
    for slug in slugs:
        cfg = read_json(SONGS / slug / "config.json")
        folder = SONGS / slug
        page = song_page(slug, cfg)
        image = "cover.png" if (folder / "cover.png").is_file() else ("cover.jpg" if (folder / "cover.jpg").is_file() else "../../assets/ol.png")
        if base_url:
            page = inject_absolute_urls(base_url, f"songs/{slug}/", f"songs/{slug}/{image}", page)
            urls.append(f"{base_url}/songs/{slug}/")
        else:
            page = page.replace("__SEO_OG_IMAGE__", image)
        (folder / "index.html").write_text(page, encoding="utf-8")
        print(f"Utworzono: songs/{slug}/index.html")

    if base_url:
        root_html = INDEX.read_text(encoding="utf-8")
        default_image = None
        if slugs:
            first_slug = slugs[0]
            folder = SONGS / first_slug
            if (folder / "cover.png").is_file():
                default_image = f"songs/{first_slug}/cover.png"
            elif (folder / "cover.jpg").is_file():
                default_image = f"songs/{first_slug}/cover.jpg"
        if not default_image:
            default_image = "assets/ol.png"
        root_html = inject_absolute_urls(base_url, "", default_image, root_html)
        INDEX.write_text(root_html, encoding="utf-8")
        urls.insert(0, f"{base_url}/")
        entries = "\n".join(f"  <url><loc>{esc(url)}</loc></url>" for url in urls)
        sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
'''
        SITEMAP.write_text(sitemap, encoding="utf-8")
        ROBOTS.write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8")
        print(f"Utworzono sitemap.xml ({len(urls)} adresów) i zaktualizowano robots.txt")
    else:
        # Use relative social image URLs until the actual public domain is known.
        root_html = INDEX.read_text(encoding="utf-8")
        default_image = "assets/ol.png"
        if slugs:
            first_folder = SONGS / slugs[0]
            if (first_folder / "cover.png").is_file():
                default_image = f"songs/{slugs[0]}/cover.png"
            elif (first_folder / "cover.jpg").is_file():
                default_image = f"songs/{slugs[0]}/cover.jpg"
        root_html = root_html.replace("__SEO_OG_IMAGE__", default_image)
        INDEX.write_text(root_html, encoding="utf-8")
        # Do not invent a public domain; sitemap and canonical URLs need the real deployed URL.
        if not ROBOTS.exists():
            ROBOTS.write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
        print("Pominięto canonical i sitemap.xml: podaj --base-url po wdrożeniu strony.")


if __name__ == "__main__":
    main()
