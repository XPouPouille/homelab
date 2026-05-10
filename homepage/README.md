# Homepage — Homer Dashboard + Auto-Discovery

Self-hosted dashboard powered by [Homer](https://github.com/bastienwirtz/homer), with a companion **Homer Manager** service that:

- **Auto-discovers** Docker containers labelled with `homer.enable=true` or `traefik.enable=true`
- Provides a **web UI** to add/remove custom links manually
- Syncs changes directly into Homer's config (Homer reloads automatically)
- Fully compatible with **Traefik** as a reverse proxy

## Services

| Service | Direct URL | Traefik URL |
|---|---|---|
| Homer dashboard | http://localhost:52000 | http://homer.localhost |
| Homer Manager | http://localhost:52001 | http://manager.localhost |
| Traefik dashboard | http://localhost:8080 | http://traefik.localhost |

## Quick Start

```bash
# Clone
git clone https://github.com/XPouPouille/homelab.git
cd homelab

# Start all services
docker compose up -d

# Check logs
docker compose logs -f
```

Homer dashboard: **http://localhost:52000**
Link Manager UI: **http://localhost:52001**

## Auto-discovery

Add these labels to any container to make it appear on the dashboard:

```yaml
labels:
  - "homer.enable=true"
  - "homer.name=My App"
  - "homer.subtitle=Short description"
  - "homer.url=http://localhost:PORT"
  - "homer.logo=https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/my-app.png"
  - "homer.tag=web"
  - "homer.group=My Group"    # optional, default: Auto-Discovered
```

If the container already has `traefik.enable=true` with a `Host(...)` rule, the URL is extracted automatically.

Homer Manager syncs every **60 seconds**. Click **Sync Now** in the UI to force immediate refresh.

## Manual link management

Open the Manager UI at http://localhost:52001, switch to the **Custom Links** tab, and click **Add Link**.
Links are saved in `homer-manager/data/custom_links.json` and written to `config/config.yml`.

## Traefik integration

All services are routed by Traefik via `*.localhost` domains.  
To use real domains, replace `homer.localhost` / `manager.localhost` / `traefik.localhost`
with your actual hostnames in `docker-compose.yml`.

Point your DNS or `/etc/hosts` to the host machine:
```
192.168.1.X  homer.localhost manager.localhost traefik.localhost
```

## File structure

```
.
├── docker-compose.yml          # All services
├── traefik/
│   └── traefik.yml             # Traefik static config
├── config/
│   └── config.yml              # Homer config (auto-updated by manager)
└── homer-manager/
    ├── Dockerfile
    ├── app.py                  # Flask API + Docker discovery
    ├── requirements.txt
    ├── data/                   # custom_links.json (auto-created)
    └── templates/
        └── index.html          # Management UI
```

## Add a static service (manual config edit)

Edit `config/config.yml` and add under the relevant `services` group:

```yaml
- name: "My App"
  logo: "https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/my-app.png"
  subtitle: "Description"
  tag: "app"
  url: "http://localhost:PORT"
  target: "_blank"
```

> **Note:** Groups named `Auto-Discovered` and `Custom Links` are managed by Homer Manager — manual edits to those groups will be overwritten on the next sync.

## Icons

Find icons at: https://github.com/walkxcode/dashboard-icons  
CDN pattern: `https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/NAME.png`
