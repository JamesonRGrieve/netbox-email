# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_email --check --dry-run   (on a dev/ephemeral NetBox)
# Adds Mailbox.send_as_addresses — the account's owned send-as identity addresses
# (mirrors MailAlias.destinations' ArrayField shape).
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_email", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailbox",
            name="send_as_addresses",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=320),
                blank=True,
                default=list,
                help_text=(
                    "Additional addresses this account OWNS as send-as identities — it may both receive "
                    "at and send from each with the domain's DKIM authority (the mail server's account-alias "
                    "set, e.g. Stalwart x:Account aliases). Full addresses, distinct from a forwarding MailAlias."
                ),
                size=None,
            ),
        ),
    ]
