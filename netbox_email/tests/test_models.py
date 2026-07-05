# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, choice-color, constraints, cascades."""
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_email.choices import MailboxTypeChoices, MailDomainTypeChoices, RelayAuthChoices
from netbox_email.models import MailAlias, Mailbox, MailDomain, MailRelay


def make_domain(name="example.com", domain_type=MailDomainTypeChoices.LOCAL):
    return MailDomain.objects.create(name=name, domain_type=domain_type)


class MailDomainModelTest(TestCase):
    def test_create_str_url_and_type_color(self):
        d = make_domain()
        self.assertEqual(str(d), "example.com")
        self.assertIn("/plugins/email/domains/", d.get_absolute_url())
        self.assertEqual(d.get_domain_type_color(), "green")
        self.assertEqual(d.domain_type, MailDomainTypeChoices.LOCAL)

    def test_name_unique(self):
        make_domain("dup.example")
        with self.assertRaises(IntegrityError), transaction.atomic():
            MailDomain.objects.create(name="dup.example")

    def test_dkim_ref_is_a_path_not_a_key(self):
        d = MailDomain.objects.create(name="dkim.example", dkim_selector="default", dkim_key_ref="mail/dkim/dkim.example")
        self.assertEqual(d.dkim_key_ref, "mail/dkim/dkim.example")
        self.assertEqual(d.dkim_selector, "default")


class MailboxModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.domain = make_domain("box.example")

    def test_str_url_defaults_and_type_color(self):
        m = Mailbox.objects.create(local_part="alice", domain=self.domain, credential_ref="mail/box/alice")
        self.assertEqual(str(m), "alice@box.example")
        self.assertIn("/plugins/email/mailboxes/", m.get_absolute_url())
        self.assertEqual(m.mailbox_type, MailboxTypeChoices.INDIVIDUAL)
        self.assertTrue(m.is_active)
        self.assertIsNone(m.quota_mb)
        self.assertEqual(m.credential_ref, "mail/box/alice")  # a path, not the secret
        self.assertEqual(m.get_mailbox_type_color(), "green")

    def test_unique_local_part_per_domain(self):
        Mailbox.objects.create(local_part="bob", domain=self.domain)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Mailbox.objects.create(local_part="bob", domain=self.domain)

    def test_same_local_part_different_domain_allowed(self):
        other = make_domain("box2.example")
        Mailbox.objects.create(local_part="carol", domain=self.domain)
        Mailbox.objects.create(local_part="carol", domain=other)
        self.assertEqual(Mailbox.objects.filter(local_part="carol").count(), 2)

    def test_cascade_on_domain_delete(self):
        d = make_domain("cascade.example")
        Mailbox.objects.create(local_part="x", domain=d)
        MailAlias.objects.create(source_local_part="y", domain=d, destinations=["x@cascade.example"])
        d.delete()
        self.assertEqual(Mailbox.objects.filter(local_part="x").count(), 0)
        self.assertEqual(MailAlias.objects.filter(source_local_part="y").count(), 0)


class MailAliasModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.domain = make_domain("alias.example")

    def test_str_url_and_destinations_array(self):
        a = MailAlias.objects.create(
            source_local_part="team", domain=self.domain,
            destinations=["alice@alias.example", "bob@remote.example"],
        )
        self.assertEqual(str(a), "team@alias.example")
        self.assertIn("/plugins/email/aliases/", a.get_absolute_url())
        self.assertEqual(a.destinations, ["alice@alias.example", "bob@remote.example"])
        self.assertTrue(a.is_active)

    def test_default_destinations_is_empty_list(self):
        a = MailAlias.objects.create(source_local_part="empty", domain=self.domain)
        self.assertEqual(a.destinations, [])

    def test_unique_source_per_domain(self):
        MailAlias.objects.create(source_local_part="sales", domain=self.domain, destinations=["a@x"])
        with self.assertRaises(IntegrityError), transaction.atomic():
            MailAlias.objects.create(source_local_part="sales", domain=self.domain, destinations=["b@x"])


class MailRelayModelTest(TestCase):
    def test_str_url_defaults_and_auth_color(self):
        r = MailRelay.objects.create(name="smarthost", upstream_host="smtp.provider.example")
        self.assertEqual(str(r), "smarthost")
        self.assertIn("/plugins/email/relays/", r.get_absolute_url())
        self.assertEqual(r.upstream_port, 587)
        self.assertEqual(r.auth_type, RelayAuthChoices.PLAIN)
        self.assertTrue(r.use_tls)
        self.assertEqual(r.get_auth_type_color(), "blue")

    def test_name_unique(self):
        MailRelay.objects.create(name="dup-relay", upstream_host="a.example")
        with self.assertRaises(IntegrityError), transaction.atomic():
            MailRelay.objects.create(name="dup-relay", upstream_host="b.example")

    def test_credential_ref_is_a_path(self):
        r = MailRelay.objects.create(
            name="auth-relay", upstream_host="smtp.example", auth_type=RelayAuthChoices.CRAM_MD5,
            credential_ref="mail/relay/auth-relay",
        )
        self.assertEqual(r.credential_ref, "mail/relay/auth-relay")  # a path, not the secret
        self.assertEqual(r.get_auth_type_color(), "green")
