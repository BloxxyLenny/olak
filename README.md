# 0łak — dokumentacja

## Odpalenie
Strona czyta pliki przez `fetch`, więc **nie działa z `file://`**. Lokalnie:
`python3 -m http.server 8000` w folderze strony → http://localhost:8000
(Na hostingu statycznym — GitHub Pages / Netlify / Cloudflare Pages — działa od ręki.)

## Dodawanie utworu
1. Utwórz folder `songs/<slug>/` (slug = nazwa folderu, trafia też do linku `#slug`).
2. Wrzuć pliki (wszystkie poza `config.json` są opcjonalne):

| Plik | Opis |
|---|---|
| `config.json` | **wymagany**, dane utworu (niżej) |
| `cover.png` / `cover.jpg` | okładka, PNG ma priorytet |
| `lyrics.txt` | tekst; linie w `[nawiasach]` są wyświetlane jako nagłówki sekcji |
| `song.mp3` | wersja low quality |
| `song.flac` | wersja hi quality |
| `intro.flac` / `intro.mp3` | instrumental; FLAC ma priorytet, **jakość z góry strony go nie dotyczy** |

3. Dopisz folder do `songs/index.json` (`["winda","nowy-utwor"]`) **albo** odpal `python3 tools/update-index.py`, który zrobi to sam (przeskanuje foldery z `config.json`).

## config.json
```json
{
  "title": "winda",
  "year": 2026,
  "order": 1,
  "artist": "0łak",
  "features": ["ktoś", "ktoś inny"]
}
```
- `title` — tytuł, `year` — rok wydania
- `order` — kolejność na liście: **wyższa liczba = wyżej**, niższa = niżej
- `artist` — wykonawca główny (jaśniejszy szary)
- `features` — wykonawcy poboczni, tablica (ciemniejszy szary, po „feat.”); może być `[]`

## Zachowanie
- Przełącznik jakości (góra strony) zapisuje się w `localStorage` (`olak.quality`). Jeśli wybranej wersji brak, strona bierze drugą.
- Brak instrumentala → przycisk INSTRUMENTAL jest wyszarzony i opisany jako niedostępny.
- Waveform liczony jest w przeglądarce z pliku audio (dla utworu z `song.mp3`, jeśli jest) — nic nie trzeba generować.
- Skróty w oknie utworu: `Spacja` play/pauza, `←/→` ±5 s, `Esc` zamknij. Zamknięcie okna nie zatrzymuje muzyki (mini-player na dole).
- Nazwy plików instrumentala (`intro.*`) i okładek zmienisz w funkcji `init()` w `index.html`.


## SEO i indeksowanie

Strona zawiera tytuł i opis SEO, metadane Open Graph/Twitter, dane strukturalne JSON-LD, semantyczny nagłówek H1, opisy alternatywne okładek oraz linki do indeksowalnych podstron utworów.

Po dodaniu lub zmianie utworu uruchom:

```bash
python3 tools/update-index.py
python3 tools/generate-seo.py
```

To wygeneruje `songs/<slug>/index.html` dla każdego utworu z `songs/index.json`. Każda podstrona zawiera własny tytuł i opis, dane MusicRecording, okładkę, odtwarzacz oraz tekst utworu, jeśli plik `lyrics.txt` istnieje.

**Po opublikowaniu strony** uruchom generator z prawdziwym adresem witryny (bez końcowego ukośnika), aby ustawić kanoniczne adresy URL, bezwzględne adresy podglądów social media, `sitemap.xml` i wpis Sitemap w `robots.txt`:

```bash
python3 tools/generate-seo.py --base-url https://twoja-domena.pl
```

Nie uruchamiaj polecenia z przykładową domeną. Prawidłowy adres domeny jest niezbędny do poprawnego canonical i sitemap. Następnie dodaj domenę do Google Search Console i zgłoś `https://twoja-domena.pl/sitemap.xml`. Samo dodanie metadanych nie gwarantuje indeksacji ani konkretnej pozycji w wynikach.
