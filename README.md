# Ansible Collection - offbyone.ansible

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


