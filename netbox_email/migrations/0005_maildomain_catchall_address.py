# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_email --check --dry-run   (on a dev/ephemeral NetBox)
# Adds MailDomain.catchall_address — where a catch-all domain's unmatched mail goes.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_email", "0004_mailrelay_sender_domains"),
    ]

    operations = [
        migrations.AddField(
            model_name="maildomain",
            name="catchall_address",
            field=models.CharField(
                blank=True,
                help_text="The address that receives mail for unmatched local parts (required when is_catchall).",
                max_length=254,
            ),
        ),
    ]
