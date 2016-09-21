# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import now


def default_scheduled(apps, schema_editor):
    EntryModel = apps.get_model('emails', 'EmailEntry')
    for entry in EntryModel.objects.all():
        default = entry.datetime_sent
        if default is None:
            default = now()
        entry.datetime_scheduled = default
        entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0007_emailkind_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailentry',
            name='datetime_scheduled',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),

        migrations.RunPython(default_scheduled, reverse_code=migrations.RunPython.noop),

        migrations.AlterField(
            model_name='emailentry',
            name='datetime_scheduled',
            field=models.DateTimeField(auto_now_add=True, null=False),
        ),
    ]
