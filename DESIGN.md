<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-email — Design

## 0. Purpose

NetBox is the native source of truth for **email infrastructure** — the data the `tofu-stalwart`
provider reads to stand up and reconcile a real mail server: which domains it is authoritative for,
the mailboxes and aliases under each domain, and the outbound relays/smarthosts mail is routed
through. Message content and delivery queues are explicitly **not** modeled — the server owns those
at runtime. This plugin owns the *configuration*, not the *mail flow*.

Everything is a real typed column or a child row — no `config_context`, no CustomField data-blob
(the workspace's retired anti-pattern). The alias fan-out is a first-class Postgres array on
`MailAlias.destinations`, not a serialized string.

## 1. Model diagram

```
        netbox_services.ServiceInstance  (the mail server: Stalwart/Postfix/…)
                 ▲ (opt FK)                             ▲ (opt FK)
                 │                                      │
        ┌────────┴───────────────────────────┐   ┌─────┴──────────────────────────┐
        │            MailDomain               │   │           MailRelay            │
        │  name·domain_type·is_catchall·      │   │  name·upstream_host·port·      │
        │  dkim_selector·dkim_key_ref         │   │  auth_type·credential_ref·tls  │
        └───┬───────────────────────┬─────────┘   └────────────────────────────────┘
     FK     │ mailboxes             │ aliases       (standalone smarthost / proxy)
            ▼                       ▼
         Mailbox                 MailAlias
   local_part·type·quota·   source_local_part·
   credential_ref·active    destinations[]·active
   (unique per domain)      (unique per domain)
```

- **MailDomain** is the anchor: a domain the mail server is authoritative for. `domain_type`
  selects how the server treats it — `local` (hosts mailboxes), `relay` (accepts and forwards
  onward), `alias` (whole domain rewrites to another). `service_instance` is an *optional*
  composition link to the netbox-services instance that serves it (`on_delete=SET_NULL` — deleting
  the instance record must not cascade away the domain SoT). `dkim_selector` + `dkim_key_ref` carry
  the DKIM signing identity (the key itself lives in OpenBao).
- **Mailbox** is a mailbox under a domain, uniquely keyed per `(local_part, domain)` — the address
  is `local_part@domain`. `mailbox_type` distinguishes individual / group (distribution list) /
  shared. `quota_mb` NULL = server default.
- **MailAlias** is a forwarding map: mail to `source_local_part@domain` fans out to every address in
  the `destinations` array (local or remote), uniquely keyed per `(source_local_part, domain)`.
- **MailRelay** is a standalone outbound relay/smarthost. `auth_type` selects the SMTP AUTH
  mechanism; the relay credential lives in OpenBao at `credential_ref`.

## 2. The compose-with-netbox-services boundary

`netbox-services` already owns the service catalog + instance layer. A deployed mail server *is* a
`ServiceInstance` (its catalog row carries the service type, health endpoint, resources, etc.).
`MailDomain` and `MailRelay` **FK** that instance rather than re-modeling deployment metadata (host,
ports, health, status). `required_plugins = ["netbox_services"]` + the migration dependency on
`netbox_services.0001_initial` make the dependency hard and fail-fast — the `netbox-ai` pattern.

Cross-service application HA fail-over pairing already lives in `netbox_services.HAMirror` and is
**referenced, never duplicated** here. This plugin models only the email-native configuration
surface (domains, mailboxes, aliases, relays) that `ServiceInstance` / `HAMirror` cannot express.

## 3. Secret-ref policy

A mailbox password, a relay auth secret, and a DKIM private key are **never** model fields.
`Mailbox.credential_ref`, `MailRelay.credential_ref`, and `MailDomain.dkim_key_ref` are **OpenBao
path references** — the `netbox-services` `credential_ref` convention. NetBox holds the structure
(which mailbox exists under which domain with which quota, which alias forwards where, which relay
authenticates how); OpenBao holds the secret value, resolved at apply time by the provider. State
and change logs therefore never carry a plaintext credential or private key.

## 4. Consumer note (how the provider reads this)

- **`tofu-stalwart` (in-house provider)** reads `MailDomain` + `Mailbox` + `MailAlias` + `MailRelay`
  as the SoT for the mail server's configuration: provision each authoritative domain (with its DKIM
  selector, key fetched from `dkim_key_ref`), create the mailboxes (password fetched from
  `credential_ref`), install the virtual-alias maps from the `destinations` arrays, and wire outbound
  routing through the relays (auth credential fetched from `credential_ref`).
- The password / key each step needs is fetched from OpenBao at the `*_ref` path, never from NetBox.

## 5. Verification owed (cannot run offline — no NetBox env in the build host)

The full NetBox Django test run and `makemigrations netbox_email --check --dry-run` require a live
NetBox and are **owed**, not yet run here. `python -m py_compile` passes on every module. Re-confirm
against the pinned NetBox 4.6:

- the `MailDomain` / `MailRelay` FK target serializes (`netbox_services.serviceinstance`) and the
  migration `dependencies` resolve (note: `virtualization` first-node is `0001_virtualization`, not
  `0001_initial` — NetBox squashes it);
- the `ServiceInstanceSerializer` import path (`netbox_services.api.serializers`) is stable;
- the `ArrayField` `destinations` column round-trips through the REST serializer;
- run `python /opt/netbox/app/netbox/manage.py test netbox_email --keepdb -v2` green.

Open deep-work items are tracked in `todo.json` (live migration verification, deploy + backfill, the
seeder + `tofu-stalwart` read path).
