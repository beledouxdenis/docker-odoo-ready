FROM localhost/odoo:noble

RUN apt-get update && apt-get install -y --no-install-recommends \
    bubblewrap curl postgresql-client ripgrep \
 && npm install -g @openai/codex \
 && rm -rf /var/lib/apt/lists/*
