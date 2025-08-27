# UBI Collection Plugins

This directory contains the plugins for the offby1.ansible collection.

## Modules

### ubi

The `ubi` module installs binary executables from GitHub and GitLab releases using the UBI (Universal Binary Installer) tool.

**Usage:**

```yaml
- name: Install development tools
  offby1.ansible.ubi:
    binaries:
      - BurntSushi/ripgrep
      - sharkdp/fd
      - name: cli/cli
        version: v2.40.1
    state: present
    install_dir: /usr/local/bin
```

See the module documentation for complete parameter details:

```bash
ansible-doc offby1.ansible.ubi
```
