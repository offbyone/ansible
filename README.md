# Ansible Collection - offby1.ansible

[![Ansible Collection Test](https://github.com/offbyone/ansible/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/offbyone/ansible/actions/workflows/ansible-test.yml)
[![Publish to Ansible Galaxy](https://github.com/offbyone/ansible/actions/workflows/ansible-publish.yml/badge.svg)](https://github.com/offbyone/ansible/actions/workflows/ansible-publish.yml)

This galaxy module contains:

- **tailscale inventory**: inventory a tailnet as hosts
- **ubi role**: Installs the UBI binary installer tool
- **ubi module**: Installs and manages binary packages using UBI

## Installation

Install this collection using the Ansible Galaxy CLI:

```bash
ansible-galaxy collection install offby1.ansible
```

You can also include it in a `requirements.yml` file:

```yaml
---
collections:
  - name: offby1.ansible
    version: ">=1.0.0"
```

## Usage

### Using the ubi role

First, install UBI itself using the included role:

```yaml
- name: Install UBI
  hosts: all
  tasks:
    - name: Include ubi role
      include_role:
        name: offby1.ansible.ubi
```

### Using the ubi module

Once UBI is installed, you can use the module to install binaries:

```yaml
- name: Install binaries with ubi module
  hosts: all
  tasks:
    - name: Install various binaries
      offby1.ansible.ubi:
        binaries:
          - BurntSushi/ripgrep
          - sharkdp/fd  
          - name: houseabsolute/precious
            version: v0.1.8
        state: present
        install_dir: /usr/local/bin
        github_token: "{{ github_token | default(omit) }}"
```

### Example playbook

```yaml
---
- name: Set up development tools
  hosts: all
  become: yes
  
  tasks:
    - name: Install UBI
      include_role:
        name: offby1.ansible.ubi
      vars:
        ubi_install_dir: /usr/local/bin

    - name: Install development binaries
      offby1.ansible.ubi:
        binaries:
          - BurntSushi/ripgrep      # Search tool
          - sharkdp/fd             # Find alternative
          - sharkdp/bat            # Cat alternative
          - ogham/exa              # Ls alternative
          - name: cli/cli          # GitHub CLI
            version: v2.40.1
        state: present
        github_token: "{{ lookup('env', 'GITHUB_TOKEN') }}"
```

## Module Parameters

### ubi module

| Parameter     | Type   | Required | Default          | Description |
|---------------|--------|----------|------------------|-------------|
| `binaries`    | list   | yes      | -                | List of binaries to install. Each can be a string or dict with `name` and `version` |
| `state`       | string | no       | `present`        | State of binaries (`present` or `absent`) |
| `install_dir` | string | no       | `/usr/local/bin` | Directory where binaries should be installed |
| `ubi_path`    | string | no       | `ubi`            | Path to the ubi executable |
| `github_token`| string | no       | -                | GitHub token for API access (avoids rate limits) |

### ubi role variables

| Variable          | Type   | Default          | Description |
|-------------------|--------|------------------|-------------|
| `ubi_install_dir` | string | `/usr/local/bin` | Directory where ubi will be installed |
| `ubi_version`     | string | `""`             | Specific version of ubi to install (empty = latest) |
| `ubi_github_token`| string | `""`             | GitHub token for API access |

## Requirements

- Ansible >= 2.9
- Linux, macOS, FreeBSD, or NetBSD target systems
- Internet access to download binaries from GitHub/GitLab

## License

MIT

## Author Information

This collection was created by offby1.

## Developer Guide

### Prerequisites

- [Just](https://github.com/casey/just) - Command runner
- [mise](https://mise.jdx.dev/) - Tool version manager (for Python, Ansible)
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

### Common Tasks

This repository uses a `justfile` to simplify common development tasks. To see all available commands:

```bash
just
```

Common commands:

```bash
# Install development dependencies
just setup

# Run linting
just lint

# Run sanity tests
just sanity

# Run all tests
just test

# Build the collection
just build

# Install the collection locally
just install

# Clean build artifacts
just clean
```

### CI/CD

This repository is configured with GitHub Actions workflows for:
- Running tests on pull requests to validate changes
- Automatically publishing to Ansible Galaxy when changes are merged to the main branch

To set up publishing to Ansible Galaxy, you need to:
1. Create an API key in your Ansible Galaxy account
2. Add the API key as a repository secret in GitHub named `ANSIBLE_GALAXY_API_KEY`

## Inventory Plugins

### `offby1.ansible.tailscale`

Use a tailnet as inventory. This plugin requires a tailscale OAuth client ID and client secret, as well as a tag set to include in the inventory.

All tags on the selected machines will be turned into groups, with individual hosts therein.

#### Example config

``` yaml
---
plugin: offby1.ansible.tailscale
client_secret: "{{ lookup('env', 'TAILSCALE_CLIENT_SECRET') }}"
client_id: "{{ lookup('env', 'TAILSCALE_CLIENT_ID') }}"
tailnet: wandering-shop.org.github
tags:
  - node
```

The plugin supports a pattern like the AWS EC2 plugin, in that you can use the template engine in Ansible to configure it. This allows you to set it up without encoding your secrets in your inventory.


