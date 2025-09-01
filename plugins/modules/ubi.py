#!/usr/bin/python

# Copyright: (c) 2025, offby1
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ubi

short_description: Install binaries using UBI (Universal Binary Installer)

version_added: "1.0.0"

description:
    - This module uses UBI to install binary releases from GitHub or GitLab repositories.
    - It can install multiple binaries with specific versions.
    - Requires UBI to be installed on the target system.

options:
    binaries:
        description:
            - List of binaries to install.
            - Each item can be a simple string (project path) or a dict with name and version.
        required: true
        type: list
        elements: raw
    state:
        description: State of the binaries
        required: false
        default: present
        choices: [ present, absent ]
        type: str
    install_dir:
        description: Directory where binaries should be installed
        required: false
        default: "/usr/local/bin"
        type: str
    ubi_path:
        description: Path to the ubi executable
        required: false
        default: "ubi"
        type: str
    github_token:
        description: GitHub token for API access (to avoid rate limits)
        required: false
        type: str

author:
    - offby1 (@offby1)
"""

EXAMPLES = r"""
- name: Install binaries with ubi
  offby1.ansible.ubi:
    binaries:
      - ripgrep
      - name: houseabsolute/precious
        version: v0.1.8
    state: present

- name: Install binaries to specific directory
  offby1.ansible.ubi:
    binaries:
      - BurntSushi/ripgrep
      - sharkdp/fd
    install_dir: "/home/user/bin"
    state: present

- name: Remove binaries
  offby1.ansible.ubi:
    binaries:
      - ripgrep
    state: absent
"""

RETURN = r"""
results:
    description: List of results for each binary operation
    returned: always
    type: list
    elements: dict
    contains:
        binary:
            description: The binary that was processed
            type: str
            returned: always
        state:
            description: The state of the binary after the operation
            type: str
            returned: always
        changed:
            description: Whether the binary state was changed
            type: bool
            returned: always
        msg:
            description: Human readable message about the operation
            type: str
            returned: always
        rc:
            description: Return code from ubi command
            type: int
            returned: when ubi command was executed
        stdout:
            description: stdout from ubi command
            type: str
            returned: when ubi command was executed
        stderr:
            description: stderr from ubi command
            type: str
            returned: when ubi command was executed
"""

import os
import subprocess

from ansible.module_utils.basic import AnsibleModule


def binary_exists(install_dir, binary_name):
    """Check if binary already exists in install directory."""
    if "/" in binary_name:
        binary_name = binary_name.split("/")[-1]

    binary_path = os.path.join(install_dir, binary_name)
    return os.path.isfile(binary_path) and os.access(binary_path, os.X_OK)


def get_binary_name(binary):
    """Extract binary name from project path."""
    if isinstance(binary, dict):
        project = binary.get("name", "")
    else:
        project = str(binary)

    if "/" in project:
        return project.split("/")[-1]
    return project


def install_binary(module, binary, install_dir, ubi_path, github_token=None):
    """Install a single binary using ubi."""
    if isinstance(binary, dict):
        project = binary.get("name")
        version = binary.get("version")
    else:
        project = str(binary)
        version = None

    if not project:
        return {
            "binary": binary,
            "state": "error",
            "changed": False,
            "msg": "Binary name is required",
            "rc": 1,
        }

    binary_name = get_binary_name(binary)

    # Check if binary already exists
    if binary_exists(install_dir, binary_name):
        return {
            "binary": project,
            "state": "present",
            "changed": False,
            "msg": f"Binary {binary_name} already exists",
        }

    # Build ubi command
    cmd = [ubi_path, "--project", project, "--in", install_dir]

    if version:
        cmd.extend(["--tag", version])

    # Set up environment
    env = os.environ.copy()
    if github_token:
        env["GITHUB_TOKEN"] = github_token

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, env=env, check=False
        )

        if result.returncode == 0:
            return {
                "binary": project,
                "state": "present",
                "changed": True,
                "msg": f"Successfully installed {binary_name}",
                "rc": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        else:
            return {
                "binary": project,
                "state": "error",
                "changed": False,
                "msg": f"Failed to install {binary_name}: {result.stderr}",
                "rc": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

    except FileNotFoundError:
        return {
            "binary": project,
            "state": "error",
            "changed": False,
            "msg": f"ubi executable not found at {ubi_path}",
            "rc": 127,
        }
    except Exception as e:
        return {
            "binary": project,
            "state": "error",
            "changed": False,
            "msg": f"Error installing {binary_name}: {str(e)}",
            "rc": 1,
        }


def remove_binary(module, binary, install_dir):
    """Remove a binary from the install directory."""
    binary_name = get_binary_name(binary)
    binary_path = os.path.join(install_dir, binary_name)

    if not binary_exists(install_dir, binary_name):
        return {
            "binary": str(binary),
            "state": "absent",
            "changed": False,
            "msg": f"Binary {binary_name} does not exist",
        }

    try:
        os.remove(binary_path)
        return {
            "binary": str(binary),
            "state": "absent",
            "changed": True,
            "msg": f"Successfully removed {binary_name}",
        }
    except Exception as e:
        return {
            "binary": str(binary),
            "state": "error",
            "changed": False,
            "msg": f"Failed to remove {binary_name}: {str(e)}",
        }


def run_module():
    module_args = dict(
        binaries=dict(type="list", elements="raw", required=True),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        install_dir=dict(type="str", default="/usr/local/bin"),
        ubi_path=dict(type="str", default="ubi"),
        github_token=dict(type="str", no_log=True),
    )

    result = {"changed": False, "results": []}

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    binaries = module.params["binaries"]
    state = module.params["state"]
    install_dir = module.params["install_dir"]
    ubi_path = module.params["ubi_path"]
    github_token = module.params["github_token"]

    # Check if install directory exists
    if not os.path.isdir(install_dir):
        module.fail_json(msg=f"Install directory {install_dir} does not exist")

    # Process each binary
    overall_changed = False

    for binary in binaries:
        if module.check_mode:
            # In check mode, just report what would be done
            binary_name = get_binary_name(binary)
            if state == "present":
                if binary_exists(install_dir, binary_name):
                    binary_result = {
                        "binary": str(binary),
                        "state": "present",
                        "changed": False,
                        "msg": f"Binary {binary_name} already exists",
                    }
                else:
                    binary_result = {
                        "binary": str(binary),
                        "state": "present",
                        "changed": True,
                        "msg": f"Would install {binary_name}",
                    }
            else:  # absent
                if binary_exists(install_dir, binary_name):
                    binary_result = {
                        "binary": str(binary),
                        "state": "absent",
                        "changed": True,
                        "msg": f"Would remove {binary_name}",
                    }
                else:
                    binary_result = {
                        "binary": str(binary),
                        "state": "absent",
                        "changed": False,
                        "msg": f"Binary {binary_name} does not exist",
                    }
        else:
            # Actually perform the operation
            if state == "present":
                binary_result = install_binary(
                    module, binary, install_dir, ubi_path, github_token
                )
            else:  # absent
                binary_result = remove_binary(module, binary, install_dir)

        if binary_result["changed"]:
            overall_changed = True

        result["results"].append(binary_result)

    result["changed"] = overall_changed

    # Check if any operations failed
    failed_operations = [r for r in result["results"] if r["state"] == "error"]
    if failed_operations:
        failure_msgs = [r["msg"] for r in failed_operations]
        module.fail_json(
            msg=f"Some operations failed: {'; '.join(failure_msgs)}", **result
        )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
