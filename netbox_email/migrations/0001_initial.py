# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_email --check --dry-run   (on a dev/ephemeral NetBox)
# Re-confirm against the pinned NetBox 4.6: the MailDomain/MailRelay FK target
# (netbox_services.serviceinstance) and the ArrayField destinations column.
import django.contrib.postgres.fields
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

_BASE = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
    ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
    ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
    ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
]
_TAGS = ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"))


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("virtualization", "0001_virtualization"),
        # MailDomain/MailRelay.service_instance FK netbox_services.ServiceInstance — table must exist.
        ("netbox_services", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="MailDomain",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=255, unique=True)),
                ("domain_type", models.CharField(default="local", max_length=16)),
                ("is_catchall", models.BooleanField(default=False)),
                ("dkim_selector", models.CharField(blank=True, max_length=63)),
                ("dkim_key_ref", models.CharField(blank=True, max_length=255)),
                ("service_instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="mail_domains", to="netbox_services.serviceinstance")),
                _TAGS,
            ],
            options={"verbose_name": "Mail Domain", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="MailRelay",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("upstream_host", models.CharField(max_length=255)),
                ("upstream_port", models.PositiveIntegerField(default=587)),
                ("auth_type", models.CharField(default="plain", max_length=16)),
                ("credential_ref", models.CharField(blank=True, max_length=255)),
                ("use_tls", models.BooleanField(default=True)),
                ("service_instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="mail_relays", to="netbox_services.serviceinstance")),
                _TAGS,
            ],
            options={"verbose_name": "Mail Relay", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Mailbox",
            fields=[
                *_BASE,
                ("local_part", models.CharField(max_length=255)),
                ("mailbox_type", models.CharField(default="individual", max_length=16)),
                ("display_name", models.CharField(blank=True, max_length=255)),
                ("quota_mb", models.PositiveIntegerField(blank=True, null=True)),
                ("credential_ref", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("domain", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailboxes", to="netbox_email.maildomain")),
                _TAGS,
            ],
            options={
                "verbose_name": "Mailbox",
                "verbose_name_plural": "Mailboxes",
                "ordering": ["domain", "local_part"],
                "constraints": [models.UniqueConstraint(fields=("local_part", "domain"), name="netbox_email_mailbox_unique_local_part_domain")],
            },
        ),
        migrations.CreateModel(
            name="MailAlias",
            fields=[
                *_BASE,
                ("source_local_part", models.CharField(max_length=255)),
                ("destinations", django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=320), default=list, size=None)),
                ("is_active", models.BooleanField(default=True)),
                ("domain", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="aliases", to="netbox_email.maildomain")),
                _TAGS,
            ],
            options={
                "verbose_name": "Mail Alias",
                "verbose_name_plural": "Mail Aliases",
                "ordering": ["domain", "source_local_part"],
                "constraints": [models.UniqueConstraint(fields=("source_local_part", "domain"), name="netbox_email_mailalias_unique_source_domain")],
            },
        ),
    ]
