# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import MailAlias, Mailbox, MailDomain, MailRelay


class MailDomainTable(NetBoxTable):
    name = tables.Column(linkify=True)
    domain_type = columns.ChoiceFieldColumn()
    service_instance = tables.Column(linkify=True)
    is_catchall = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_email:maildomain_list")

    class Meta(NetBoxTable.Meta):
        model = MailDomain
        fields = ("pk", "id", "name", "domain_type", "service_instance", "is_catchall",
                  "dkim_selector", "tags", "created", "last_updated")
        default_columns = ("name", "domain_type", "service_instance", "is_catchall")


class MailboxTable(NetBoxTable):
    local_part = tables.Column(linkify=True)
    domain = tables.Column(linkify=True)
    mailbox_type = columns.ChoiceFieldColumn()
    is_active = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_email:mailbox_list")

    class Meta(NetBoxTable.Meta):
        model = Mailbox
        fields = ("pk", "id", "local_part", "domain", "mailbox_type", "display_name", "quota_mb",
                  "credential_ref", "is_active", "tags", "created", "last_updated")
        default_columns = ("local_part", "domain", "mailbox_type", "display_name", "is_active")


class MailAliasTable(NetBoxTable):
    source_local_part = tables.Column(linkify=True)
    domain = tables.Column(linkify=True)
    is_active = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_email:mailalias_list")

    class Meta(NetBoxTable.Meta):
        model = MailAlias
        fields = ("pk", "id", "source_local_part", "domain", "destinations", "is_active",
                  "tags", "created", "last_updated")
        default_columns = ("source_local_part", "domain", "destinations", "is_active")


class MailRelayTable(NetBoxTable):
    name = tables.Column(linkify=True)
    auth_type = columns.ChoiceFieldColumn()
    service_instance = tables.Column(linkify=True)
    use_tls = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_email:mailrelay_list")

    class Meta(NetBoxTable.Meta):
        model = MailRelay
        fields = ("pk", "id", "name", "upstream_host", "upstream_port", "auth_type", "use_tls",
                  "service_instance", "tags", "created", "last_updated")
        default_columns = ("name", "upstream_host", "upstream_port", "auth_type", "use_tls")
