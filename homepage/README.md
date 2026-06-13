# Homepage — Homer Dashboard + Auto-Discovery

Dashboard self-hébergé basé sur [Homer](https://github.com/bastienwirtz/homer) avec un service **Homer Manager** qui :

- **Auto-découvre** les containers Docker labellisés `homer.enable=true` ou `traefik.enable=true`
- Fournit une **interface web** pour ajouter/supprimer des liens manuellement
- Synchronise les changements dans la config Homer (rechargement automatique)
- Routé via **Traefik** (installé séparément) sur le réseau Docker `frontend`
- Homer est la **page principale** sur le domaine public

---

## 1. Prérequis — Installer Docker

```bash
# Mettre à jour les paquets
sudo apt update && sudo apt upgrade -y

# Installer les dépendances
sudo apt install -y ca-certificates curl gnupg

# Ajouter la clé GPG officielle Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Ajouter le dépôt Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker Engine + Compose
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Permettre l'utilisation de Docker sans sudo (nécessite déconnexion/reconnexion)
sudo usermod -aG docker $USER
```

> Après `usermod`, se déconnecter et reconnecter pour que le groupe soit pris en compte.  
> En attendant, préfixer toutes les commandes `docker` avec `sudo`.

---

## 2. Télécharger le projet

```bash
# Cloner le dépôt complet
sudo git clone https://github.com/XPouPouille/homelab.git /opt/homelab

# Aller dans le dossier homepage
cd /opt/homelab/homepage
```

---

## 3. Configurer le domaine (.env)

```bash
# Copier le fichier exemple
sudo cp .env.example .env

# Éditer le fichier .env
sudo nano .env
```

Contenu à renseigner dans `.env` :

```env
DOMAIN=votre-domaine.com
MANAGER_SUBDOMAIN=manager
```

> `.env` est ignoré par git — ne jamais committer ce fichier.

---

## 4. Démarrer les services

```bash
# Construire et démarrer en arrière-plan
sudo docker compose up -d --build

# Vérifier que les containers tournent
sudo docker compose ps

# Consulter les logs en temps réel
sudo docker compose logs -f
```

Homer accessible sur **http://votre-domaine.com** (via Traefik)  
Accès direct local : **http://localhost:52000**

---

## 5. Mettre à jour

```bash
cd /opt/homelab/homepage

# Récupérer les dernières modifications
sudo git pull

# Reconstruire et redémarrer
sudo docker compose up -d --build

# Supprimer les anciennes images inutilisées
sudo docker image prune -f
```

---

## Services

| Service | Accès direct | Via Traefik |
|---|---|---|
| Homer (page principale) | http://localhost:52000 | http://votre-domaine.com |
| Homer Manager | http://localhost:52001 | http://manager.votre-domaine.com |

---

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

---

## Gestion manuelle des liens

Ouvrir le Manager sur http://manager.votre-domaine.com, onglet **Custom Links**, bouton **Add Link**.  
Les liens sont sauvegardés dans `homer-manager/data/custom_links.json` et écrits dans `config/config.yml`.

---

## Structure des fichiers

```
homepage/
├── .env.example              # Template variables (commité)
├── .env                      # Valeurs réelles — IGNORÉ par git
├── docker-compose.yml        # Homer + Homer Manager (Traefik géré séparément)
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

---

## Ajouter un service statique (édition manuelle)

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

---

## Icônes

Bibliothèque : https://github.com/walkxcode/dashboard-icons  
Pattern CDN : `https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/NOM.png`
