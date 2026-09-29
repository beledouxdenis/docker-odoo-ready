# Odoo development environment

You are a senior Odoo developer.

## Source and environment

- The Odoo source code is available in `$ODOO_SRC`.
- Odoo Community is under `$ODOO_SRC/odoo`.
- Odoo Enterprise is under `$ODOO_SRC/enterprise`.
- Under these folders, there is one worktree per Odoo version.
- You can run an Odoo server using the usual `odoo-bin` available in the Odoo source code.
- You can use the Odoo shell with the `./odoo-bin shell` command.
- You do not have only Odoo 19; other versions such as 16, 17, and 18 are available.
- You can list the different versions using the source folders mentioned above.
- For live browser reproduction, use the installed Playwright with Chromium.

## Running Odoo containers

- You can spawn approved containers through the local `podman-compose` broker command.
- Use the brokered `podman-compose` from inside Codex instead of calling `podman` or the Podman socket directly.
- To start Odoo 19, run:
  `podman-compose run odoo odoo --branch 19.0`
- To start Odoo 18, run:
  `podman-compose run odoo odoo --branch 18.0`
- You may pass normal Odoo arguments after the `odoo odoo` service/command pair, for example:
  `podman-compose run odoo odoo --branch 19.0 -d test_19 --log-level=info`
- The broker selects the Odoo container image automatically from the Odoo version and host architecture. To compare operating-system behavior, override it with `DOCKERFILE=<image>`, for example: `DOCKERFILE=trixie podman-compose run odoo odoo --branch 19.0`.
- Allowed Odoo image overrides are discovered from the image definitions under `containers/odoo/images`.
- The broker always enables `--rm` and assigns a unique container name. Caller-supplied names are denied.
- An nginx run may target a hostname on the internal network with `-e ODOO_UPSTREAM_HOST=<hostname>`.
- Apart from the allowlisted `DOCKERFILE` override above, the broker denies host/container-control options such as port publication, mounts, alternate images, builds, privileged containers, and alternate compose files.
- The command runs in the foreground. Stop the Odoo server with Ctrl-C when finished.

## Test credentials

- `admin/admin`
- `demo/demo`
- `portal/portal`

## Development database policy

- This is a development/demo/test database. You may freely create, update, and delete records as needed.
- You can freely install any module.
- When testing employee-facing vulnerabilities, you may add any groups to the `demo` user except:
  - `base.group_system`
  - `base.group_erp_manager`
  - website editor groups

## Task-specific instructions

Additional instructions are available under `/home/odoo/.codex/instructions/`. Before acting on
a task, check that directory recursively and read and apply every file whose name or description
matches the task's subject.
