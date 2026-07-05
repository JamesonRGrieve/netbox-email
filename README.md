<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-email

A NetBox 4.6 plugin: the **native source of truth for email infrastructure** — which mail domains a
server is authoritative for (and their DKIM signing identity), the mailboxes under each domain, the
aliases / forwarding maps that fan an address out to other destinations, and the forwarding relays /
smarthosts outbound mail is routed through.

It is what the `tofu-stalwart` provider reads to realize a mail server. It does **not** own message
content or delivery state — the server owns that at runtime.

## Scope

- **In scope:** mail domains + authority mode + DKIM identity, mailboxes, aliases/forwarding maps,
  and outbound relays/smarthosts.
- **Out of scope:** message bodies / delivery queues (the server owns them), secret values (OpenBao
  owns them), and cross-service application HA fail-over pairing (that lives in `netbox-services`
  `HAMirror`).

## Composes netbox-services

The mail server that serves a domain (Stalwart, Postfix, etc.) is a
`netbox_services.ServiceInstance`. `MailDomain` and `MailRelay` FK it, so
`PluginConfig.required_plugins = ["netbox_services"]` and the migration depends on
`netbox_services.0001_initial`. This plugin is the **email layer on top of** `ServiceInstance` — it
references, it does not re-model deployment metadata (the `netbox-ai` pattern).

## Model

- **MailDomain** — `name` (unique), `domain_type` (local / relay / alias), optional
  `service_instance` link, `is_catchall`, `dkim_selector`, `dkim_key_ref` (**OpenBao path**).
- **Mailbox** (FK domain) — `local_part`, `mailbox_type` (individual / group / shared),
  `display_name`, `quota_mb`, `credential_ref` (**OpenBao path**), `is_active`. Unique per
  `(local_part, domain)`; the address is `local_part@domain`.
- **MailAlias** (FK domain) — `source_local_part`, `destinations` (a Postgres array of addresses),
  `is_active`. Unique per `(source_local_part, domain)`.
- **MailRelay** — `name` (unique), `upstream_host`, `upstream_port` (default 587), `auth_type`
  (none / plain / login / cram_md5), `credential_ref` (**OpenBao path**), `use_tls`, optional
  `service_instance` link.

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Secret policy

A mailbox password, a relay auth secret, and a DKIM private key are **never** field values here.
`Mailbox.credential_ref` / `MailRelay.credential_ref` / `MailDomain.dkim_key_ref` are **OpenBao path
references** (the `netbox-services` convention). NetBox holds the structure; OpenBao holds the secret.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-email   # or: pip install -e .
# add "netbox_email" to PLUGINS in configuration.py (netbox_services must be enabled too)
python manage.py migrate netbox_email
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test framework.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_email --keepdb -v2
```

## License

AGPL-3.0-or-later.
