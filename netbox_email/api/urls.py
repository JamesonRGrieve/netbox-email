# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_email"

router = NetBoxRouter()
router.register("domains", views.MailDomainViewSet)
router.register("mailboxes", views.MailboxViewSet)
router.register("aliases", views.MailAliasViewSet)
router.register("relays", views.MailRelayViewSet)

urlpatterns = router.urls
