# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_email --check --dry-run   (on a dev/ephemeral NetBox)
# Adds MailRelay.sender_domains — the sender domains whose outbound mail leaves through the relay.
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_email", "0003_mailbox_shared_with"),
    ]

    operations = [
        migrations.AddField(
            model_name="mailrelay",
            name="sender_domains",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=253),
                blank=True,
                default=list,
                help_text=(
                    "Sender domains whose outbound mail to non-local recipients leaves through this relay (e.g. a "
                    "smarthost account the domain is verified on). A domain may be claimed by at most one relay."
                ),
                size=None,
            ),
        ),
    ]
