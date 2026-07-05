# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-email: NetBox as the native source of truth for **email infrastructure** — which mail
domains a server is authoritative for (and their DKIM signing identity), the mailboxes living under
each domain, the aliases / forwarding maps that fan an address out to other destinations, and the
forwarding relays / smarthosts that outbound mail is routed through.

**It composes ``netbox-services``, it does not re-model it (the netbox-ai pattern):** the mail server
that serves a domain (Stalwart, Postfix, etc.) is a :class:`netbox_services.ServiceInstance`;
``MailDomain`` and ``MailRelay`` **FK** it, so ``required_plugins = ["netbox_services"]`` and the
migration depends on ``netbox_services.0001_initial``. Deployment metadata (host, ports, health)
stays on the ``ServiceInstance`` — it is referenced, never duplicated.

**Secret policy (load-bearing):** a mailbox password, a relay auth secret, and a DKIM private key are
**never** field values here. ``Mailbox.credential_ref`` / ``MailRelay.credential_ref`` /
``MailDomain.dkim_key_ref`` are **OpenBao path references** (the netbox-services ``credential_ref``
convention) — the secret value stays in OpenBao.

This is what the ``tofu-stalwart`` provider reads as the mail-infrastructure SoT.
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxEmailConfig(PluginConfig):
    name = "netbox_email"
    verbose_name = "NetBox Email"
    description = "Native SoT for email infrastructure (mail domains, mailboxes, aliases, relays)"
    version = __version__
    author = "Jameson"
    base_url = "email"
    min_version = "4.6.0"
    max_version = "4.6.99"
    # MailDomain/MailRelay.service_instance FK netbox_services.ServiceInstance and the migration
    # depends on netbox_services.0001_initial, so the dependency is hard and fails fast at startup.
    required_plugins = ["netbox_services"]


config = NetBoxEmailConfig
