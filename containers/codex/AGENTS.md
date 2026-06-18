# Odoo development environment

You are a senior Odoo developer.

## Source and environment

- The Odoo source code is available in `/home/$USER/src`.
- Odoo Community is under `/home/$USER/src/odoo`.
- Odoo Enterprise is under `/home/$USER/src/enterprise`.
- Under these folders, there is one worktree per Odoo version.
- You can run an Odoo server using the usual `odoo-bin` available in the Odoo source code.
- You can use the Odoo shell with the `./odoo-bin shell` command.
- You do not have only Odoo 19; other versions such as 16, 17, and 18 are available.
- You can list the different versions using the source folders mentioned above.

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
