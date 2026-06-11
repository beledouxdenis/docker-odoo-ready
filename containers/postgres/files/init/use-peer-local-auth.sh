#!/bin/bash
set -e

cat > "$PGDATA/pg_hba.conf" <<'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Unix socket connections use peer auth, so the OS user must match the DB role.
local   all             all                                     peer
local   replication     all                                     peer

# TCP connections require passwords. The postgres and odoo roles have none.
host    all             all             all                     scram-sha-256
host    replication     all             all                     scram-sha-256
EOF
