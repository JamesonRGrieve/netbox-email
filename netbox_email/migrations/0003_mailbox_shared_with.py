# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_email --check --dry-run   (on a dev/ephemeral NetBox)
# Adds Mailbox.shared_with — the mailboxes whose owners also open this mailbox in their mail client
# (mirrors send_as_addresses' ArrayField shape).
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_email", "0002_mailbox_send_as_addresses"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailbox",
            name="shared_with",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=320),
                blank=True,
                default=list,
                help_text=(
                    "Addresses of the mailboxes whose owners also open THIS mailbox in their mail client, "
                    "authenticating with this mailbox's own credential — so each receives at and sends as this "
                    "address (e.g. a second personal mailbox, or a shared mailbox for several people). Each entry "
                    "must be another mailbox defined here."
                ),
                size=None,
            ),
        ),
    ]
