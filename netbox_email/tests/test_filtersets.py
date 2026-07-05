# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): FK-id scoping, choice filters, and search()."""
from django.test import TestCase
from netbox_email.choices import MailboxTypeChoices, MailDomainTypeChoices, RelayAuthChoices
from netbox_email.filtersets import (
    MailAliasFilterSet, MailboxFilterSet, MailDomainFilterSet, MailRelayFilterSet,
)
from netbox_email.models import MailAlias, Mailbox, MailDomain, MailRelay


class MailDomainFilterSetTest(TestCase):
    queryset = MailDomain.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.d1 = MailDomain.objects.create(name="local.example", domain_type=MailDomainTypeChoices.LOCAL)
        cls.d2 = MailDomain.objects.create(name="relay.example", domain_type=MailDomainTypeChoices.RELAY)

    def test_domain_type(self):
        self.assertEqual(MailDomainFilterSet({"domain_type": ["relay"]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(MailDomainFilterSet({"q": "local.example"}, self.queryset).qs.count(), 1)


class MailboxFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = MailDomain.objects.create(name="d1.example")
        cls.d2 = MailDomain.objects.create(name="d2.example")
        Mailbox.objects.bulk_create([
            Mailbox(local_part="ada", domain=cls.d1, mailbox_type=MailboxTypeChoices.INDIVIDUAL),
            Mailbox(local_part="bob", domain=cls.d1, mailbox_type=MailboxTypeChoices.SHARED),
            Mailbox(local_part="cy", domain=cls.d2, mailbox_type=MailboxTypeChoices.GROUP),
        ])

    def test_domain_scope(self):
        self.assertEqual(MailboxFilterSet({"domain_id": [self.d1.pk]}, Mailbox.objects.all()).qs.count(), 2)

    def test_mailbox_type(self):
        self.assertEqual(MailboxFilterSet({"mailbox_type": ["shared"]}, Mailbox.objects.all()).qs.count(), 1)

    def test_search(self):
        self.assertEqual(MailboxFilterSet({"q": "cy"}, Mailbox.objects.all()).qs.count(), 1)


class MailAliasFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.d1 = MailDomain.objects.create(name="a1.example")
        cls.d2 = MailDomain.objects.create(name="a2.example")
        MailAlias.objects.bulk_create([
            MailAlias(source_local_part="team", domain=cls.d1, destinations=["ada@a1.example"]),
            MailAlias(source_local_part="sales", domain=cls.d1, destinations=["bob@a1.example"]),
            MailAlias(source_local_part="ops", domain=cls.d2, destinations=["cy@a2.example"]),
        ])

    def test_domain_scope(self):
        self.assertEqual(MailAliasFilterSet({"domain_id": [self.d1.pk]}, MailAlias.objects.all()).qs.count(), 2)

    def test_search_source(self):
        self.assertEqual(MailAliasFilterSet({"q": "ops"}, MailAlias.objects.all()).qs.count(), 1)


class MailRelayFilterSetTest(TestCase):
    queryset = MailRelay.objects.all()

    @classmethod
    def setUpTestData(cls):
        MailRelay.objects.create(name="r-plain", upstream_host="plain.example", auth_type=RelayAuthChoices.PLAIN)
        MailRelay.objects.create(name="r-cram", upstream_host="cram.example", auth_type=RelayAuthChoices.CRAM_MD5)

    def test_auth_type(self):
        self.assertEqual(MailRelayFilterSet({"auth_type": ["cram_md5"]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(MailRelayFilterSet({"q": "plain.example"}, self.queryset).qs.count(), 1)
