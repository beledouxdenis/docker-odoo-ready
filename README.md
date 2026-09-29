### Setup Odoo source repositories, with branches in worktrees.

```sh
src=~/src
repositories="odoo enterprise design-themes"
branches="7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0 17.0 18.0 saas-18.2 saas-18.3 saas-18.4 19.0 saas-19.1 saas-19.2 saas-19.3"
upgrade_repositories="upgrade-util upgrade"

# Create the source folder
mkdir $src

# Clone Odoo repositories
for r in $repositories; do mkdir $src/$r && cd $src/$r && git clone git@github.com:odoo/$r.git master && cd master && git switch master; done
# Rename remote origin to odoo, add remote odoo-dev, for all repositories
for r in $repositories; do git -C $src/$r/master remote rename origin odoo && git -C $src/$r/master remote add odoo-dev git@github.com:odoo-dev/$r.git;  done
# Add a worktree for all branches for all repositories
for b in $branches; do for r in $repositories; do git -C $src/$r/master worktree add ../$b $b; done; done

# Clone Odoo Upgrade repositories
for r in $upgrade_repositories; do cd $src && git clone git@github.com:odoo/$r.git; done
```

### Setup this tool
```sh
src=~/src

# Install requirements
sudo apt install podman pipx
# newer version of podman-compose than the one provided by Ubuntu distribution, to include
# https://github.com/containers/podman-compose/pull/916
pipx install podman-compose

# Setup the repository and symlink the binary in a bin folder within the PATH
cd $src && git clone git@github.com:beledouxdenis/docker-odoo-ready.git
mkdir ~/bin
source ~/.profile # Apply the addition of ~/bin in the PATH
ln -s $src/docker-odoo-ready/docker-odoo ~/bin/odoo
```

### Build images
```sh
podman-compose build postgres
podman-compose build odoo
podman-compose build codex
# For a specific image, if needed
DOCKERFILE=noble podman-compose build odoo
```

### Run Odoo
```sh
odoo -b 19.0 -d 19.0
odoo -b 19.0 -d 19.0 --image trixie
odoo shell -b 19.0 -d 19.0
```

### Run codex

Codex can spawn approved compose services through a constrained `podman-compose`
client. To avoid forwarding the Podman socket, the `podman-broker` parses each
request and invokes the real `podman-compose` itself.

The broker accepts `podman-compose run` for the `odoo` and `nginx` services,
`inspect` for active broker-managed containers, and `exec` for active Odoo
containers. It forces `--rm`, assigns a unique container name, and validates
the service command. Caller-provided names, port publication, mounts,
arbitrary images or compose files, builds, privileged options, unknown flags,
and environment changes other than the documented overrides are rejected.
The sole `podman-compose run -e` override is
`ODOO_UPSTREAM_HOST=<hostname>` for the `nginx` service, allowing each proxy to
target a specific container on the internal network. The hostname is
syntax-validated before being substituted into the nginx configuration.
This is to avoid for instance he would be able to escape its container by mounting a volume
from the host to the container and change host files from within the container.

For this, the `podman-broker` needs to be able to communicate with the host Podman.
On Linux, it's done by enabling the podman socket
On Macos, it's done by using the default SSH connection given by `podman machine init`.

For Linux only:
```sh
systemctl --user start podman.socket
```

For MacOS only:
```sh
uri="$(podman system connection list --format '{{if .Default}}{{.URI}}{{end}}')"
key="$(podman system connection list --format '{{if .Default}}{{.Identity}}{{end}}')"
printf 'PODMAN_CONTAINER_HOST=%s\n' "${uri/127.0.0.1/host.containers.internal}" >> .env
printf 'PODMAN_CONTAINER_SSHKEY=%s\n' "${key}" >> .env
```

```sh
podman-compose run --rm codex
# To mount additional folders to give to codex
podman-compose run --rm -v path/to/host/folder:path/in/container codex
# To run a shell
podman-compose run --rm codex /bin/bash
```

Inside the Codex container, an Odoo server can be started with:

```sh
podman-compose run odoo odoo --branch 19.0 -d test_19
```

The broker injects `--rm`, generates and prints a unique container name, and
keeps the name registered while the command is running for subsequent approved
`inspect` or Odoo `exec` operations. With one Odoo run, Codex can reach it at
`http://odoo:8069` through the Compose service alias. When several Odoo runs
are active, use a specific internal hostname instead of the shared `odoo`
alias. The broker does not permit publishing container ports on the host.

For Odoo runs, the broker selects the image automatically from the Odoo version
and host architecture, using the same policy as `docker-odoo`. Codex can choose
an allowed image explicitly when comparing operating-system behavior:

```sh
DOCKERFILE=trixie podman-compose run odoo odoo --branch 19.0
DOCKERFILE=noble podman-compose run odoo odoo --branch 19.0
```

### Incoming test mail server, to test mails outgoing from odoo
```sh
podman-compose up -d mailpit
odoo -b 19.0 -d 19.0 --smtp mailpit --smtp-port 1025
```

The Mailpit web UI is available at http://127.0.0.1:8025.
