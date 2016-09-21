# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailentry',
            name='datetime_sent',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='emailentry',
            name='deleted',
            field=models.BooleanField(verbose_name='Marked for deletion', default=False),
        ),
    ]
