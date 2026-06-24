### Setup Odoo source repositories, with branches in worktrees.

```sh
src=~/src
repositories="odoo enterprise design-themes"
branches="7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0 17.0 18.0 saas-18.2 saas-18.3 saas-18.4 19.0 saas-19.1 saas-19.2 saas-19.3"
upgrade_repositories="upgrade-util upgrade"

# Create the source folder
mkdir $src

# Clone Odoo repositories
for r in $repositories; do mkdir $src/$r && cd $src/$r && git clone -b master git@github.com:odoo/$r.git master; done
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

### Run postgresql and squid in background
```sh
podman-compose up -d postgres squid
```
To add more domains in the whitelist of the HTTP proxy (squid), add domains in the file
`containers/squid/files/whitelist.txt`

### Run Odoo
```sh
odoo -b 19.0 -d 19.0
odoo -b 19.0 -d 19.0 --image trixie
odoo shell -b 19.0 -d 19.0
```

### Run codex
```sh
podman-compose run --rm codex
# or
ln -s $src/docker-odoo-ready/host/files/bin/odoo-codex ~/bin/odoo-codex
# To mount additional folders to give to codex
podman-compose run --rm -v path/to/host/folder:path/in/container codex
# To run a shell
podman-compose run --rm codex /bin/bash
```

### Incoming test mail server, to test mails outgoing from odoo
```sh
podman run --rm --name maildev -p 1025:1025 -p 1080:1080 docker.io/maildev/maildev
odoo -b 19.0 -d 19.0 --smtp host.containers.internal --smtp-port 1025
```
