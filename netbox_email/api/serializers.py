# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.serializers import NetBoxModelSerializer
from netbox_services.api.serializers import ServiceInstanceSerializer
from rest_framework import serializers
from ..models import MailAlias, Mailbox, MailDomain, MailRelay


class MailDomainSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_email-api:maildomain-detail")
    service_instance = ServiceInstanceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = MailDomain
        fields = [
            "id", "url", "display", "name", "domain_type", "service_instance", "is_catchall",
            "dkim_selector", "dkim_key_ref", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "domain_type"]


class MailboxSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_email-api:mailbox-detail")
    domain = MailDomainSerializer(nested=True)

    class Meta:
        model = Mailbox
        fields = [
            "id", "url", "display", "local_part", "domain", "mailbox_type", "display_name",
            "quota_mb", "credential_ref", "send_as_addresses", "is_active", "tags", "custom_fields",
            "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "local_part", "domain"]


class MailAliasSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_email-api:mailalias-detail")
    domain = MailDomainSerializer(nested=True)

    class Meta:
        model = MailAlias
        fields = [
            "id", "url", "display", "source_local_part", "domain", "destinations", "is_active",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "source_local_part", "domain"]


class MailRelaySerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_email-api:mailrelay-detail")
    service_instance = ServiceInstanceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = MailRelay
        fields = [
            "id", "url", "display", "name", "upstream_host", "upstream_port", "auth_type",
            "credential_ref", "use_tls", "service_instance", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "upstream_host"]
