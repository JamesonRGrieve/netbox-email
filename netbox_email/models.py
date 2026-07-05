# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native email-infrastructure source-of-truth models. ``MailDomain`` is the anchor: a domain the
mail server is authoritative for, optionally linked to the ``netbox_services.ServiceInstance`` that
serves it. Mailboxes and aliases hang off a domain; a ``MailRelay`` is a standalone
smarthost/forwarding proxy outbound mail is routed through.

FKs to sibling models use STRING labels ("netbox_services.ServiceInstance") — never import those
into this module.

SECRET POLICY: a mailbox password, a relay auth secret, and a DKIM private key are NEVER field
values here. ``Mailbox.credential_ref`` / ``MailRelay.credential_ref`` / ``MailDomain.dkim_key_ref``
are OpenBao PATH references (the netbox-services convention); the secret value stays in OpenBao.
"""
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import MailboxTypeChoices, MailDomainTypeChoices, RelayAuthChoices

DEFAULT_SUBMISSION_PORT = 587


class MailDomain(NetBoxModel):
    """A mail domain the server is authoritative for. ``domain_type`` selects how the server treats
    it (hosts mailboxes / relays onward / whole-domain alias). ``is_catchall`` routes otherwise
    unmatched local parts to a catch-all. ``dkim_key_ref`` is an OpenBao PATH to the DKIM private
    key — never the key material."""

    name = models.CharField(max_length=255, unique=True, help_text="The mail domain (e.g. example.com).")
    domain_type = models.CharField(
        max_length=16, choices=MailDomainTypeChoices, default=MailDomainTypeChoices.LOCAL
    )
    service_instance = models.ForeignKey(
        "netbox_services.ServiceInstance", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mail_domains",
        help_text="The netbox-services mail server (Stalwart, etc.) serving this domain.",
    )
    is_catchall = models.BooleanField(
        default=False, help_text="Route unmatched local parts to a catch-all mailbox."
    )
    dkim_selector = models.CharField(
        max_length=63, blank=True, help_text="DKIM selector (the s= tag, e.g. 'default')."
    )
    dkim_key_ref = models.CharField(
        max_length=255, blank=True, help_text="OpenBao path for the DKIM private key — NEVER the key."
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Mail Domain"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_email:maildomain", args=[self.pk])

    def get_domain_type_color(self):
        return MailDomainTypeChoices.colors.get(self.domain_type)


class Mailbox(NetBoxModel):
    """A mailbox under a domain. ``local_part`` is the part before the ``@``; the full address is
    ``local_part@domain``. ``credential_ref`` is an OpenBao PATH — never the password. ``quota_mb``
    NULL = no quota (server default)."""

    local_part = models.CharField(max_length=255, help_text="The part before the '@'.")
    domain = models.ForeignKey(MailDomain, on_delete=models.CASCADE, related_name="mailboxes")
    mailbox_type = models.CharField(
        max_length=16, choices=MailboxTypeChoices, default=MailboxTypeChoices.INDIVIDUAL
    )
    display_name = models.CharField(max_length=255, blank=True)
    quota_mb = models.PositiveIntegerField(null=True, blank=True, help_text="Quota in MiB (NULL = server default).")
    credential_ref = models.CharField(
        max_length=255, blank=True, help_text="OpenBao path for the password — NEVER the secret."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["domain", "local_part"]
        verbose_name = "Mailbox"
        verbose_name_plural = "Mailboxes"
        constraints = [
            models.UniqueConstraint(
                fields=["local_part", "domain"], name="netbox_email_mailbox_unique_local_part_domain"
            ),
        ]

    def __str__(self):
        return f"{self.local_part}@{self.domain}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_email:mailbox", args=[self.pk])

    def get_mailbox_type_color(self):
        return MailboxTypeChoices.colors.get(self.mailbox_type)


class MailAlias(NetBoxModel):
    """A forwarding alias: mail to ``source_local_part@domain`` is fanned out to every address in
    ``destinations``. The destinations are arbitrary addresses (local or remote), stored as a Postgres
    array — the mail server's virtual-alias map."""

    source_local_part = models.CharField(max_length=255, help_text="The alias local part (before the '@').")
    domain = models.ForeignKey(MailDomain, on_delete=models.CASCADE, related_name="aliases")
    destinations = ArrayField(
        models.CharField(max_length=320), default=list,
        help_text="Destination addresses mail is forwarded to.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["domain", "source_local_part"]
        verbose_name = "Mail Alias"
        verbose_name_plural = "Mail Aliases"
        constraints = [
            models.UniqueConstraint(
                fields=["source_local_part", "domain"],
                name="netbox_email_mailalias_unique_source_domain",
            ),
        ]

    def __str__(self):
        return f"{self.source_local_part}@{self.domain}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_email:mailalias", args=[self.pk])


class MailRelay(NetBoxModel):
    """A forwarding relay / smarthost outbound mail is routed through. ``auth_type`` selects the
    SMTP AUTH mechanism; ``credential_ref`` is an OpenBao PATH to the relay credential (never the
    secret). Optionally linked to the ``netbox_services.ServiceInstance`` that runs the relay."""

    name = models.CharField(max_length=100, unique=True)
    upstream_host = models.CharField(max_length=255, help_text="Upstream smarthost hostname/IP.")
    upstream_port = models.PositiveIntegerField(default=DEFAULT_SUBMISSION_PORT)
    auth_type = models.CharField(
        max_length=16, choices=RelayAuthChoices, default=RelayAuthChoices.PLAIN
    )
    credential_ref = models.CharField(
        max_length=255, blank=True, help_text="OpenBao path for the relay credential — NEVER the secret."
    )
    use_tls = models.BooleanField(default=True)
    service_instance = models.ForeignKey(
        "netbox_services.ServiceInstance", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="mail_relays",
        help_text="The netbox-services instance running this relay (composition link).",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Mail Relay"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_email:mailrelay", args=[self.pk])

    def get_auth_type_color(self):
        return RelayAuthChoices.colors.get(self.auth_type)
