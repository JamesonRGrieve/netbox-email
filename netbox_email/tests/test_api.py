# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (no GraphQL type shipped yet). Mailbox / MailAlias rows target a
shared domain; unique constraints ((local_part, domain) / (source_local_part, domain)) keep the
create rows distinct.
"""
from utilities.testing import APIViewTestCases
from netbox_email.models import MailAlias, Mailbox, MailDomain, MailRelay


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


class MailDomainAPITest(_CRUD):
    model = MailDomain
    brief_fields = ["display", "domain_type", "id", "name", "url"]
    bulk_update_data = {"is_catchall": True}

    @classmethod
    def setUpTestData(cls):
        MailDomain.objects.bulk_create([
            MailDomain(name="exist-a.example"),
            MailDomain(name="exist-b.example", domain_type="relay"),
            MailDomain(name="exist-c.example", domain_type="alias"),
        ])
        cls.create_data = [
            {"name": "srv-a.example", "domain_type": "local"},
            {"name": "srv-b.example", "domain_type": "relay", "is_catchall": True},
            {"name": "srv-c.example", "domain_type": "alias", "dkim_selector": "s1", "dkim_key_ref": "mail/dkim/srv-c"},
        ]


class MailboxAPITest(_CRUD):
    model = Mailbox
    brief_fields = ["display", "domain", "id", "local_part", "url"]
    bulk_update_data = {"is_active": False}

    @classmethod
    def setUpTestData(cls):
        d = MailDomain.objects.create(name="box.example")
        Mailbox.objects.bulk_create([
            Mailbox(local_part="a", domain=d),
            Mailbox(local_part="b", domain=d),
            Mailbox(local_part="c", domain=d),
        ])
        cls.create_data = [
            {"local_part": "k1", "domain": d.pk, "mailbox_type": "individual", "credential_ref": "mail/box/k1"},
            {"local_part": "k2", "domain": d.pk, "mailbox_type": "shared", "quota_mb": 2048, "display_name": "Shared K2"},
            {"local_part": "k3", "domain": d.pk, "mailbox_type": "group"},
        ]


class MailAliasAPITest(_CRUD):
    model = MailAlias
    brief_fields = ["display", "domain", "id", "source_local_part", "url"]
    bulk_update_data = {"is_active": False}

    @classmethod
    def setUpTestData(cls):
        d = MailDomain.objects.create(name="alias.example")
        MailAlias.objects.bulk_create([
            MailAlias(source_local_part="a", domain=d, destinations=["x@alias.example"]),
            MailAlias(source_local_part="b", domain=d, destinations=["y@alias.example"]),
            MailAlias(source_local_part="c", domain=d, destinations=["z@alias.example"]),
        ])
        cls.create_data = [
            {"source_local_part": "k1", "domain": d.pk, "destinations": ["one@alias.example"]},
            {"source_local_part": "k2", "domain": d.pk, "destinations": ["a@r.example", "b@r.example"]},
            {"source_local_part": "k3", "domain": d.pk, "destinations": []},
        ]


class MailRelayAPITest(_CRUD):
    model = MailRelay
    brief_fields = ["display", "id", "name", "upstream_host", "url"]
    bulk_update_data = {"use_tls": False}

    @classmethod
    def setUpTestData(cls):
        MailRelay.objects.bulk_create([
            MailRelay(name="rel-a", upstream_host="a.example"),
            MailRelay(name="rel-b", upstream_host="b.example", auth_type="login"),
            MailRelay(name="rel-c", upstream_host="c.example", use_tls=False),
        ])
        cls.create_data = [
            {"name": "k1", "upstream_host": "smtp1.example", "upstream_port": 587, "auth_type": "plain"},
            {"name": "k2", "upstream_host": "smtp2.example", "auth_type": "cram_md5", "credential_ref": "mail/relay/k2"},
            {"name": "k3", "upstream_host": "smtp3.example", "auth_type": "none", "use_tls": False},
        ]
