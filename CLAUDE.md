# netbox-email — Agent Operating Guide

Adapted from the sibling `../netbox-database` / `../netbox-services` plugins (same engineering + test
discipline), re-targeted to the **email-infrastructure layer**.

`netbox-email` is an **AGPL-3.0** NetBox 4.6 plugin: the **native source of truth for email
infrastructure** — which mail domains a server is authoritative for (and their DKIM signing
identity), the mailboxes under each domain, the aliases / forwarding maps that fan an address out to
other destinations, and the forwarding relays / smarthosts outbound mail is routed through. It is
what the `tofu-stalwart` provider reads. It does **not** own message content or delivery state — the
server owns that at runtime. See **DESIGN.md** for the full data model, the compose boundary, and
verification owed.

**It composes `netbox-services`, it does not re-model it (the netbox-ai pattern):** the mail server
serving a domain is (optionally) a `netbox_services.ServiceInstance` — `MailDomain` and `MailRelay`
**FK** it, so `required_plugins = ["netbox_services"]` and the migration depends on
`netbox_services.0001_initial`. Deployment metadata (host, ports, health) stays on the
`ServiceInstance` and cross-service HA pairing stays in `netbox_services.HAMirror` — both are
**reused, never duplicated**.

**Secret policy (load-bearing):** a mailbox password, a relay auth secret, and a DKIM private key are
**never** field values here. `Mailbox.credential_ref` / `MailRelay.credential_ref` /
`MailDomain.dkim_key_ref` are **OpenBao path** references (the netbox-services convention). NetBox
holds the structure; OpenBao holds the secret.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter.
- Any time you modify a source file, ensure its accompanying test under `netbox_email/tests/`
  contains **comprehensive tests for the change WITHOUT MOCKS**, so `manage.py test netbox_email`
  discovers them, and update any `.md` in the same directory that references it.
- Write concise code (avoid obvious comments; one-liners where possible).
- Model the alias fan-out as a first-class `ArrayField`, never a serialized/JSON blob.
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Store a mailbox password, relay secret, or DKIM private key (any secret value) in a model field.
  Only OpenBao path references.
- Model message content / delivery queues — the mail server owns those at runtime.
- Duplicate `netbox_services.ServiceInstance` deployment metadata or `HAMirror` — FK / reference them.
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test; keep a broken path as a fallback; or re-implement a function in a second
  location to bypass the original. No bandaid fixes.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests run
  against a **real test database** with real `MailDomain` / `netbox_services.ServiceInstance` rows.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — never `import datetime`.
- Package-relative imports inside `netbox_email` (`from .models import MailDomain`); core/sibling use
  the real path (`from netbox_services.api.serializers import ServiceInstanceSerializer`).
- FKs to sibling models in `models.py` use **string labels** (`"netbox_services.ServiceInstance"`) —
  never import them there.
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, GraphQL — free).

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_email`, `base_url='email'`, min/max 4.6, `required_plugins=["netbox_services"]` |
| `choices.py` | `ChoiceSet`s: `MailDomainTypeChoices`, `MailboxTypeChoices`, `RelayAuthChoices` |
| `models.py` | the 4 models below |
| `migrations/0001_initial.py` | hand-authored (NetBox disables makemigrations in prod); verify with `makemigrations --check --dry-run`; deps: dcim, extras, virtualization (`0001_virtualization`!), netbox_services |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST (`NetBoxModelViewSet`, `NetBoxRouter`) — the contract the provider + seeder read; nests the netbox_services serializer |
| `filtersets.py` | `NetBoxModelFilterSet` per model (explicit `<fk>_id` + `search()`) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py` | UI (generic NetBox views; `_routes()` helper; PluginMenu groups Domains / Mailboxes / Aliases / Relays) |
| `graphql/__init__.py` | placeholder (auto GraphQL via `NetBoxModel`) |

### Model — domains + mailboxes + aliases + relays
- **MailDomain**: `name`(unique)·`domain_type`·`is_catchall`·`dkim_selector`·`dkim_key_ref`(OpenBao
  path); optional `service_instance`("netbox_services.ServiceInstance", SET_NULL).
- **Mailbox** (FK domain): `local_part`·`mailbox_type`·`display_name`·`quota_mb`·`credential_ref`
  (OpenBao path)·`is_active`; unique `(local_part, domain)`; `__str__ = local_part@domain`.
- **MailAlias** (FK domain): `source_local_part`·`destinations`(ArrayField)·`is_active`; unique
  `(source_local_part, domain)`.
- **MailRelay**: `name`(unique)·`upstream_host`·`upstream_port`(587)·`auth_type`·`credential_ref`
  (OpenBao path)·`use_tls`; optional `service_instance`("netbox_services.ServiceInstance", SET_NULL).

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_email/tests/` (`test_models.py`, `test_api.py`, `test_filtersets.py`).
  Build real domains via a `make_domain`/inline helper; API `create_data` rows share a domain and
  stay distinct under the uniqueness constraints.
- `test_models` covers `__str__`, choice colors, every uniqueness constraint, the array default, and
  cascade-on-domain-delete; `test_api` runs the CRUD mixins per model; `test_filtersets` covers
  FK-id scoping, choice filters, and `search()`.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_email --keepdb -v2`.
- **Verification owed (cannot run offline — no NetBox env in the build host):**
  `makemigrations netbox_email --check --dry-run` on an ephemeral NetBox, and a full test run.
  Re-confirm against the pinned NetBox 4.6: the FK-target serialization
  (`netbox_services.serviceinstance`), the migration `dependencies` (virtualization first node is
  `0001_virtualization`, not `0001_initial`), the `ArrayField` REST round-trip, and the
  `netbox_services.api.serializers.ServiceInstanceSerializer` import path. `py_compile` passes on
  every module today.
- **Never skip a failing test** — fix the root cause.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.
