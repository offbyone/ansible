import asyncio
import json
import os
from typing import Any, TypedDict

import click
import httpx
from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import json
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.template import Templar
from ansible.utils.display import Display, subprocess
from authlib.integrations.httpx_client import AsyncOAuth2Client as OAuth2

display = Display()

DOCUMENTATION = """
    name: tailscale
    plugin_type: inventory
    short_description: Tailscale dynamic inventory source
    description:
        - This inventory plugin allows the use of Tailscale as a dynamic inventory source.
    options:
        client_id:
            description: OAuth2 Client ID for Tailscale
            required: True
            type: string
        client_secret:
            description: OAuth2 Client Secret for Tailscale
            required: True
            type: string
            no_log: True
        tailnet:
            description: The tailnet to use
            type: str
            required: True
            env:
                - name: TAILNET
        tags:
            description: List of tags to filter devices by
            type: list
            required: False
            default: []
"""


class TailscaleOAuth2API:
    BASE_URL = "https://api.tailscale.com/api/v2"
    TOKEN_URL = "https://api.tailscale.com/api/v2/oauth/token"

    def __init__(self, client_id, client_secret, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.token_file = ".tailscale_token.json"  # Store token to reuse later
        self.token = None
        self.client = httpx.Client()

    @classmethod
    async def setup(cls, client_id, client_secret, token_url=TOKEN_URL):
        self = cls(client_id, client_secret, token_url)
        await self.connect()
        return self

    async def connect(self):
        await self.load_token()

    async def load_token(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                self.token = json.load(f)
        else:
            await self.get_token()

    async def get_token(self):
        async with OAuth2(self.client_id, self.client_secret) as client:
            self.token = await client.fetch_token(self.token_url)

    async def get_devices(self, tailnet_name):
        headers = {"Authorization": f"Bearer {self.token['access_token']}"}
        url = f"{self.BASE_URL}/tailnet/{tailnet_name}/devices"

        response = self.client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code}: {response.text}")


class InventoryModule(BaseInventoryPlugin):
    NAME = "tailscale"

    class TemplatedOptions:
        TEMPLATABLE_OPTIONS = [
            "client_secret",
            "client_id",
            "tailnet",
            "tags",
        ]

        def __init__(self, templar: Templar, options: dict[str, Any]):
            self.original_options = options
            self.templar = templar

        def __getitem__(self, *args):
            return self.original_options.__getitem__(*args)

        def __setitem__(self, *args):
            return self.original_options.__setitem__(*args)

        def get(self, *args):
            value = self.original_options.get(*args)
            if (
                not value
                or not self.templar
                or args[0] not in self.TEMPLATABLE_OPTIONS
                or not self.templar.is_template(value)
            ):
                return value

            return self.templar.template(variable=value, disable_lookups=False)

    def get_options(self, *args):
        return self.TemplatedOptions(self.templar, super().get_options(*args))

    def get_option(self, option, hostvars=None):
        return self.TemplatedOptions(
            self.templar, {option: super().get_option(option, hostvars)}
        ).get(option)

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache=True)
        self.config = self._read_config_data(path)

        client_id = self.get_option("client_id")
        client_secret = self.get_option("client_secret")
        tailnet = self.get_option("tailnet")
        tags = self.get_option("tags")

        async def aparse():
            tailscale = await TailscaleOAuth2API.setup(client_id, client_secret)
            devices = await tailscale.get_devices(tailnet)

            return devices

        loop = asyncio.get_event_loop()
        devices = loop.run_until_complete(aparse())

        for device in devices["devices"]:
            device_tags = device.get("tags", [])
            if not tags or any(f"tag:{tag}" in device_tags for tag in tags):
                hostname = device["hostname"]
                ip_address = device["addresses"][
                    0
                ]  # Assuming the first address is the desired one
                self.inventory.add_host(hostname)
                self.inventory.set_variable(hostname, "ansible_host", ip_address)

                for tag in device_tags:
                    groups = self.inventory.get_groups_dict()
                    group_name = f"tag_{tag[4:]}"
                    if group_name not in groups:
                        self.inventory.add_group(group_name)
                    self.inventory.add_child(group_name, hostname)


TailnetConfig = TypedDict(
    "TailnetConfig",
    {"client_id": str, "client_secret": str, "tailnet": str, "tags": list},
)


@click.group()
@click.option(
    "--client-id",
    required=True,
    help="OAuth2 Client ID for Tailscale",
    envvar="TAILSCALE_CLIENT_ID",
    type=str,
)
@click.option(
    "--client-secret",
    required=True,
    help="OAuth2 Client Secret for Tailscale",
    envvar="TAILSCALE_CLIENT_SECRET",
    type=str,
)
@click.option(
    "--tailnet",
    required=True,
    help="The tailnet to use",
    envvar="TAILNET_NAME",
    type=str,
)
@click.pass_context
def main(ctx: click.Context, client_id: str, client_secret: str, tailnet: str):
    ctx.obj = {
        "client_id": client_id,
        "client_secret": client_secret,
        "tailnet": tailnet,
    }


@main.command()
@click.pass_obj
@click.option("--path", type=str, default="inventory/tailscale.yaml")
@click.argument("tags", nargs=-1)
def inventory(obj: TailnetConfig, path: str, tags: list[str]):
    inv = InventoryModule()
    inv.parse(None, None, path)


@main.command()
@click.pass_obj
def nodes(obj: TailnetConfig):
    async def inner_main():
        tailscale_api = await TailscaleOAuth2API.setup(
            obj["client_id"],
            obj["client_secret"],
        )
        devices = await tailscale_api.get_devices(obj["tailnet"])

        for device in devices["devices"]:
            print(f"Device: {device['hostname']}, IP: {device['addresses'][0]}")

    asyncio.run(inner_main())


if __name__ == "__main__":
    main()
