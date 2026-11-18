#!/usr/bin/env python3
# Skanuje songs/ i generuje songs/index.json (foldery zawierające config.json).
import json, pathlib
r = pathlib.Path(__file__).resolve().parent.parent / "songs"
n = sorted(p.name for p in r.iterdir() if (p / "config.json").is_file())
(r / "index.json").write_text(json.dumps(n, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("index.json:", n)
