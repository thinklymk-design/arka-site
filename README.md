# arka-site

Le site vitrine [arkawatch.com](https://arkawatch.com) : une page HTML statique, sans build
ni dépendance, servie par un conteneur `nginx` derrière un Traefik existant.

```
public/index.html          la page — seul dossier servi
deploy/docker-compose.yml  le conteneur (lecture seule, 64 Mo, aucun port publié)
deploy/.env.example        ARKA_DOMAIN=<domaine>
```

Aperçu local : `open public/index.html`.

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
