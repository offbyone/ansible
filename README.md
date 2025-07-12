# Ansible Collection - offbyone.ansible

[![Ansible Collection Test](https://github.com/offby1/ansible/actions/workflows/ansible-test.yml/badge.svg)](https://github.com/offby1/ansible/actions/workflows/ansible-test.yml)
[![Publish to Ansible Galaxy](https://github.com/offby1/ansible/actions/workflows/ansible-publish.yml/badge.svg)](https://github.com/offby1/ansible/actions/workflows/ansible-publish.yml)

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

### `offbyone.ansible.tailscale`

Use a tailnet as inventory. This plugin requires a tailscale OAuth client ID and client secret, as well as a tag set to include in the inventory.

All tags on the selected machines will be turned into groups, with individual hosts therein.

#### Example config

``` yaml
---
plugin: offbyone.ansible.tailscale
client_secret: "{{ lookup('env', 'TAILSCALE_CLIENT_SECRET') }}"
client_id: "{{ lookup('env', 'TAILSCALE_CLIENT_ID') }}"
tailnet: wandering-shop.org.github
tags:
  - node
```

The plugin supports a pattern like the AWS EC2 plugin, in that you can use the template engine in Ansible to configure it. This allows you to set it up without encoding your secrets in your inventory.


