# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views


def _routes(slug, name, model, list_view, edit_view, detail_view, delete_view, bulk_delete_view):
    return [
        path(f"{slug}/", list_view.as_view(), name=f"{name}_list"),
        path(f"{slug}/add/", edit_view.as_view(), name=f"{name}_add"),
        path(f"{slug}/delete/", bulk_delete_view.as_view(), name=f"{name}_bulk_delete"),
        path(f"{slug}/<int:pk>/", detail_view.as_view(), name=name),
        path(f"{slug}/<int:pk>/edit/", edit_view.as_view(), name=f"{name}_edit"),
        path(f"{slug}/<int:pk>/delete/", delete_view.as_view(), name=f"{name}_delete"),
        path(f"{slug}/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name=f"{name}_changelog", kwargs={"model": model}),
        path(f"{slug}/<int:pk>/journal/", ObjectJournalView.as_view(), name=f"{name}_journal", kwargs={"model": model}),
    ]


urlpatterns = [
    *_routes("domains", "maildomain", models.MailDomain,
             views.MailDomainListView, views.MailDomainEditView, views.MailDomainView,
             views.MailDomainDeleteView, views.MailDomainBulkDeleteView),
    *_routes("mailboxes", "mailbox", models.Mailbox,
             views.MailboxListView, views.MailboxEditView, views.MailboxView,
             views.MailboxDeleteView, views.MailboxBulkDeleteView),
    *_routes("aliases", "mailalias", models.MailAlias,
             views.MailAliasListView, views.MailAliasEditView, views.MailAliasView,
             views.MailAliasDeleteView, views.MailAliasBulkDeleteView),
    *_routes("relays", "mailrelay", models.MailRelay,
             views.MailRelayListView, views.MailRelayEditView, views.MailRelayView,
             views.MailRelayDeleteView, views.MailRelayBulkDeleteView),
]
