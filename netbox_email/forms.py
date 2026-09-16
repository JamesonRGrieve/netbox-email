# SPDX-License-Identifier: AGPL-3.0-or-later
from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from .choices import MailboxTypeChoices, MailDomainTypeChoices, RelayAuthChoices
from .models import MailAlias, Mailbox, MailDomain, MailRelay


class MailDomainForm(NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "domain_type", "service_instance", "is_catchall", name="Domain"),
        FieldSet("dkim_selector", "dkim_key_ref", name="DKIM"),
    )

    class Meta:
        model = MailDomain
        fields = ["name", "domain_type", "service_instance", "is_catchall", "dkim_selector",
                  "dkim_key_ref", "tags"]


class MailboxForm(NetBoxModelForm):
    domain = DynamicModelChoiceField(queryset=MailDomain.objects.all())
    send_as_addresses = SimpleArrayField(
        forms.CharField(max_length=320), required=False,
        help_text="Comma-separated addresses this account owns as send-as identities.",
    )

    fieldsets = (
        FieldSet("local_part", "domain", "mailbox_type", "display_name", name="Mailbox"),
        FieldSet("quota_mb", "credential_ref", "is_active", name="Quota / auth"),
        FieldSet("send_as_addresses", name="Send-as identities"),
    )

    class Meta:
        model = Mailbox
        fields = ["local_part", "domain", "mailbox_type", "display_name", "quota_mb",
                  "credential_ref", "send_as_addresses", "is_active", "tags"]


class MailAliasForm(NetBoxModelForm):
    domain = DynamicModelChoiceField(queryset=MailDomain.objects.all())
    destinations = SimpleArrayField(
        forms.CharField(max_length=320), required=False,
        help_text="Comma-separated destination addresses.",
    )

    fieldsets = (FieldSet("source_local_part", "domain", "destinations", "is_active", name="Alias"),)

    class Meta:
        model = MailAlias
        fields = ["source_local_part", "domain", "destinations", "is_active", "tags"]


class MailRelayForm(NetBoxModelForm):
    fieldsets = (
        FieldSet("name", "upstream_host", "upstream_port", "use_tls", name="Relay"),
        FieldSet("auth_type", "credential_ref", "service_instance", name="Auth"),
    )

    class Meta:
        model = MailRelay
        fields = ["name", "upstream_host", "upstream_port", "auth_type", "credential_ref",
                  "use_tls", "service_instance", "tags"]


class MailDomainFilterForm(NetBoxModelFilterSetForm):
    model = MailDomain
    domain_type = forms.MultipleChoiceField(choices=MailDomainTypeChoices, required=False)
    is_catchall = forms.NullBooleanField(required=False)
    tag = TagFilterField(MailDomain)


class MailboxFilterForm(NetBoxModelFilterSetForm):
    model = Mailbox
    domain_id = DynamicModelMultipleChoiceField(queryset=MailDomain.objects.all(), required=False, label="Domain")
    mailbox_type = forms.MultipleChoiceField(choices=MailboxTypeChoices, required=False)
    is_active = forms.NullBooleanField(required=False)
    tag = TagFilterField(Mailbox)


class MailAliasFilterForm(NetBoxModelFilterSetForm):
    model = MailAlias
    domain_id = DynamicModelMultipleChoiceField(queryset=MailDomain.objects.all(), required=False, label="Domain")
    is_active = forms.NullBooleanField(required=False)
    tag = TagFilterField(MailAlias)


class MailRelayFilterForm(NetBoxModelFilterSetForm):
    model = MailRelay
    auth_type = forms.MultipleChoiceField(choices=RelayAuthChoices, required=False)
    use_tls = forms.NullBooleanField(required=False)
    tag = TagFilterField(MailRelay)
