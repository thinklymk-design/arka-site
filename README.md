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
deploy/docker-compose.yml  les conteneurs (lecture seule, aucun port publié)
deploy/signup/app.py       la liste d'attente : POST /api/inscription → /opt/arka-data/inscriptions.csv
deploy/.env.example        ARKA_DOMAIN=<domaine>
archive/v1/index.html      la version précédente (hors ligne, gardée pour mémoire)
```

## Modifier le site

1. Un texte : le changer dans **les trois** fichiers `src/i18n/*.json` (mêmes clés partout,
   `build.py` refuse sinon). La mise en page ou le script : `src/index.html`.
2. `python3 build.py` (Python 3, aucune dépendance), puis vérifier `public/`.
3. Committer `src/` **et** `public/`, pousser.

Aperçu local : `python3 -m http.server 5500 --directory public`, puis http://localhost:5500.

## Mobile

Sous 760 px de large, la page affiche `#mob` (maquette « L'application des collectionneurs
de montres ») : un seul écran à 7 étapes (intro où les points dessinent le logo, flèches,
glissement du doigt), une vue « Maisons » propre au mobile (`#maisons`) et une feuille
« Être prévenu ». La scène du bureau (`#stage`) y est masquée et ne dessine rien. Textes dans
la section `mobile` des JSON ; la vue Maisons reprend ceux de `partners`. L'inscription ouvre
pour l'instant un e-mail prérempli (HubSpot à brancher).

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

## Liste d'attente

Les boutons « S'inscrire » (bureau) et « Me prévenir » (mobile) envoient l'adresse en
arrière-plan à `POST /api/inscription` : rien ne s'ouvre chez le visiteur, qui voit « Merci,
c'est noté ». Le conteneur `arka-signup` (Python, bibliothèque standard seulement, 32 Mo,
utilisateur sans droits) ajoute une ligne `date,email,langue` à `/opt/arka-data/inscriptions.csv`,
hors du dépôt. Doublons ignorés ; 5 envois par heure et par visiteur, 1000 par jour au total ;
aucune adresse dans les journaux. Si le service ne répond pas, la page retombe sur l'e-mail
(`mailto:`), comme avant. Les questions passent toujours par l'e-mail.

Mise en route (une fois) :

```sh
mkdir -p /opt/arka-data && chown 65534:65534 /opt/arka-data && chmod 700 /opt/arka-data
cd /opt/arka-site-src/deploy && docker compose up -d arka-signup
```

Lire la liste : `cat /opt/arka-data/inscriptions.csv` (le fichier s'importe tel quel dans HubSpot).
Après un changement de `app.py` : `docker restart arka-signup`.

## Retirer ou déplacer

- **Retirer** : `docker compose down` dans `/opt/arka-site-src/deploy`, puis supprimer le dossier
  (et `/opt/arka-data` une fois la liste récupérée).
- **Changer de serveur** : refaire « Mettre en ligne » sur le nouveau, puis pointer le DNS.
- **Changer de propriétaire GitHub** (transfert du dépôt) : GitHub redirige l'ancienne
  adresse ; pour la mettre à jour sur le serveur,
  `git -C /opt/arka-site-src remote set-url origin https://github.com/<nouveau>/arka-site.git`.

Les notes de conception (jetons, règles du rouge, périmètre) restent dans le dépôt
privé du projet, `site/README.md`.
