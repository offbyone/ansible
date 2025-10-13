# UBI Role

This role installs packages using [ubi](https://github.com/houseabsolute/ubi) (Universal Binary Installer), which downloads and installs pre-built binaries from GitHub releases.

## Requirements

None.

## Role Variables

See `defaults/main.yml` for available variables.

## Dependencies

None.

## Example Playbook

```yaml
- hosts: all
  roles:
    - offby1.ansible.ubi
```

## License

MIT

## Author Information

Created by Chris Rose (offline@offby1.net)