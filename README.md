# dotenv_man (Ansible module)

Manage `.env` / dotenv files (`KEY=VALUE`) idempotently with Ansible.

This custom module ensures environment variables are present (set to specific values) and/or absent (removed), while preserving comments and unrelated lines.

## Features

- Ensure keys exist with desired values
- Remove keys (`absent_keys`)
- Preserves comments/blank lines/unknown lines
- Supports `--check` (check mode)
- Supports `--diff` (shows before/after content)
- Optional quoting (`none`, `double`, `single`)
- Optional file permissions/ownership (`mode`, `owner`, `group`)

## Requirements

Standard requirements for Ansible:
- Ansible installed on the control node
- Managed host needs Python 

## Install 
Place the module in a `library/` directory next to your playbook

## Usage

- Only lines starting with a valid env var name followed by = (e.g. FOO=bar) are treated as entries.
- Comments (# ...), blank lines, and unrelated lines are preserved.
- If a key appears multiple times, v1 updates the first occurrence (future versions may optionally deduplicate).
- Use --diff to see before/after content; use --check for dry-run.

### Options

| Option | Type | Required | Default | Description |
|---|---|---:|---|---|
| `path` | path | yes | — | Path to the dotenv file |
| `values` | dict | no | `{}` | Keys/values to ensure present |
| `absent_keys` | list | no | `[]` | Keys to remove |
| `create` | bool | no | `true` | Create file if missing |
| `quote` | str | no | `none` | `none`, `double`, `single` |
| `mode` | str | no | `null` | File mode (e.g. `0600`) |
| `owner` | str | no | `null` | File owner |
| `group` | str | no | `null` | File group |

### Ensure keys are present (and set permissions)

```yaml
- hosts: app_servers
  tasks:
    - name: Ensure app .env values
      dotenv_kv:
        path: /etc/myapp/myapp.env
        values:
          PORT: "8080"
          LOG_LEVEL: "info"
        mode: "0600"
        owner: myapp
        group: myapp
```

### Remove deprecated keys

```yaml
- hosts: app_servers
  tasks:
    - name: Remove deprecated keys
      dotenv_kv:
        path: /etc/myapp/myapp.env
        absent_keys:
          - OLD_FLAG
          - UNUSED_TOKEN
```

### Use with secrets

```yaml
- hosts: app_servers
  tasks:
    - name: Write secrets safely
      dotenv_kv:
        path: /etc/myapp/myapp.env
        values:
          DB_PASS: "{{ vault_db_pass }}"
          API_TOKEN: "{{ vault_api_token }}"
      no_log: true
```

### Check mode + diff

ansible-playbook -i inventory playbooks/site.yml --check --diff