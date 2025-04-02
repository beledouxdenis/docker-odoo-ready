### Setup Odoo source repositories, with branches in worktrees.

```sh
src=~/src
repositories="odoo enterprise design-themes"
branches="7.0 8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0 16.0 17.0 saas-17.2 saas-17.4 18.0 saas-18.1"
upgrade_repositories="upgrade-util upgrade"
security_repositories="odoo enterprise"
security_branches="8.0 9.0 10.0 11.0 12.0 13.0 14.0 15.0"

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

# Security branches (for Odoo employees having access)
# Add the remote security repository
for r in $security_repositories; do git -C $src/$r/master remote add security git@github.com:odoo/$r-security.git; done
# Update the remote tracking branch of security branches to the security remote, and reset the HEAD
for b in $security_branches; do for r in $security_repositories; do git -C $src/$r/$b fetch security $b && git -C $src/$r/$b branch -u security/$b && git -C $src/$r/$b reset --hard security/$b; done; done
```

### Setup this tool
```sh
src=~/src

# Install requirements
sudo apt install podman postgresql pipx
sudo su - postgres -c "createuser $USER --createdb"
# newer version of podman-compose than the one provided by Ubuntu distribution, to include
# https://github.com/containers/podman-compose/pull/916
pipx install podman-compose==1.2.0

# Setup the repository and symlink the binary in a bin folder within the PATH
cd $src && git clone git@github.com:beledouxdenis/docker-odoo-ready.git
mkdir ~/bin
source ~/.profile # Apply the addition of ~/bin in the PATH
ln -s $src/docker-odoo-ready/docker-odoo ~/bin/odoo
```

### Run Odoo
```sh
odoo -b 17.0 -d 17.0
odoo -b 17.0 -d 17.0 --image focal
odoo -b 17.0 -d 17.0 --domain-whitelist=www.google.com,google.com
odoo shell -b 17.0 -d 17.0
```

### Incoming test mail server, to test mails outgoing from odoo
```sh
podman run --rm --name maildev -p 1025:1025 -p 1080:1080 docker.io/maildev/maildev
odoo -b 18.0 -d 18.0 --smtp host.containers.internal --smtp-port 1025
```
