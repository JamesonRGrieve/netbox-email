# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import MailAlias, Mailbox, MailDomain, MailRelay
from .serializers import (
    MailAliasSerializer, MailboxSerializer, MailDomainSerializer, MailRelaySerializer,
)


class MailDomainViewSet(NetBoxModelViewSet):
    queryset = MailDomain.objects.prefetch_related("service_instance", "tags")
    serializer_class = MailDomainSerializer
    filterset_class = filtersets.MailDomainFilterSet


class MailboxViewSet(NetBoxModelViewSet):
    queryset = Mailbox.objects.prefetch_related("domain", "tags")
    serializer_class = MailboxSerializer
    filterset_class = filtersets.MailboxFilterSet


class MailAliasViewSet(NetBoxModelViewSet):
    queryset = MailAlias.objects.prefetch_related("domain", "tags")
    serializer_class = MailAliasSerializer
    filterset_class = filtersets.MailAliasFilterSet


class MailRelayViewSet(NetBoxModelViewSet):
    queryset = MailRelay.objects.prefetch_related("service_instance", "tags")
    serializer_class = MailRelaySerializer
    filterset_class = filtersets.MailRelayFilterSet
