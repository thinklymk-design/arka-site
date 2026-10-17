#!/usr/bin/env python3
"""Génère public/ (fr), public/de/ et public/en/ à partir de src/index.html et src/i18n/*.json.

    python3 build.py

Le gabarit contient des repères :
  {{section.cle}}      texte échappé pour le HTML
  {{url:section.cle}}  texte encodé pour une URL (objet d'un mailto)
  {{js}}               la section « js » du JSON, pour le script de la page
  {{lang}} {{pageUrl}} {{hreflang}}
Aucune dépendance : bibliothèque standard de Python uniquement.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = 'https://arkawatch.com'
LANGS = {'fr': '', 'de': 'de/', 'en': 'en/'}  # langue -> sous-dossier de public/
DEFAULT = 'fr'


def flatten(d, prefix=''):
    out = {}
    for k, v in d.items():
        key = f'{prefix}{k}'
        if isinstance(v, dict):
            out.update(flatten(v, key + '.'))
        else:
            out[key] = v
    return out


def keys_of(d, prefix=''):
    out = set()
    for k, v in d.items():
        out.add(prefix + k)
        if isinstance(v, dict):
            out |= keys_of(v, prefix + k + '.')
    return out


def main():
    template = (ROOT / 'src/index.html').read_text()
    data = {lang: json.loads((ROOT / f'src/i18n/{lang}.json').read_text()) for lang in LANGS}

    # Les trois langues doivent avoir exactement les mêmes clés.
    ref = keys_of(data[DEFAULT])
    for lang, d in data.items():
        missing, extra = ref - keys_of(d), keys_of(d) - ref
        if missing or extra:
            sys.exit(f'{lang}.json : clés manquantes {sorted(missing)}, en trop {sorted(extra)}')

    hreflang = '\n'.join(
        [f'<link rel="alternate" hreflang="{l}" href="{SITE}/{p}">' for l, p in LANGS.items()]
        + [f'<link rel="alternate" hreflang="x-default" href="{SITE}/{LANGS[DEFAULT]}">']
    )

    for lang, sub in LANGS.items():
        flat = flatten(data[lang])
        page_url = f'{SITE}/{sub}'

        def fill(m):
            token = m.group(1)
            if token == 'lang':
                return lang
            if token == 'pageUrl':
                return page_url
            if token == 'hreflang':
                return hreflang
            if token == 'js':
                return json.dumps(data[lang]['js'], ensure_ascii=False).replace('</', '<\\/')
            if token.startswith('url:'):
                return quote(flat[token[4:]], safe='')
            if token not in flat:
                sys.exit(f'Repère inconnu dans src/index.html : {{{{{token}}}}}')
            return html.escape(flat[token], quote=True)

        page = re.sub(r'\{\{([^{}]+)\}\}', fill, template)
        out = ROOT / 'public' / sub / 'index.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page)
        print(f'{lang}: public/{sub}index.html')


if __name__ == '__main__':
    main()
