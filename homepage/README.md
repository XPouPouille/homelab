# Homepage — Homer Dashboard + Auto-Discovery

Self-hosted dashboard powered by [Homer](https://github.com/bastienwirtz/homer), with a companion **Homer Manager** service that:

- **Auto-discovers** Docker containers labelled with `homer.enable=true` or `traefik.enable=true`
- Provides a **web UI** to add/remove custom links manually
- Syncs changes directly into Homer's config (Homer reloads automatically)
- Routed via **Traefik** — Homer is the main landing page on the public domain

## Configuration du domaine

Copier `.env.example` en `.env` et renseigner le domaine :

```bash
cp .env.example .env
# Éditer .env et définir DOMAIN=votre-domaine.com
```

Le fichier `.env` est ignoré par git — ne jamais committer les vraies valeurs.

## Services

| Service | Accès direct | Via Traefik |
|---|---|---|
| Homer (page principale) | http://localhost:52000 | http://${DOMAIN} |
| Homer Manager | http://localhost:52001 | http://manager.${DOMAIN} |
| Traefik dashboard | http://localhost:8080 | http://traefik.${DOMAIN} |

## Quick Start

```bash
# Cloner le dépôt
git clone https://github.com/XPouPouille/homelab.git
cd homelab/homepage

# Configurer le domaine
cp .env.example .env
# Éditer .env : DOMAIN=monsite.ddns.net

# Démarrer tous les services
docker compose up -d

# Vérifier les logs
docker compose logs -f
```

Homer accessible sur **http://${DOMAIN}** (remplacer `${DOMAIN}` par la valeur dans `.env`).

## Auto-discovery

Ajouter ces labels à n'importe quel container pour qu'il apparaisse sur le dashboard :

```yaml
labels:
  - "homer.enable=true"
  - "homer.name=Mon App"
  - "homer.subtitle=Courte description"
  - "homer.url=http://mon-app.mondomaine.fr"
  - "homer.logo=https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/mon-app.png"
  - "homer.tag=web"
  - "homer.group=Mon Groupe"    # optionnel, défaut: Auto-Discovered
```

Si le container a déjà `traefik.enable=true` avec une règle `Host(...)`, l'URL est extraite automatiquement.

Homer Manager synchronise toutes les **60 secondes**. Bouton **Sync Now** pour forcer.

## Gestion manuelle des liens

Ouvrir le Manager sur http://manager.${DOMAIN}, onglet **Custom Links**, bouton **Add Link**.
Les liens sont sauvegardés dans `homer-manager/data/custom_links.json` et écrits dans `config/config.yml`.

## Structure des fichiers

```
homepage/
├── .env.example              # Template variables d'environnement (commité)
├── .env                      # Valeurs réelles — IGNORÉ par git (ne pas committer)
├── docker-compose.yml        # Tous les services
├── traefik/
│   └── traefik.yml           # Config statique Traefik
├── config/
│   └── config.yml            # Config Homer (mise à jour auto par homer-manager)
└── homer-manager/
    ├── Dockerfile
    ├── app.py                # API Flask + découverte Docker
    ├── requirements.txt
    ├── data/                 # custom_links.json (créé automatiquement, ignoré par git)
    └── templates/
        └── index.html        # Interface de gestion
```

## Ajouter un service statique

Éditer `config/config.yml` sous le groupe `services` concerné :

```yaml
- name: "Mon App"
  logo: "https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/mon-app.png"
  subtitle: "Description"
  tag: "app"
  url: "http://mon-app.mondomaine.fr"
  target: "_blank"
```

> **Attention :** Les groupes `Auto-Discovered` et `Custom Links` sont gérés par Homer Manager — les modifications manuelles seront écrasées à la prochaine synchronisation.

## Icônes

Bibliothèque d'icônes : https://github.com/walkxcode/dashboard-icons  
Pattern CDN : `https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/NOM.png`
