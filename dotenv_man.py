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

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        new=dict(type='bool', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_message'] = module.params['name']
    result['message'] = 'goodbye'

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    if module.params['new']:
        result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()