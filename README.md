# arka-site

Le site vitrine [arkawatch.com](https://arkawatch.com) : une page HTML statique, sans build
(design « Constellation » : un champ de points à explorer, polices Google Fonts),
en français, allemand et anglais, servie par un conteneur `nginx` derrière un Traefik existant.

```
src/index.html             le gabarit de la page (repères {{section.cle}} à la place des textes)
src/i18n/fr.json de.json en.json   tous les textes, une langue par fichier
src/static/                icônes, image de partage, robots.txt, manifeste — copiés dans public/
build.py                   génère public/ (pages, copie de src/static/, sitemap.xml)
public/                    les pages générées (/, /de/, /en/) — seul dossier servi, ne pas éditer
deploy/docker-compose.yml  le conteneur (lecture seule, 64 Mo, aucun port publié)
deploy/.env.example        ARKA_DOMAIN=<domaine>
archive/v1/index.html      la version précédente (hors ligne, gardée pour mémoire)
```

## Modifier le site

1. Un texte : le changer dans **les trois** fichiers `src/i18n/*.json` (mêmes clés partout,
   `build.py` refuse sinon). La mise en page ou le script : `src/index.html`.
2. `python3 build.py` (Python 3, aucune dépendance), puis vérifier `public/`.
3. Committer `src/` **et** `public/`, pousser.

Aperçu local : `python3 -m http.server 5500 --directory public`, puis http://localhost:5500.

## Langues

Pas de sélecteur. L'adresse d'entrée `/` suit la langue du navigateur (français, allemand,
sinon anglais) et redirige vers `/de/` ou `/en/` au besoin ; une adresse de langue (`/de/`,
`/en/`) est toujours respectée. `?lang=fr|de|en` force une langue et la mémorise. Les robots
ne sont jamais redirigés ; les balises `hreflang` relient les trois versions.

## Référencement

Chaque page déclare son icône (`favicon.ico` 16–48 px, `favicon.svg`, `apple-touch-icon.png`),
son image de partage (`og-image.png`, 1200×630) et des données structurées schema.org
(`Organization` et `WebSite`, nom « ARKA », autre nom « Arkawatch »). `robots.txt` pointe vers
`sitemap.xml`, régénéré à chaque `build.py`. Les icônes viennent de `brand/svg/arka-icon-flat.svg`
et `arka-lockup-horizontal-notagline.svg` du dépôt ARKA.

## Mettre en ligne (une fois)

Prérequis : un enregistrement DNS A pour le domaine **et** pour `www` vers le serveur, et
un Traefik sur le réseau Docker `public_network` avec le résolveur `mytlschallenge`.

```sh
git clone --depth 1 https://github.com/thinklymk-design/arka-site.git /opt/arka-site-src
cd /opt/arka-site-src/deploy && echo 'ARKA_DOMAIN=<domaine>' > .env && docker compose up -d
```

## Mettre à jour

```sh
cd /opt/arka-site-src && git pull
```

Pas de redémarrage : le conteneur monte le dossier `public/` en entier et voit le nouveau
fichier tout de suite.

## Retirer ou déplacer

- **Retirer** : `docker compose down` dans `/opt/arka-site-src/deploy`, puis supprimer le dossier.
- **Changer de serveur** : refaire « Mettre en ligne » sur le nouveau, puis pointer le DNS.
- **Changer de propriétaire GitHub** (transfert du dépôt) : GitHub redirige l'ancienne
  adresse ; pour la mettre à jour sur le serveur,
  `git -C /opt/arka-site-src remote set-url origin https://github.com/<nouveau>/arka-site.git`.

Les notes de conception (jetons, règles du rouge, périmètre) restent dans le dépôt
privé du projet, `site/README.md`.
