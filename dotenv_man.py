#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

EXAMPLES = '''
# Ensure keys are present (and set permissions)
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

# Remove a keys
- hosts: app_servers
  tasks:
    - name: Remove deprecated keys
      dotenv_kv:
        path: /etc/myapp/myapp.env
        absent_keys:
          - OLD_FLAG
          - UNUSED_TOKEN

# Use with secrets
- hosts: app_servers
  tasks:
    - name: Write secrets safely
      dotenv_kv:
        path: /etc/myapp/myapp.env
        values:
          DB_PASS: "{{ vault_db_pass }}"
          API_TOKEN: "{{ vault_api_token }}"
      no_log: true
'''

DOCUMENTATION = '''
---
module: dotenv_man

short_description:  ansible module to manage .env 

version_added: "1.0.0"

description:
    - "This custom module ensures environment variables are present (set to specific values) and/or absent (removed), while preserving comments and unrelated lines."

options:
  path:
    description:
      - Path to the dotenv file to manage.
    type: path
    required: true
  values:
    description:
      - Mapping of environment variable names to values to ensure presence.
      - Existing keys are updated (first occurrence) if the value differs.
      - Missing keys are appended.
    type: dict
    required: false
    default: {}
  absent_keys:
    description:
      - List of variable names to remove from the dotenv file.
      - If a key appears multiple times, all occurrences are removed.
    type: list
    elements: str
    required: false
    default: []
  create:
    description:
      - Whether to create the dotenv file if it does not exist.
    type: bool
    required: false
    default: true
  quote:
    description:
      - How to quote values when writing.
      - C(none) writes C(KEY=value), C(double) writes C(KEY="value"), C(single) writes C(KEY='value').
    type: str
    required: false
    choices: [none, double, single]
    default: none
  mode:
    description:
      - File mode to set on the dotenv file (e.g. C(0600)).
    type: str
    required: false
  owner:
    description:
      - Owner user name or uid for the dotenv file.
    type: str
    required: false
  group:
    description:
      - Owner group name or gid for the dotenv file.
    type: str
    required: false

author:
    - Marek M (@marekm30)
'''

RETURN = '''
path:
  description: Path to the dotenv file that was managed.
  type: str
  returned: always
managed_keys:
  description: List of keys ensured present via C(values).
  type: list
  elements: str
  returned: always
removed_keys:
  description: List of keys requested for removal via C(absent_keys).
  type: list
  elements: str
  returned: always
changed:
  description: Whether the module made changes (or would in check mode).
  type: bool
  returned: always
diff:
  description: Before/after content of the dotenv file (only when C(--diff) is used and a change occurs).
  type: dict
  returned: when supported and changed
  contains:
    before:
      description: Content before changes.
      type: str
    after:
      description: Content after changes.
      type: str
'''

from ansible.module_utils.basic import AnsibleModule
import os
import re

# Regex to validate keys
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Parse .env lines and return list of lines and original lines
# Treat only lines matching "KEY=VALUE" 
# Comments, blank or other lines stay unchanged
def parse_env_lines(lines):
  key_to_indexes = {}
  for i, line in enumerate(lines):
    # Keep trailing newline out of matching logic
    raw = line.rstrip("\n")
    if not raw or raw.lstrip().startswith("#"):
      continue
    # Match KEY=... at start of line with no leading space
    if "=" in raw:
      key, _ = raw.split("=", 1)
      if KEY_RE.match(key):
        key_to_indexes.setdefault(key, []).append(i)
  return key_to_indexes, lines

# Add quotes if requested
def format_value(value, quote):
  if quote == "none":
    return value
  if quote == "double":
    return '"' + value.replace('"', r"\"") + '"'
  if quote == "single":
    return "'" + value.replace("'", r"\'") + "'"
  raise ValueError("Invalid quote option")

def read_file(path):
  if not os.path.exists(path):
    return []
  with open(path, "r", encoding="utf-8") as f:
    return f.readlines()

def write_file(path, lines, mode, owner, group, module):
  # Ensure parent dir exists
  parent = os.path.dirname(path) or "."
  if not os.path.isdir(parent):
    os.makedirs(parent, exist_ok=True)

  tmp_path = path + ".ansible_tmp"
  with open(tmp_path, "w", encoding="utf-8") as f:
      f.writelines(lines)
  os.replace(tmp_path, path)

  # Apply permissions/ownership if provided
  if mode is not None:
      module.set_mode_if_different(path, mode, False)
  if owner is not None or group is not None:
      module.set_owner_if_different(path, owner, False)
      module.set_group_if_different(path, group, False)




def run_module():

  # Available arguments/parameters a user can pass
  module_args = dict(
    path=dict(type="path", required=True),
    values=dict(type="dict", required=False, default={}),
    absent_keys=dict(type="list", elements="str", required=False, default=[]),
    create=dict(type="bool", default=True),
    quote=dict(type="str", choices=["none", "double", "single"], default="none"),
    mode=dict(type="str", required=False, default=None),
    owner=dict(type="str", required=False, default=None),
    group=dict(type="str", required=False, default=None),
  )

  module = AnsibleModule(
    argument_spec=module_args,
    supports_check_mode=True,
    supports_diff=True,
  )

  path = module.params["path"]
  values = module.params["values"] or {}
  absent_keys = module.params["absent_keys"] or []
  create = module.params["create"]
  quote = module.params["quote"]
  mode = module.params["mode"]
  owner = module.params["owner"]
  group = module.params["group"]




def main():
  run_module()


if __name__ == '__main__':
  main()