# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _item(model, label):
    return PluginMenuItem(
        link=f"plugins:netbox_email:{model}_list",
        link_text=label,
        buttons=[
            PluginMenuButton(f"plugins:netbox_email:{model}_add", "Add", "mdi mdi-plus-thick")
        ],
    )


menu = PluginMenu(
    label="Email",
    groups=(
        ("Domains", (_item("maildomain", "Mail Domains"),)),
        ("Mailboxes", (_item("mailbox", "Mailboxes"),)),
        ("Aliases", (_item("mailalias", "Mail Aliases"),)),
        ("Relays", (_item("mailrelay", "Mail Relays"),)),
    ),
    icon_class="mdi mdi-email",
)
