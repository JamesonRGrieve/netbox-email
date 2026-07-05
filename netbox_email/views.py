# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class MailDomainView(generic.ObjectView):
    queryset = models.MailDomain.objects.all()


class MailDomainListView(generic.ObjectListView):
    queryset = models.MailDomain.objects.all()
    table = tables.MailDomainTable
    filterset = filtersets.MailDomainFilterSet
    filterset_form = forms.MailDomainFilterForm


class MailDomainEditView(generic.ObjectEditView):
    queryset = models.MailDomain.objects.all()
    form = forms.MailDomainForm


class MailDomainDeleteView(generic.ObjectDeleteView):
    queryset = models.MailDomain.objects.all()


class MailDomainBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MailDomain.objects.all()
    table = tables.MailDomainTable


class MailboxView(generic.ObjectView):
    queryset = models.Mailbox.objects.all()


class MailboxListView(generic.ObjectListView):
    queryset = models.Mailbox.objects.all()
    table = tables.MailboxTable
    filterset = filtersets.MailboxFilterSet
    filterset_form = forms.MailboxFilterForm


class MailboxEditView(generic.ObjectEditView):
    queryset = models.Mailbox.objects.all()
    form = forms.MailboxForm


class MailboxDeleteView(generic.ObjectDeleteView):
    queryset = models.Mailbox.objects.all()


class MailboxBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Mailbox.objects.all()
    table = tables.MailboxTable


class MailAliasView(generic.ObjectView):
    queryset = models.MailAlias.objects.all()


class MailAliasListView(generic.ObjectListView):
    queryset = models.MailAlias.objects.all()
    table = tables.MailAliasTable
    filterset = filtersets.MailAliasFilterSet
    filterset_form = forms.MailAliasFilterForm


class MailAliasEditView(generic.ObjectEditView):
    queryset = models.MailAlias.objects.all()
    form = forms.MailAliasForm


class MailAliasDeleteView(generic.ObjectDeleteView):
    queryset = models.MailAlias.objects.all()


class MailAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MailAlias.objects.all()
    table = tables.MailAliasTable


class MailRelayView(generic.ObjectView):
    queryset = models.MailRelay.objects.all()


class MailRelayListView(generic.ObjectListView):
    queryset = models.MailRelay.objects.all()
    table = tables.MailRelayTable
    filterset = filtersets.MailRelayFilterSet
    filterset_form = forms.MailRelayFilterForm


class MailRelayEditView(generic.ObjectEditView):
    queryset = models.MailRelay.objects.all()
    form = forms.MailRelayForm


class MailRelayDeleteView(generic.ObjectDeleteView):
    queryset = models.MailRelay.objects.all()


class MailRelayBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MailRelay.objects.all()
    table = tables.MailRelayTable
