import json
import logging
import os
import re
import threading
import time
import uuid
from pathlib import Path

import docker
import yaml
from flask import Flask, jsonify, render_template, request

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

CONFIG_PATH = os.environ.get("HOMER_CONFIG", "/config/config.yml")
DATA_PATH = os.environ.get("DATA_PATH", "/data")
CUSTOM_LINKS_FILE = os.path.join(DATA_PATH, "custom_links.json")
SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL", "60"))

MANAGED_GROUP_DOCKER = "Auto-Discovered"
MANAGED_GROUP_CUSTOM = "Custom Links"
MANAGED_GROUPS = {MANAGED_GROUP_DOCKER, MANAGED_GROUP_CUSTOM}


def load_custom_links():
    if os.path.exists(CUSTOM_LINKS_FILE):
        with open(CUSTOM_LINKS_FILE) as f:
            return json.load(f)
    return []


def save_custom_links(links):
    Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
    with open(CUSTOM_LINKS_FILE, "w") as f:
        json.dump(links, f, indent=2)


def get_docker_services():
    try:
        client = docker.from_env()
        services = []
        for c in client.containers.list():
            labels = c.labels
            homer_enabled = labels.get("homer.enable", "").lower() == "true"
            traefik_enabled = labels.get("traefik.enable", "").lower() == "true"
            if not homer_enabled and not traefik_enabled:
                continue

            url = labels.get("homer.url", "")
            if not url:
                for key, val in labels.items():
                    if ".rule" in key and "Host" in val:
                        m = re.search(r"Host\(`([^`]+)`\)", val)
                        if m:
                            url = f"http://{m.group(1)}"
                            break

            services.append({
                "id": c.id[:12],
                "name": labels.get("homer.name", c.name),
                "subtitle": labels.get("homer.subtitle", c.status),
                "url": url,
                "logo": labels.get("homer.logo", ""),
                "tag": labels.get("homer.tag", "docker"),
                "group": labels.get("homer.group", MANAGED_GROUP_DOCKER),
                "source": "docker",
            })
        return services
    except Exception as e:
        app.logger.error("Docker error: %s", e)
        return []


def sync_homer_config():
    if not os.path.exists(CONFIG_PATH):
        app.logger.warning("Homer config not found: %s", CONFIG_PATH)
        return

    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f) or {}

    preserved = [s for s in config.get("services", [])
                 if s.get("name") not in MANAGED_GROUPS]

    docker_services = get_docker_services()
    if docker_services:
        preserved.append({
            "name": MANAGED_GROUP_DOCKER,
            "icon": "fab fa-docker",
            "items": [{
                "name": svc["name"],
                "subtitle": svc["subtitle"],
                "url": svc["url"] or "#",
                "logo": svc["logo"] or "https://cdn.jsdelivr.net/gh/walkxcode/dashboard-icons/png/docker.png",
                "tag": svc["tag"],
                "target": "_blank",
            } for svc in docker_services],
        })

    custom = load_custom_links()
    if custom:
        preserved.append({
            "name": MANAGED_GROUP_CUSTOM,
            "icon": "fas fa-link",
            "items": [{
                "name": lnk["name"],
                "subtitle": lnk.get("subtitle", ""),
                "url": lnk["url"],
                "logo": lnk.get("logo", ""),
                "tag": lnk.get("tag", ""),
                "target": "_blank",
            } for lnk in custom],
        })

    config["services"] = preserved

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    app.logger.info("Homer config synced (%d docker, %d custom)", len(docker_services), len(custom))


def _background_sync():
    while True:
        time.sleep(SYNC_INTERVAL)
        try:
            sync_homer_config()
        except Exception as e:
            app.logger.error("Background sync error: %s", e)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/containers")
def api_containers():
    return jsonify(get_docker_services())


@app.route("/api/links", methods=["GET"])
def api_get_links():
    return jsonify(load_custom_links())


@app.route("/api/links", methods=["POST"])
def api_add_link():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("url"):
        return jsonify({"error": "name and url required"}), 400
    links = load_custom_links()
    data["id"] = str(uuid.uuid4())[:8]
    data["source"] = "manual"
    links.append(data)
    save_custom_links(links)
    sync_homer_config()
    return jsonify(data), 201


@app.route("/api/links/<link_id>", methods=["DELETE"])
def api_delete_link(link_id):
    links = load_custom_links()
    links = [lnk for lnk in links if lnk.get("id") != link_id]
    save_custom_links(links)
    sync_homer_config()
    return "", 204


@app.route("/api/sync", methods=["POST"])
def api_sync():
    sync_homer_config()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
    sync_homer_config()
    t = threading.Thread(target=_background_sync, daemon=True)
    t.start()
    app.run(host="0.0.0.0", port=5000)
