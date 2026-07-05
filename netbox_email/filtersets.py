# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from .choices import MailboxTypeChoices, MailDomainTypeChoices, RelayAuthChoices
from .models import MailAlias, Mailbox, MailDomain, MailRelay

# Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields, so
# `?domain_id=` would be silently ignored. NetBox convention is `<fk>_id` (by PK) + `<fk>` (name).


class _DomainFilterMixin(NetBoxModelFilterSet):
    domain_id = django_filters.ModelMultipleChoiceFilter(
        field_name="domain", queryset=MailDomain.objects.all(), label="Domain (ID)"
    )
    domain = django_filters.ModelMultipleChoiceFilter(
        field_name="domain__name", to_field_name="name", queryset=MailDomain.objects.all(),
        label="Domain (name)",
    )

    class Meta:
        abstract = True


class MailDomainFilterSet(NetBoxModelFilterSet):
    domain_type = django_filters.MultipleChoiceFilter(choices=MailDomainTypeChoices)

    class Meta:
        model = MailDomain
        fields = ["id", "name", "is_catchall", "dkim_selector", "service_instance_id"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(dkim_selector__icontains=value))


class MailboxFilterSet(_DomainFilterMixin):
    mailbox_type = django_filters.MultipleChoiceFilter(choices=MailboxTypeChoices)

    class Meta:
        model = Mailbox
        fields = ["id", "local_part", "display_name", "quota_mb", "credential_ref", "is_active"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(local_part__icontains=value) | Q(display_name__icontains=value)
            | Q(domain__name__icontains=value)
        )


class MailAliasFilterSet(_DomainFilterMixin):
    class Meta:
        model = MailAlias
        fields = ["id", "source_local_part", "is_active"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(source_local_part__icontains=value) | Q(destinations__icontains=value)
            | Q(domain__name__icontains=value)
        )


class MailRelayFilterSet(NetBoxModelFilterSet):
    auth_type = django_filters.MultipleChoiceFilter(choices=RelayAuthChoices)

    class Meta:
        model = MailRelay
        fields = ["id", "name", "upstream_host", "upstream_port", "use_tls", "service_instance_id"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(upstream_host__icontains=value))
